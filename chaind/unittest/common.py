# standard imports
import unittest
import hashlib
import tempfile

# external imports
from chainqueue.cache import CacheTokenTx
from chainlib.status import Status as TxStatus
from chainlib.chain import ChainSpec
from chainlib.error import RPCException

# local imports
from chaind.adapters.fs import ChaindFsAdapter


class MockCacheAdapter(CacheTokenTx):

    def deserialize(self, v):
        h = hashlib.sha256()
        h.update(v.encode('utf-8'))
        z = h.digest()
        self.hash = z.hex()


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


class TestChaindFsBase(unittest.TestCase):

    def setUp(self):
        self.chain_spec = ChainSpec('foo', 'bar', 42, 'baz')
        self.path = tempfile.mkdtemp()
        self.dispatcher = MockDispatcher()
        self.adapter = ChaindFsAdapter(self.chain_spec, self.path, self.cache_adapter, self.dispatcher)

