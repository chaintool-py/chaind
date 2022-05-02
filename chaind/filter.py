# standard imports
import logging
import time

# external imports
from chainlib.status import Status as TxStatus
from chainsyncer.filter import SyncFilter
from chainqueue.error import NotLocalTxError
from chaind.adapters.fs import ChaindFsAdapter
from shep.error import StateLockedKey

# local imports
from .error import (
        QueueLockError,
        BackendError,
        )
from chaind.lock import StoreLock

logg = logging.getLogger(__name__)


class StateFilter(SyncFilter):

    def __init__(self, chain_spec, adapter_path, tx_adapter, throttler=None):
        self.chain_spec = chain_spec
        self.adapter_path = adapter_path
        self.tx_adapter = tx_adapter
        self.throttler = throttler


    def filter(self, conn, block, tx, session=None):
        cache_tx = None
        store_lock = StoreLock()
        queue_adapter = None
        while True:
            try:
                queue_adapter = ChaindFsAdapter(
                    self.chain_spec,
                    self.adapter_path,
                    self.tx_adapter,
                    None,
                    )
            except BackendError as e:
                logg.error('adapter instantiation failed: {}, one more try'.format(e))
                store_lock.again()
                continue

            store_lock.reset()

            try:
                cache_tx = queue_adapter.get(tx.hash)
                break
            except NotLocalTxError:
                logg.debug('skipping not local transaction {}'.format(tx.hash))
                return False
            except BackendError as e:
                logg.error('adapter instantiation failed: {}, one more try'.format(e))
                queue_adapter = None
                store_lock.again()
                continue

        if cache_tx == None:
            raise NotLocalTxError(tx.hash)

        store_lock = StoreLock()
        queue_lock = StoreLock(error=QueueLockError)
        while True:
            try:
                if tx.status == TxStatus.SUCCESS:
                    queue_adapter.succeed(block, tx)
                else:
                    queue_adapter.fail(block, tx)
                break
            except QueueLockError as e:
                logg.debug('queue item {} is blocked, will retry: {}'.format(tx.hash, e))
                queue_lock.again()
            except FileNotFoundError as e:
                logg.debug('queue item {} not found, possible race condition, will retry: {}'.format(tx.hash, e))
                store_lock.again()
                continue
            except NotLocalTxError as e:
                logg.debug('queue item {} not found, possible race condition, will retry: {}'.format(tx.hash, e))
                store_lock.again()
                continue
            except StateLockedKey as e:
                logg.debug('queue item {} not found, possible race condition, will retry: {}'.format(tx.hash, e))
                store_lock.again()
                continue

        logg.info('filter registered {} for {} in {}'.format(tx.status.name, tx.hash, block))

        if self.throttler != None:
            self.throttler.dec(tx.hash)

        return False
