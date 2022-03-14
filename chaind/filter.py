# external imports
from chainlib.status import Status as TxStatus


class StateFilter:

    def __init__(self, adapter, throttler=None):
        self.adapter = adapter
        self.throttler = throttler


    def filter(self, conn, block, tx, session=None):
        cache_tx = self.adapter.get(tx.hash)
        if tx.status == TxStatus.SUCCESS:
            self.adapter.succeed(block, tx)
        else:
            self.adapter.fail(block, tx)
        if self.throttler != None:
            self.throttler.dec(tx.hash)
