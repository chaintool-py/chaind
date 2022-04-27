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

    if flags & ChaindFlag.TOKEN:
        args_override['TOKEN_MODULE'] = getattr(args, 'token_module')

    config.dict_override(args_override, 'local cli args')

    if flags & ChaindFlag.SOCKET_CLIENT:
        config.add(getattr(args, 'socket_send'), '_SOCKET_SEND', False)

    return config
