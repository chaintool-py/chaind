# external imports
from chainqueue import Store as QueueStore


class ChaindAdapter:

    def __init__(self, chain_spec, state_store, index_store, counter_store,deserializer, dispatcher, cache=None, pending_retry_threshold=0, error_retry_threshold=0):
        self.deserialize = deserializer
        self.dispatcher = dispatcher
        self.store = QueueStore(chain_spec, state_store, index_store, counter_store, cache=cache)
