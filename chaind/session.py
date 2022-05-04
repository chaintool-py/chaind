# standard imports
import os
import socket
import logging
import stat

# external imports
from hexathon import strip_0x

# local imports
from .error import (
        NothingToDoError,
        ClientGoneError,
        ClientBlockError,
        ClientInputError,
        )
from .lock import StoreLock
from .error import BackendError

logg = logging.getLogger(__name__)


class SessionController:

    def __init__(self, config, processor):
        self.dead = False
        os.makedirs(os.path.dirname(config.get('SESSION_SOCKET_PATH')), exist_ok=True)
        try:
            os.unlink(config.get('SESSION_SOCKET_PATH'))
        except FileNotFoundError:
            pass
        self.socket_path = config.get('SESSION_SOCKET_PATH')

        self.srv = socket.socket(family=socket.AF_UNIX, type=socket.SOCK_STREAM)
        self.srv.bind(config.get('SESSION_SOCKET_PATH'))
        self.srv.listen(2)
        self.srv.settimeout(float(config.get('SESSION_DISPATCH_DELAY')))
        self.processor = processor
        self.chain_spec = config.get('CHAIN_SPEC')


    def shutdown(self, signo, frame):
        if self.dead:
            return
        self.dead = True
        if signo != None:
            logg.info('closing on {}'.format(signo))
        else:
            logg.info('explicit shutdown')
        sockname = self.srv.getsockname()
        self.srv.close()
        try:
            os.unlink(sockname)
        except FileNotFoundError:
            logg.warning('socket file {} already gone'.format(sockname))


    def get_connection(self):
        return self.srv.accept()


    def process(self, conn):
        state_lock = StoreLock()
        r = None
        while True:
            try:
                r = self.processor(conn)
                break
            except BackendError as e:
                state_lock.again(e)
                continue
                
        if r > 0:
            self.srv.settimeout(0.1)
        else:
            self.srv.settimeout(4.0)


    def get(self):
        srvs = None
        try:
            logg.debug('getting connection')
            (srvs, srvs_addr) = self.get_connection()
        except OSError as e:
            try:
                fi = os.stat(self.socket_path)
            except FileNotFoundError:
                logg.error('socket is gone')
                raise ClientGoneError()
            if not stat.S_ISSOCK(fi.st_mode):
                logg.error('entity on socket path is not a socket')
                raise ClientGoneError()
            if srvs == None:
                logg.debug('timeout (remote socket is none)')
                raise NothingToDoError()

        self.srv.settimeout(0.1)
        srvs.settimeout(0.1)
        data_in = None
        try:
            data_in = srvs.recv(1048576)
        except BlockingIOError as e:
            logg.debug('block io error: {}'.format(e))

        if data_in == None:
            raise ClientBlockError()

        data = None
        try:
            data_in_str = data_in.decode('utf-8')
            data_hex = strip_0x(data_in_str.rstrip())
            data = bytes.fromhex(data_hex)
        except ValueError:
            logg.error('invalid input "{}"'.format(data_in_str))
            raise ClientInputError()

        return (srvs, data,)


    def respond_put(self, srvs, r, extra_data=None):
        v = r.to_bytes(4, byteorder='big')
        if extra_data != None:
            v += strip_0x(extra_data).encode('utf-8')
        try:
            srvs.send(v)
            logg.debug('{} bytes sent'.format(len(v)))
        except BrokenPipeError:
            logg.debug('they just hung up. how rude.')
        srvs.close()
