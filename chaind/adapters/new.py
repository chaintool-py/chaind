# external imports
from chainlib.error import RPCException
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

    def __init__(self, chain_spec, path, deserializer, dispatcher, cache=None, pending_retry_threshold=0, error_retry_threshold=0, digest_bytes=32):
        factory = SimpleFileStoreFactory(path).add
        state_store = Status(factory)
        index_store = IndexStore(path, digest_bytes=digest_bytes)
        counter_store = CounterStore(path)
        self.store = QueueStore(chain_spec, state_store, index_store, counter_store, cache=cache)
        self.deserialize = deserializer
        self.dispatcher = dispatcher


    def put(self, signed_tx):
        cache_tx = self.deserialize(signed_tx)
        self.store.put(cache_tx.tx_hash, signed_tx)
        return cache_tx.tx_hash


    def get(self, tx_hash):
        v = self.store.get(tx_hash)
        return v[1]


    def upcoming(self):
        return self.store.upcoming()


    def pending(self):
        return self.store.pending()


    def deferred(self):
        return self.store.deferred()


    def enqueue(self, tx_hash):
        return self.store.enqueue(tx_hash)


    def dispatch(self, tx_hash):
        entry = self.store.send_start(tx_hash)
        tx_wire = entry.serialize()

        r = None
        try:
            r = self.dispatcher.send(tx_wire)
        except RPCException:
            self.store.fail(tx_hash)
            return False

        self.store.send_end(tx_hash)
        return True
