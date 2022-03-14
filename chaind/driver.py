# standard imports
import logging

logg = logging.getLogger(__name__)


class QueueDriver:

    def __init__(self, adapter, throttler=None):
        self.adapter = adapter
        self.throttler = throttler


    def __enqueue(self, txs):
        c = len(txs)
        if self.throttler != None:
            r = self.throttler.count()
            if r < c:
                c = r
        for i in range(c):
            self.adapter.enqueue(txs[i])
            if self.throttler != None:
                self.throttler.inc(txs[i].hash)
        return c


    def process(self):
        total = 0
        txs = self.adapter.pending()
        r = self.__enqueue(txs)
        total += r
        logg.debug('pending enqueued {} total {}'.format(r, total))

        txs = self.adapter.deferred()
        r = self.__enqueue(txs)
        total += r
        logg.debug('deferred enqueued {} total {}'.format(r, total))

        return txs
