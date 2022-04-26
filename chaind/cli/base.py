# standard imports
import enum

# external imports
from chainlib.eth.cli import (
    argflag_std_read,
    argflag_std_write,
    argflag_std_base,
    Flag,
    )


class SyncFlag(enum.IntEnum):
    SESSION = 1
    SYNCER = 16
    QUEUE = 256
    DISPATCH = 512
    SOCKET = 4096


argflag_local_sync = argflag_std_base | Flag.CHAIN_SPEC | SyncFlag.SYNCER | SyncFlag.SESSION
argflag_local_queue = SyncFlag.QUEUE | Flag.CHAIN_SPEC | SyncFlag.SOCKET | SyncFlag.SESSION
