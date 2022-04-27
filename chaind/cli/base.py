# standard imports
import enum


class ChaindFlag(enum.IntEnum):
    SESSION = 1
    DISPATCH = 2
    SOCKET = 16
    SOCKET_CLIENT = 32
    TOKEN = 256

argflag_local_base = ChaindFlag.SESSION
argflag_local_socket_client = ChaindFlag.SESSION | ChaindFlag.SOCKET | ChaindFlag.SOCKET_CLIENT
