# standard imports
import logging
import os
import uuid

# external imports
from chainlib.settings import ChainSettings

logg = logging.getLogger(__name__)


class ChaindSettings(ChainSettings):

    def __init__(settings, include_sync=False, include_queue=False):
        super(ChaindSettings, settings).__init__()
        settings.include_sync = include_sync
        settings.include_queue = include_queue


    def dir_for(self, k):
        return os.path.join(self.o['SESSION_DIR'], k)


def process_session(settings, config):
    session_id = config.get('SESSION_ID')

    base_dir = os.getcwd()
    data_dir = config.get('SESSION_DATA_DIR')
    if data_dir == None:
        data_dir = os.path.join(base_dir, '.chaind', 'chaind', settings.o.get('CHAIND_BACKEND'))
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
        runtime_dir = os.path.join('/run', 'user', str(uid), 'chaind', settings.o.get('CHAIND_BACKEND'))
    #runtime_dir = os.path.join(runtime_dir, config.get('CHAIND_ENGINE'), session_id, config.get('CHAIND_COMPONENT'))
    runtime_dir = os.path.join(runtime_dir, config.get('CHAIND_ENGINE'), session_id)
    os.makedirs(runtime_dir, exist_ok=True)

    settings.set('SESSION_RUNTIME_DIR', runtime_dir)
    settings.set('SESSION_DIR', session_dir)
    settings.set('SESSION_DATA_DIR', data_dir)
    settings.set('SESSION_ID', session_id)

    return settings


def process_sync(settings, config):
    settings = process_sync_range(settings, config)
    return settings


def process_socket(settings, config):
    socket_path = config.get('SESSION_SOCKET_PATH')
    if socket_path == None:
        socket_path = os.path.join(settings.get('SESSION_RUNTIME_DIR'), 'chaind.sock')
    settings.get('SESSION_SOCKET_PATH', socket_path)
    return settings


def process_dispatch(settings, config):
    settings.set('SESSION_DISPATCH_DELAY', 0.01)
    return settings


def process_token(settings, config):
    settings.set('TOKEN_MODULE', config.get('TOKEN_MODULE'))
    return settings


def process_backend(settings, config):
    syncer_backend = settings.get('SYNCER_BACKEND')
    queue_backend = settings.get('QUEUE_BACKEND')
    backend = None
    if settings.include_sync and settings.include_queue:
        if queue_backend != syncer_backend:
            raise ValueError('queue and syncer backends must match. queue "{}" != syncer "{}"'.format(queue_backend, syncer_backend))
        backend = syncer_backend
    elif settings.include_sync:
        backend = syncer_backend
    elif settings.include_queue:
        backend = queue_backen
    else:
        raise ValueError('at least one backend must be set')

    settings.set('CHAIND_BACKEND', backend)
    return settings
   

def process_chaind_queue(settings, config):
    if config.get('QUEUE_STATE_PATH') == None:
        queue_state_dir = settings.dir_for('queue')
        config.add(queue_state_dir, 'QUEUE_STATE_PATH', False)
        logg.debug('setting queue state path {}'.format(queue_state_dir))
    
    settings = process_queue_tx(settings, config)
    settings = process_queue_paths(settings, config)
    if config.get('QUEUE_BACKEND') == 'fs':
        settings = process_queue_backend_fs(settings, config)
    settings = process_queue_backend(settings, config)
    settings = process_queue_store(settings, config)
    
    return settings


#def process_settings(settings, config):
#    if settings = include_queue:
#        settings = process_queue_backend(settings, config)
#    if settings = include_sync:
#        settings = process_sync_backend(settings, config)
#
#    settings = process_backend(settings, config)
#    settings = process_session(settings, config)
#
#    if settings = include_sync:
#        settings = process_sync(settings, config)
#    if settings = include_queue:
#        settings = process_chaind_queue(settings, config)
#        settings = process_dispatch(settings, config)
#        settings = process_token(settings, config)
#
#    settings = process_socket(settings, config)
#
#    return settings
