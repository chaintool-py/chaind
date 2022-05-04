# standard imports
import logging

# local ipmorts
from chaind.adapters.fs import ChaindFsAdapter
from chaind.eth.cache import EthCacheTx

logg = logging.getLogger(__name__)


class DispatchProcessor:

    def __init__(self, chain_spec, queue_dir, dispatcher):
        self.dispatcher = dispatcher
        self.chain_spec = chain_spec,
        self.queue_dir = queue_dir


    def process(self, rpc, limit=50):
        adapter = ChaindFsAdapter(
            self.chain_spec,
            self.queue_dir, 
            EthCacheTx,
            self.dispatcher,
            )
        
        upcoming = adapter.upcoming(limit=limit)
        logg.info('processor has {} candidates for {}, processing with limit {}'.format(len(upcoming), self.chain_spec, limit))
        i = 0
        for tx_hash in upcoming:
            if adapter.dispatch(tx_hash):
                i += 1
        return i
