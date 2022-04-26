# standard imports
import logging
import os

# external imports
from chainlib.chain import ChainSpec
from chainsyncer.settings import ChainsyncerSettings

logg = logging.getLogger(__name__)


class ChaindSettings(ChainsyncerSettings):

    def __init__(self, include_sync=False, include_queue=False):
        self.o = {}
        self.get = self.o.get
        self.include_sync = include_sync
        self.include_queue = include_queue


    def process_common(self, config):
        self.o['CHAIN_SPEC'] = ChainSpec.from_chain_str(config.get('CHAIN_SPEC'))
        self.o['SOCKET_PATH'] = config.get('SESSION_SOCKET_PATH')

   
    def process_session(self, config):
        session_id = config.get('SESSION_ID')

        base_dir = os.getcwd()
        data_dir = config.get('SESSION_DATA_DIR')
        if data_dir == None:
            data_dir = os.path.join(base_dir, '.chaind', 'chaind')
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

        data_dir = os.path.join(session_dir, 'sync')
        os.makedirs(data_dir, exist_ok=True)

        # create volatile dir
        uid = os.getuid()
        runtime_dir = config.get('SESSION_RUNTIME_DIR')
        if runtime_dir == None:
            runtime_dir = os.path.join('/run', 'user', str(uid), 'chaind')
        runtime_dir = os.path.join(runtime_dir, config.get('CHAIND_ENGINE'), session_id, 'sync')
        os.makedirs(runtime_dir, exist_ok=True)

        self.o['SESSION_RUNTIME_DIR'] = runtime_dir
        self.o['SESSION_DATA_DIR'] = data_dir
        self.o['SESSION_ID'] = session_id

    
    def process_sync_interface(self, config):
        raise NotImplementedError('no sync interface implementation defined')


    def process_sync(self, config):
        self.process_sync_interface(config)
        self.process_sync_range(config)

                
    def process(self, config):
        self.process_common(config)
        self.process_session(config)
        if self.include_sync:
            self.process_sync(config)


    def __str__(self):
        ks = list(self.o.keys())
        ks.sort()
        s = ''
        for k in ks:
            s += '{}: {}\n'.format(k, self.o.get(k))
        return s
