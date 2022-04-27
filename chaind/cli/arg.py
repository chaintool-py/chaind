# local imports
from .base import ChaindFlag

def process_flags(argparser, flags):
    if flags & ChaindFlag.SESSION > 0:
        argparser.add_argument('--session-id', dest='session_id', type=str, help='Session to store state and data under')
        argparser.add_argument('--runtime-dir', dest='runtime_dir', type=str, help='Directory to store volatile data')
        argparser.add_argument('--data-dir', dest='data_dir', type=str, help='Directory to store persistent data')

    if flags & ChaindFlag.SOCKET > 0:
        argparser.add_argument('--socket-path', dest='socket', type=str, help='UNIX socket path')

    if flags & ChaindFlag.SOCKET_CLIENT > 0:
        argparser.add_argument('--send-socket', dest='socket_send', action='store_true', help='Send to UNIX socket')

    if flags & ChaindFlag.TOKEN > 0:
        argparser.add_argument('--token-module', dest='token_module', type=str, help='Python module path to resolve tokens from identifiers')
