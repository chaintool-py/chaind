# standard imports
import unittest
import tempfile
import logging

# external imports
from chainlib.chain import ChainSpec

# local imports
from chaind.adapters.fs import ChaindFsAdapter

logging.STATETRACE = 5
logg = logging.getLogger(__name__)
logg.setLevel(logging.STATETRACE)


class TestChaindFsBase(unittest.TestCase):

    def setUp(self):
        self.chain_spec = ChainSpec('foo', 'bar', 42, 'baz')
        self.path = tempfile.mkdtemp()
        self.adapter = ChaindFsAdapter(self.chain_spec, self.path, self.cache_adapter, self.dispatcher, event_callback=self.log_state)


    def log_state(self, k, from_state, to_state):
        logg.log(logging.STATETRACE, 'state change {}: {} -> {}'.format(
            k,
            from_state,
            to_state,
            )
            )
