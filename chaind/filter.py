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
        self.last_block_height = 0
        self.adapter = None
        self.store_lock = None


    def __get_adapter(self, block, force_reload=False):
        if self.store_lock == None:
            self.store_lock = StoreLock()

        reload = False
        if block.number != self.last_block_height:
            reload = True
        elif self.adapter == None:
            reload = True
        elif force_reload:
            reload = True
        
        self.last_block_height = block.number

        if reload:
            while True:
                logg.info('reloading adapter')
                try:
                    self.adapter = ChaindFsAdapter(
                        self.chain_spec,
                        self.adapter_path,
                        self.tx_adapter,
                        None,
                        )
                    break
                except BackendError as e:
                    logg.error('adapter instantiation failed: {}, one more try'.format(e))
                    self.store_lock.again()
                    continue

        return self.adapter


    def filter(self, conn, block, tx, session=None):
        cache_tx = None
        queue_adapter = self.__get_adapter(block)
        
        self.store_lock.reset()
    
        while True:
            try:
                cache_tx = queue_adapter.get(tx.hash)
                break
            except NotLocalTxError:
                logg.debug('skipping not local transaction {}'.format(tx.hash))
                return False
            except BackendError as e:
                logg.error('adapter get failed: {}, one more try'.format(e))
                self.store_lock.again()
                queue_adapter = self.__get_adapter(block, force_reload=True)
                continue

        if cache_tx == None:
            raise NotLocalTxError(tx.hash)

        self.store_lock.reset()

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
                self.store_lock.again()
                queue_adapter = self.__get_adapter(block, force_reload=True)
                continue
            except NotLocalTxError as e:
                logg.debug('queue item {} not found, possible race condition, will retry: {}'.format(tx.hash, e))
                self.store_lock.again()
                queue_adapter = self.__get_adapter(block, force_reload=True)
                continue
            except StateLockedKey as e:
                logg.debug('queue item {} not found, possible race condition, will retry: {}'.format(tx.hash, e))
                self.store_lock.again()
                queue_adapter = self.__get_adapter(block, force_reload=True)
                continue

        logg.info('filter registered {} for {} in {}'.format(tx.status_name, tx.hash, block))

        if self.throttler != None:
            self.throttler.dec(tx.hash)

        return False
