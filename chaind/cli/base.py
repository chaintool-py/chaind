# standard imports
import enum


class ChaindFlag(enum.IntEnum):
    SESSION = 1
    DISPATCH = 512
    SOCKET = 4096

argflag_local_base = ChaindFlag.SESSION
