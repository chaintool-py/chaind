# local imports
from .base import ChaindFlag

def process_flags(argparser, flags):
    if flags & ChaindFlag.SESSION:
        argparser.add_argument('--session-id', dest='session_id', type=str, help='Session to store state and data under')
        argparser.add_argument('--runtime-dir', dest='runtime_dir', type=str, help='Directory to store volatile data')
        argparser.add_argument('--data-dir', dest='data_dir', type=str, help='Directory to store persistent data')

    if flags & ChaindFlag.SOCKET:
        argparser.add_argument('--socket', type=str, help='Socket path to send transactions to (assumes -s).')
