# standard imports
import logging
import os
import time

# external imports
from chainlib.error import RPCException
from chainqueue import Status
from chainqueue.cache import Cache
from chainqueue.store.fs import (
        IndexStore,
        CounterStore,
        )
from shep.store.file import SimpleFileStoreFactory
from shep.error import (
        StateInvalid,
        StateLockedKey,
        )

# local imports
from .base import ChaindAdapter
from chaind.lock import StoreLock

logg = logging.getLogger(__name__)


class ChaindFsAdapter(ChaindAdapter):

    def __init__(self, chain_spec, path, cache_adapter, dispatcher, cache=None, pending_retry_threshold=0, error_retry_threshold=0, digest_bytes=32, event_callback=None, store_sync=True):
        factory = SimpleFileStoreFactory(path, use_lock=True).add
        state_store = Status(factory, allow_invalid=True, event_callback=event_callback)
        index_path = os.path.join(path, 'tx')
        index_store = IndexStore(index_path, digest_bytes=digest_bytes)
        counter_store = CounterStore(path)
        super(ChaindFsAdapter, self).__init__(chain_spec, state_store, index_store, counter_store, cache_adapter, dispatcher, cache=cache, pending_retry_threshold=pending_retry_threshold, error_retry_threshold=error_retry_threshold, store_sync=store_sync)


    def put(self, signed_tx):
        (s, tx_hash,) = self.store.put(signed_tx, cache_adapter=self.cache_adapter)
        return tx_hash


    def get(self, tx_hash):
        v = None
        store_lock = StoreLock()
        while True:
            try:
                v = self.store.get(tx_hash)
                break
            except StateInvalid as e:
                logg.error('I am just a simple syncer and do not know how to handle the state which the tx {} is in: {}'.format(tx_hash, e))
                return None
            except FileNotFoundError as e:
                logg.debug('queuestore get (file missing) {} failed, possible race condition (will try again): {}'.format(tx_hash, e))
                store_lock.again()
                continue
            except StateLockedKey as e:
                logg.debug('queuestore get (statelock) {} failed, possible race condition (will try again): {}'.format(tx_hash, e))
                store_lock.again()
                continue

        return v[1]


    def upcoming(self, limit=0):
        real_limit = 0
        in_flight = []
        if limit > 0:
            in_flight = self.store.by_state(state=self.store.IN_NETWORK, not_state=self.store.FINAL)
            real_limit = limit - len(in_flight)
            if real_limit <= 0:
                return []
        r = self.store.upcoming(limit=real_limit)
        logg.info('upcoming returning {} upcoming from limit {} less {} active in-flight txs'.format(len(r), limit, len(in_flight)))
        return r


    def pending(self):
        return self.store.pending()


    def deferred(self):
        return self.store.deferred()


    def failed(self):
        return self.store.failed()


    def succeed(self, block, tx):
        if self.store.is_reserved(tx.hash):
            raise QueueLockError(tx.hash)
        r = self.store.final(tx.hash, block, tx, error=False)
        (k, v) = self.store.get(tx.hash)
        self.store.purge(k)
        return r


    def fail(self, block, tx):
        if self.store.is_reserved(tx.hash):
            raise QueueLockError(tx.hash)
        r = self.store.final(tx.hash, block, tx, error=True)
        (k, v) = self.store.get(tx.hash)
        self.store.purge(k)
        return r


    def sendfail(self):
        return self.store.fail(tx.hash)


    def enqueue(self, tx_hash):
        return self.store.enqueue(tx_hash)


    def dispatch(self, tx_hash):
        entry = None

        store_lock = StoreLock()
        while True:
            try:
                entry = self.store.send_start(tx_hash)
                break
            except FileNotFoundError as e:
                logg.debug('dispatch failed to find {} in backend, will try again: {}'.format(tx_hash, e))
                store_lock.again()
                continue
            except StateLockedKey as e:
                logg.debug('dispatch failed to find {} in backend, will try again: {}'.format(tx_hash, e))
                store_lock.again()
                continue

        tx_wire = entry.serialize()

        r = None
        try:
            r = self.dispatcher.send(tx_wire)
        except RPCException as e:
            logg.error('dispatch send failed for {}: {}'.format(tx_hash, e))
            self.store.fail(tx_hash)
            return False

        store_lock = StoreLock()
        while True:
            try:
                self.store.send_end(tx_hash)
                break
            except FileNotFoundError as e:
                logg.debug('dispatch failed to find {} in backend, will try again: {}'.format(tx_hash, e))
                store_lock.again(e)
                continue
            except StateLockedKey as e:
                logg.debug('dispatch failed to find {} in backend, will try again: {}'.format(tx_hash, e))
                store_lock.again(e)
                continue

        return True
