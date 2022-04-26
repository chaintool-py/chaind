# external imports
from chaind.cli import ChaindFlag


def process_config(config, args, flags):
        args_override = {}
        if flags & ChaindFlag.SESSION:
            args_override['SESSION_ID'] = getattr(args, 'session_id')
            args_override['SESSION_RUNTIME_DIR'] = getattr(args, 'runtime_dir')
            args_override['SESSION_DATA_DIR'] = getattr(args, 'data_dir')

        if flags & ChaindFlag.SOCKET:
            args_override['SESSION_SOCKET_PATH'] = getattr(args, 'socket')

        config.dict_override(args_override, 'local cli args')

        return config
