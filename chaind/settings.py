# standard imports
import logging
import os
import uuid

# external imports
from chainsyncer.settings import ChainsyncerSettings
from chainqueue.settings import ChainqueueSettings

logg = logging.getLogger(__name__)


class ChaindSettings(ChainsyncerSettings, ChainqueueSettings):

    def __init__(self, include_sync=False, include_queue=False):
        super(ChaindSettings, self).__init__()
        self.include_sync = include_sync
        self.include_queue = include_queue


    def process_session(self, config):
        session_id = config.get('SESSION_ID')

        base_dir = os.getcwd()
        data_dir = config.get('SESSION_DATA_DIR')
        if data_dir == None:
            data_dir = os.path.join(base_dir, '.chaind', 'chaind', self.o.get('CHAIND_BACKEND'))
        data_engine_dir = os.path.join(data_dir, config.get('CHAIND_ENGINE'))
        os.makedirs(data_engine_dir, exist_ok=True)

        # check if existing session
        if session_id == None:
            fp = os.path.join(data_engine_dir, 'default')
            try:
                os.stat(fp)
                fp = os.path.realpath(fp)
            except FileNotFoundError:
                fp = None
            if fp != None:
                session_id = os.path.basename(fp)

        make_default = False
        if session_id == None:
            session_id = str(uuid.uuid4())
            make_default = True

        # create the session persistent dir
        session_dir = os.path.join(data_engine_dir, session_id)
        if make_default:
            fp = os.path.join(data_engine_dir, 'default')
            os.symlink(session_dir, fp)

        #data_dir = os.path.join(session_dir, config.get('CHAIND_COMPONENT'))
        data_dir = session_dir
        os.makedirs(data_dir, exist_ok=True)

        # create volatile dir
        uid = os.getuid()
        runtime_dir = config.get('SESSION_RUNTIME_DIR')
        if runtime_dir == None:
            runtime_dir = os.path.join('/run', 'user', str(uid), 'chaind', self.o.get('CHAIND_BACKEND'))
        #runtime_dir = os.path.join(runtime_dir, config.get('CHAIND_ENGINE'), session_id, config.get('CHAIND_COMPONENT'))
        runtime_dir = os.path.join(runtime_dir, config.get('CHAIND_ENGINE'), session_id)
        os.makedirs(runtime_dir, exist_ok=True)

        self.o['SESSION_RUNTIME_DIR'] = runtime_dir
        self.o['SESSION_DIR'] = session_dir
        self.o['SESSION_DATA_DIR'] = data_dir
        self.o['SESSION_ID'] = session_id

    
    def process_sync_interface(self, config):
        raise NotImplementedError('no sync interface implementation defined')


    def process_sync(self, config):
        self.process_sync_interface(config)
        self.process_sync_range(config)


    def process_socket(self, config):
        socket_path = config.get('SESSION_SOCKET_PATH')
        if socket_path == None:
            socket_path = os.path.join(self.o['SESSION_RUNTIME_DIR'], 'chaind.sock')
        self.o['SESSION_SOCKET_PATH'] = socket_path


    def process_dispatch(self, config):
        self.o['SESSION_DISPATCH_DELAY'] = 0.01


    def process_token(self, config):
        self.o['TOKEN_MODULE'] = config.get('TOKEN_MODULE')


    def process_backend(self, config):
        if self.include_sync and self.include_queue:
            if self.o['QUEUE_BACKEND'] != self.o['SYNCER_BACKEND']:
                raise ValueError('queue and syncer backends must match. queue "{}" != syncer "{}"'.format(self.o['QUEUE_BACKEND'], self.o['SYNCER_BACKEND']))
            self.o['CHAIND_BACKEND'] = self.o['SYNCER_BACKEND']
        elif self.include_sync:
            self.o['CHAIND_BACKEND'] = self.o['SYNCER_BACKEND']
        elif self.include_queue:
            self.o['CHAIND_BACKEND'] = self.o['QUEUE_BACKEND']
        else:
            raise ValueError('at least one backend must be set')


    def process(self, config):
        super(ChaindSettings, self).process(config)
        if self.include_sync:
            self.process_sync(config)
            self.process_sync_backend(config)
        if self.include_queue:
            self.process_queue_backend(config)
            self.process_dispatch(config)
            self.process_token(config)

        self.process_backend(config)
        self.process_session(config)
        self.process_socket(config)


    def dir_for(self, k):
        return os.path.join(self.o['SESSION_DIR'], k)
