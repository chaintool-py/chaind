# standard imports
import logging

# external imports
from chainlib.status import Status as TxStatus
from chainsyncer.filter import SyncFilter
from chainqueue.error import NotLocalTxError

logg = logging.getLogger(__name__)

class StateFilter(SyncFilter):

    def __init__(self, adapter, throttler=None):
        self.adapter = adapter
        self.throttler = throttler


    def filter(self, conn, block, tx, session=None):
        try:
            cache_tx = self.adapter.get(tx.hash)
        except NotLocalTxError:
            logg.debug('skipping not local transaction {}'.format(tx.hash))
            return False

        if tx.status == TxStatus.SUCCESS:
            self.adapter.succeed(block, tx)
        else:
            self.adapter.fail(block, tx)
        if self.throttler != None:
            self.throttler.dec(tx.hash)

        return False
