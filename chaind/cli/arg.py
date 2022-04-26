# external imports
from chainlib.eth.cli import ArgumentParser as BaseArgumentParser

# local imports
from .base import SyncFlag, Flag


class ArgumentParser(BaseArgumentParser):

    def process_local_flags(self, local_arg_flags):
        if local_arg_flags & SyncFlag.SESSION:
            self.add_argument('--session-id', dest='session_id', type=str, help='Session to store state and data under')
            self.add_argument('--runtime-dir', dest='runtime_dir', type=str, help='Directory to store volatile data')
            self.add_argument('--data-dir', dest='data_dir', type=str, help='Directory to store persistent data')
        if local_arg_flags & SyncFlag.SYNCER:
            self.add_argument('--offset', type=int, help='Block to start sync from. Default is the latest block at first run.')
            self.add_argument('--until', type=int, default=-1, help='Block to stop sync on. Default is do not stop.')
