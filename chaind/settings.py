# standard imports
import logging
import os

# external imports
from chainlib.chain import ChainSpec
from chainlib.eth.block import block_latest
from hexathon import (
        to_int as hex_to_int,
        strip_0x,
        )

logg = logging.getLogger(__name__)


class ChaindSettings:

    def __init__(self):
        self.o = {}
        self.get = self.o.get


    def process_common(self, config):
        self.o['CHAIN_SPEC'] = ChainSpec.from_chain_str(config.get('CHAIN_SPEC'))
        self.o['SOCKET_PATH'] = config.get('SESSION_SOCKET_PATH')

   
    def process_sync_range(self, config):
        o = block_latest()
        r = self.o['RPC'].do(o)
        block_offset = int(strip_0x(r), 16) + 1
        logg.info('network block height at startup is {}'.format(block_offset))

        keep_alive = False
        session_block_offset = 0
        block_limit = 0
        session_block_offset = int(config.get('SYNCER_OFFSET'))

        until = int(config.get('SYNCER_LIMIT'))
        if until > 0:
            if until <= session_block_offset:
                raise ValueError('sync termination block number must be later than offset ({} >= {})'.format(session_block_offset, until))
            block_limit = until
        else:
            keep_alive=True
            block_limit = -1

        if session_block_offset == -1:
            session_block_offset = block_offset
        elif not config.true('_KEEP_ALIVE'):
            if block_limit == 0:
                lock_limit = block_offset
    
        self.o['SYNCER_OFFSET'] = session_block_offset
        self.o['SYNCER_LIMIT'] = block_limit


    def process_sync_session(self, config):
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
        self.process_sync_session(config)
        self.process_sync_range(config)

                
    def process(self, config):
        self.process_common(config)
        self.process_sync(config)


    def __str__(self):
        ks = list(self.o.keys())
        ks.sort()
        s = ''
        for k in ks:
            s += '{}: {}\n'.format(k, self.o.get(k))
        return s
