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

# local imports
from chaind.adapters.new import ChaindFsAdapter

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()


class MockCacheAdapter(CacheTokenTx):

    def deserialize(self, v):
        tx = CacheTokenTx()
        h = hashlib.sha256()
        h.update(v.encode('utf-8'))
        z = h.digest()
        tx.tx_hash = z.hex()
        return tx


class TestChaindFs(unittest.TestCase):

    def setUp(self):
        self.chain_spec = ChainSpec('foo', 'bar', 42, 'baz')
        self.path = tempfile.mkdtemp()
        self.adapter = ChaindFsAdapter(self.chain_spec, self.path, MockCacheAdapter().deserialize)


    def tearDown(self):
        shutil.rmtree(self.path)


    def test_fs_setup(self):
        data = os.urandom(128).hex()
        hsh = self.adapter.add(data)
        v = self.adapter.get(hsh)
        self.assertEqual(data, v)


if __name__ == '__main__':
    unittest.main()
