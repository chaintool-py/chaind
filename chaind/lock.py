# standard imports
import time

# local imports
from .error import BackendError

BASE_DELAY = 0.01
BASE_DELAY_LIMIT = 10.0


class StoreLock:

    def __init__(self, delay=BASE_DELAY, delay_limit=BASE_DELAY_LIMIT, error=BackendError, description=None):
        self.base_delay = delay
        self.delay = delay
        self.delay_limit = delay_limit
        self.error = error
        self.description = description

    
    def again(self, e=None):
        if self.delay > self.delay_limit:
            err = None
            if e != None:
                err = str(e)
            else:
                err = self.description
            raise self.error(err)
        time.sleep(self.delay)
        self.delay *= 2


    def reset(self):
        self.delay = self.base_delay
