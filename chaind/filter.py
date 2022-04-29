# standard imports
import logging
import time

# external imports
from chainlib.status import Status as TxStatus
from chainsyncer.filter import SyncFilter
from chainqueue.error import NotLocalTxError

# local imports
from .error import QueueLockError

logg = logging.getLogger(__name__)

class StateFilter(SyncFilter):

    delay_limit = 3.0

    def __init__(self, adapter, throttler=None):
        self.adapter = adapter
        self.throttler = throttler


    def filter(self, conn, block, tx, session=None):
        try:
            cache_tx = self.adapter.get(tx.hash)
        except NotLocalTxError:
            logg.debug('skipping not local transaction {}'.format(tx.hash))
            return False

        delay = 0.01
        while True:
            if delay > self.delay_limit:
                raise QueueLockError('The queue lock for tx {} seems to be stuck. Human meddling needed.'.format(tx.hash))
            try:
                if tx.status == TxStatus.SUCCESS:
                    self.adapter.succeed(block, tx)
                else:
                    self.adapter.fail(block, tx)
                break
            except QueueLockError as e:
                logg.debug('queue item {} is blocked, will retry: {}'.format(tx.hash, e))
                time.sleep(delay)
                delay *= 2

        if self.throttler != None:
            self.throttler.dec(tx.hash)

        return False
