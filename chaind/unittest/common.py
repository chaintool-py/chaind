# standard imports
import hashlib
import tempfile

# external imports
from chainqueue.cache import CacheTokenTx
from chainlib.status import Status as TxStatus
from chainlib.chain import ChainSpec
from chainlib.error import RPCException


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
        if v in self.fails:
            raise RPCException('{} is in fails'.format(v))
        pass


class MockTx:

    def __init__(self, tx_hash, status=TxStatus.SUCCESS):
        self.hash = tx_hash
        self.status = status
