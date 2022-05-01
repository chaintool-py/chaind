# standard imports
import logging
import time

# external imports
from chainlib.status import Status as TxStatus
from chainsyncer.filter import SyncFilter
from chainqueue.error import NotLocalTxError
from chaind.adapters.fs import ChaindFsAdapter

# local imports
from .error import (
        QueueLockError,
        BackendIntegrityError,
        )

logg = logging.getLogger(__name__)


class StateFilter(SyncFilter):

    delay_limit = 3.0
    race_delay = 0.1

    def __init__(self, chain_spec, adapter_path, tx_adapter, throttler=None):
        self.chain_spec = chain_spec
        self.adapter_path = adapter_path
        self.tx_adapter = tx_adapter
        self.throttler = throttler


    def filter(self, conn, block, tx, session=None):
        cache_tx = None
        for i in range(3):
            queue_adapter = None
            try:
                queue_adapter = ChaindFsAdapter(
                    self.chain_spec,
                    self.adapter_path,
                    self.tx_adapter,
                    None,
                    )
            except BackendIntegrityError as e:
                logg.error('adapter instantiation failed: {}, one more try'.format(e))
                time.sleep(self.race_delay)
                continue

            try:
                cache_tx = queue_adapter.get(tx.hash)
            except NotLocalTxError:
                logg.debug('skipping not local transaction {}'.format(tx.hash))
                return False
            except BackendIntegrityError as e:
                logg.error('adapter instantiation failed: {}, one more try'.format(e))
                time.sleep(self.race_delay)
                continue

            break

        if cache_tx == None:
            raise NotLocalTxError(tx.hash)

        delay = 0.01
        race_attempts = 0
        err = None
        while True:
            if delay > self.delay_limit:
                raise QueueLockError('The queue lock for tx {} seems to be stuck. Human meddling needed.'.format(tx.hash))
            elif race_attempts >= 3:
                break
            try:
                if tx.status == TxStatus.SUCCESS:
                    queue_adapter.succeed(block, tx)
                else:
                    queue_adapter.fail(block, tx)
                err = None
                break
            except QueueLockError as e:
                logg.debug('queue item {} is blocked, will retry: {}'.format(tx.hash, e))
                time.sleep(delay)
                delay *= 2
                race_attempts = 0
                err = None
            except FileNotFoundError as e:
                err = e
                logg.debug('queue item {} not found, possible race condition, will retry: {}'.format(tx.hash, e))
                race_attempts += 1
                time.sleep(self.race_delay)
                continue
            except NotLocalTxError as e:
                err = e
                logg.debug('queue item {} not found, possible race condition, will retry: {}'.format(tx.hash, e))
                race_attempts += 1
                time.sleep(self.race_delay)
                continue

        if err != None:
            raise BackendIntegrityError('cannot find queue item {} in backend: {}'.format(tx.hash, err))

        logg.info('filter registered {} for {} in {}'.format(tx.status.name, tx.hash, block))

        if self.throttler != None:
            self.throttler.dec(tx.hash)

        return False
