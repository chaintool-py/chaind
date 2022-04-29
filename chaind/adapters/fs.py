# standard imports
import logging
import os

# external imports
from chainlib.error import RPCException
from chainqueue import Status
from chainqueue.cache import Cache
from chainqueue.store.fs import (
        IndexStore,
        CounterStore,
        )
from shep.store.file import SimpleFileStoreFactory
from shep.error import StateInvalid

# local imports
from .base import ChaindAdapter

logg = logging.getLogger(__name__)


class ChaindFsAdapter(ChaindAdapter):

    def __init__(self, chain_spec, path, cache_adapter, dispatcher, cache=None, pending_retry_threshold=0, error_retry_threshold=0, digest_bytes=32):
        factory = SimpleFileStoreFactory(path).add
        state_store = Status(factory)
        index_path = os.path.join(path, 'tx')
        index_store = IndexStore(index_path, digest_bytes=digest_bytes)
        counter_store = CounterStore(path)
        super(ChaindFsAdapter, self).__init__(chain_spec, state_store, index_store, counter_store, cache_adapter, dispatcher, cache=cache, pending_retry_threshold=pending_retry_threshold, error_retry_threshold=error_retry_threshold)


    def put(self, signed_tx):
        (s, tx_hash,) = self.store.put(signed_tx, cache_adapter=self.cache_adapter)
        return tx_hash


    def get(self, tx_hash):
        v = None
        try:
            v = self.store.get(tx_hash)
        except StateInvalid as e:
            logg.error('I am just a simple syncer and do not know how to handle the state which the tx {} is in: {}'.format(tx_hash, e))
            return None
        return v[1]


    def upcoming(self):
        return self.store.upcoming()


    def pending(self):
        return self.store.pending()


    def deferred(self):
        return self.store.deferred()


    def succeed(self, block, tx):
        if self.store.is_reserved(tx.hash):
            raise QueueLockError(tx.hash)

        return self.store.final(tx.hash, block, tx, error=False)


    def fail(self, block, tx):
        return self.store.final(tx.hash, block, tx, error=True)


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
