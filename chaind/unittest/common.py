# standard imports
import hashlib
import tempfile

# external imports
from chainqueue.cache import CacheTokenTx
from chainlib.status import Status as TxStatus
from chainlib.chain import ChainSpec
from chainlib.error import RPCException
from chainlib.tx import (
        Tx,
        TxResult,
        )
from chainlib.block import Block


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


class MockTx(Tx):

    def __init__(self, tx_hash, status=TxStatus.SUCCESS):
        result = TxResult()
        result.status = status
        super(MockTx, self).__init__(result=result)
        self.set_hash(tx_hash)


class MockBlock(Block):

    def __init__(self, number):
        super(MockBlock, self).__init__()
        self.number = number
