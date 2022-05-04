# standard imports
import logging
import time

# external imports
from chainqueue import Store as QueueStore

# local imports
from chaind.lock import StoreLock

logg = logging.getLogger(__name__)


class ChaindAdapter:

    def __init__(self, chain_spec, state_store, index_store, counter_store, cache_adapter, dispatcher, cache=None, pending_retry_threshold=0, error_retry_threshold=0, store_sync=True):
        self.cache_adapter = cache_adapter
        self.dispatcher = dispatcher
        store_lock = StoreLock()
        while True:
            try:
                self.store = QueueStore(chain_spec, state_store, index_store, counter_store, cache=cache, sync=store_sync)
                break
            except FileNotFoundError as e:
                logg.debug('queuestore instantiation failed, possible race condition (will try again): {}'.format(e))
                store_lock.again()
                continue
