def process_config(config, arg, args, flags):
    args_override = {}
    if arg.match('session', flags):
        args_override['SESSION_ID'] = getattr(args, 'session_id')
        args_override['SESSION_RUNTIME_DIR'] = getattr(args, 'runtime_path')
        args_override['SESSION_DATA_DIR'] = getattr(args, 'state_path')

    if arg.match('socket', flags):
        args_override['SESSION_SOCKET_PATH'] = getattr(args, 'socket')

    if arg.match('token', flags):
        args_override['TOKEN_MODULE'] = getattr(args, 'token_module')

    config.dict_override(args_override, 'local cli args')

    if arg.match('socket_client', flags):
        config.add(getattr(args, 'send_socket'), '_SOCKET_SEND', False)

    return config
