# standard imports
import os
import tempfile
import unittest
import shutil
import logging
import hashlib

# external imports
from chainlib.chain import ChainSpec
from chainqueue.cache import CacheTokenTx
from chainlib.error import RPCException
from chainlib.status import Status as TxStatus

# local imports
from chaind.adapters.fs import ChaindFsAdapter
from chaind.driver import QueueDriver
from chaind.filter import StateFilter

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()


class MockCacheAdapter(CacheTokenTx):

    def deserialize(self, v):
        tx = CacheTokenTx()
        h = hashlib.sha256()
        h.update(v.encode('utf-8'))
        z = h.digest()
        tx.hash = z.hex()
        return tx


class MockDispatcher:

    def __init__(self):
        self.fails = []


    def add_fail(self, v):
        self.fails.append(v)


    def send(self, v):
        if v not in self.fails:
            raise RPCException('{} is in fails'.format(v))
        pass


class MockTx:

    def __init__(self, tx_hash, status=TxStatus.SUCCESS):
        self.hash = tx_hash
        self.status = status



class TestChaindFs(unittest.TestCase):

    def setUp(self):
        self.chain_spec = ChainSpec('foo', 'bar', 42, 'baz')
        self.path = tempfile.mkdtemp()
        self.dispatcher = MockDispatcher()
        deserializer = MockCacheAdapter().deserialize
        self.adapter = ChaindFsAdapter(self.chain_spec, self.path, deserializer, self.dispatcher)


    def tearDown(self):
        shutil.rmtree(self.path)


    def test_fs_setup(self):
        data = os.urandom(128).hex()
        hsh = self.adapter.put(data)
        v = self.adapter.get(hsh)
        self.assertEqual(data, v)


    def test_fs_defer(self):
        data = os.urandom(128).hex()
        hsh = self.adapter.put(data)
        self.dispatcher.add_fail(hsh)
        self.adapter.dispatch(hsh)
        txs = self.adapter.deferred()
        self.assertEqual(len(txs), 1)


    def test_fs_process(self):
        drv = QueueDriver(self.adapter)

        data = os.urandom(128).hex()
        hsh = self.adapter.put(data)

        txs = self.adapter.upcoming()
        self.assertEqual(len(txs), 0)

        drv.process()
        txs = self.adapter.upcoming()
        self.assertEqual(len(txs), 1)


    def test_fs_filter(self):
        drv = QueueDriver(self.adapter)

        data = os.urandom(128).hex()
        hsh = self.adapter.put(data)
        
        fltr = StateFilter(self.adapter)
        tx = MockTx(hsh)
        fltr.filter(None, None, tx)


    def test_fs_filter_fail(self):
        drv = QueueDriver(self.adapter)

        data = os.urandom(128).hex()
        hsh = self.adapter.put(data)
        
        fltr = StateFilter(self.adapter)
        tx = MockTx(hsh, TxStatus.ERROR)
        fltr.filter(None, None, tx)


if __name__ == '__main__':
    unittest.main()
