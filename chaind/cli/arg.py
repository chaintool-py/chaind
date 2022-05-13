def apply_flag(flag):
    flag.add('session')
    flag.add('dispatch')
    flag.add('socket')
    flag.add('socket_client')
    flag.add('token')

    flag.alias('chaind_base', 'session')
    flag.alias('chaind_socket_client', 'session', 'socket', 'socket_client')

    return flag


def apply_arg(arg): 
    arg.add_long('session-id', 'session', help='Session to store state and data under')
    arg.add_long('socket-path', 'socket', help='UNIX socket path')
    arg.add_long('send-socket', 'socket_client', typ=bool, help='Send to UNIX socket')
    arg.add_long('token-module', 'token', help='Python module path to resolve tokens from identifiers')
    return arg
