# standard imports
import logging
import os
import uuid

# external imports
from chainlib.settings import ChainSettings
from chainqueue.settings import *

logg = logging.getLogger(__name__)


class ChaindSettings(ChainSettings):

    def __init__(settings, include_sync=False, include_queue=False):
        super(ChaindSettings, settings).__init__()
        settings.include_sync = include_sync
        settings.include_queue = include_queue


    def dir_for(self, k):
        return os.path.join(self.o['SESSION_PATH'], k)


def process_session(settings, config):
    session_id = config.get('SESSION_ID')

    base_dir = os.getcwd()
    data_dir = config.get('SESSION_DATA_PATH')
    if data_dir == None:
        data_dir = os.path.join(base_dir, '.chaind', 'chaind', settings.get('CHAIND_BACKEND'))
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

    chain_spec = settings.get('CHAIN_SPEC')
    network_id_str = str(chain_spec.network_id())
    # create the session persistent dir
    session_path = os.path.join(
            data_engine_dir,
            chain_spec.arch(),
            chain_spec.fork(),
            network_id_str,
            session_id,
            )
    if make_default:
        fp = os.path.join(data_engine_dir, 'default')
        os.symlink(session_path, fp)

    data_path = session_path
    os.makedirs(data_path, exist_ok=True)

    # create volatile dir
    uid = os.getuid()
    runtime_path = config.get('SESSION_RUNTIME_PATH')
    if runtime_path == None:
        runtime_path = os.path.join('/run', 'user', str(uid), 'chaind', settings.get('CHAIND_BACKEND'))
    runtime_path = os.path.join(
            runtime_path,
            config.get('CHAIND_ENGINE'),
            chain_spec.arch(),
            chain_spec.fork(),
            str(chain_spec.network_id()),
            session_id,
            )
    os.makedirs(runtime_path, exist_ok=True)

    settings.set('SESSION_RUNTIME_PATH', runtime_path)
    settings.set('SESSION_PATH', session_path)
    settings.set('SESSION_DATA_PATH', data_path)
    settings.set('SESSION_ID', session_id)

    return settings


def process_socket(settings, config):
    socket_path = config.get('SESSION_SOCKET_PATH')
    if socket_path == None:
        socket_path = os.path.join(settings.get('SESSION_RUNTIME_PATH'), 'chaind.sock')
    settings.set('SESSION_SOCKET_PATH', socket_path)
    return settings


def process_dispatch(settings, config):
    settings.set('SESSION_DISPATCH_DELAY', 0.01)
    return settings


def process_token(settings, config):
    settings.set('TOKEN_MODULE', config.get('TOKEN_MODULE'))
    return settings


def process_backend(settings, config):
    settings.set('CHAIND_BACKEND', config.get('STATE_BACKEND')) #backend)
    return settings
   

def process_queue(settings, config):
    if config.get('STATE_PATH') == None:
        queue_state_dir = settings.dir_for('queue')
        config.add(queue_state_dir, 'STATE_PATH', False)
        logg.debug('setting queue state path {}'.format(queue_state_dir))
    
    settings = process_queue_tx(settings, config)
    settings = process_queue_paths(settings, config)
    if config.get('STATE_BACKEND') == 'fs':
        settings = process_queue_backend_fs(settings, config)
    settings = process_queue_store(settings, config)
    
    return settings
