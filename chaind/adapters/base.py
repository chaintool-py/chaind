# standard imports
import logging
import time

# external imports
from chainqueue import Store as QueueStore

# local imports
from chaind.error import BackendIntegrityError

logg = logging.getLogger(__name__)


class ChaindAdapter:

    race_delay = 0.1

    def __init__(self, chain_spec, state_store, index_store, counter_store, cache_adapter, dispatcher, cache=None, pending_retry_threshold=0, error_retry_threshold=0):
        self.cache_adapter = cache_adapter
        self.dispatcher = dispatcher
        err = None
        for i in range(3):
            try:
                self.store = QueueStore(chain_spec, state_store, index_store, counter_store, cache=cache)
                err = None
                break
            except FileNotFoundError as e:
                logg.debug('queuestore instantiation failed, possible race condition (will try again): {}'.format(e))
                err = e
                time.sleep(self.race_delay)
                continue

        if err != None:
            raise BackendIntegrityError(err)
