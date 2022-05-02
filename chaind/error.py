class TxSourceError(Exception):
    pass


class NothingToDoError(Exception):
    pass


class ClientGoneError(Exception):
    pass


class ClientBlockError(BlockingIOError):
    pass


class ClientInputError(ValueError):
    pass


class QueueLockError(Exception):
    pass


class BackendError(Exception):
    pass
