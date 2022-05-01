# standard imports
import os
import unittest
import shutil
import logging

# external imports
from chainlib.status import Status as TxStatus

# local imports
from chaind.driver import QueueDriver
from chaind.filter import StateFilter

# test imports
from chaind.unittest.common import (
    MockTx,
    MockCacheAdapter,
    MockDispatcher,
    )
from chaind.unittest.fs import TestChaindFsBase

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()


class TestChaindFs(TestChaindFsBase):

    def setUp(self):
        self.cache_adapter = MockCacheAdapter
        self.dispatcher = MockDispatcher()
        super(TestChaindFs, self).setUp()


    def tearDown(self):
        shutil.rmtree(self.path)


    def test_fs_setup(self):
        data = os.urandom(128).hex()
        hsh = self.adapter.put(data)
        v = self.adapter.get(hsh)
        self.assertEqual(data, v)


    def test_fs_fail(self):
        data = os.urandom(128).hex()
        hsh = self.adapter.put(data)
        self.dispatcher.add_fail(data)

        r = self.adapter.dispatch(hsh)
        self.assertFalse(r)

        txs = self.adapter.failed()
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
        
        fltr = StateFilter(self.chain_spec, self.path, MockCacheAdapter)
        tx = MockTx(hsh)
        fltr.filter(None, None, tx)


    def test_fs_filter_fail(self):
        drv = QueueDriver(self.adapter)

        data = os.urandom(128).hex()
        hsh = self.adapter.put(data)
        
        fltr = StateFilter(self.chain_spec, self.path, MockCacheAdapter)
        tx = MockTx(hsh, TxStatus.ERROR)
        fltr.filter(None, None, tx)


    def test_upcoming(self):
        drv = QueueDriver(self.adapter)

        txs = []
        for i in range(10):
            data = os.urandom(128).hex()
            hsh = self.adapter.put(data)
            txs.append(hsh)
            self.adapter.enqueue(hsh)

        r = self.adapter.upcoming(limit=5)
        self.assertEqual(len(r), 5)

        r = self.adapter.dispatch(txs[0])
        self.assertTrue(r)

        r = self.adapter.upcoming(limit=5)
        self.assertEqual(len(r), 4)


if __name__ == '__main__':
    unittest.main()
