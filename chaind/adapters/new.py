# external imports
from chainqueue import (
        Status,
        Store as QueueStore,
        )
from chainqueue.cache import Cache
from chainqueue.store.fs import (
        IndexStore,
        CounterStore,
        )
from shep.store.file import SimpleFileStoreFactory


class ChaindFsAdapter:

    def __init__(self, chain_spec, path, deserializer, cache=None, pending_retry_threshold=0, error_retry_threshold=0, digest_bytes=32):
        factory = SimpleFileStoreFactory(path).add
        state_store = Status(factory)
        index_store = IndexStore(path, digest_bytes=digest_bytes)
        counter_store = CounterStore(path)
        self.store = QueueStore(chain_spec, state_store, index_store, counter_store, cache=cache)
        self.deserialize = deserializer


    def add(self, signed_tx):
        cache_tx = self.deserialize(signed_tx)
        self.store.put(cache_tx.tx_hash, signed_tx)
        return cache_tx.tx_hash


    def get(self, tx_hash):
        v = self.store.get(tx_hash)
        return v[1]
