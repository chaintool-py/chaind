# standard imports
import logging
import os

# external imports
from chainlib.cli import (
        Config as BaseConfig,
        Flag,
        )
from chaind.cli import SyncFlag

script_dir = os.path.dirname(os.path.realpath(__file__))

logg = logging.getLogger(__name__)


class Config(BaseConfig):

    local_base_config_dir = os.path.join(script_dir, '..', 'data', 'config')

    @classmethod
    def from_args(cls, engine, args, arg_flags, local_arg_flags, extra_args={}, default_config_dir=None, base_config_dir=None, default_fee_limit=None):
        expanded_base_config_dir = [cls.local_base_config_dir]
        if base_config_dir != None:
            if isinstance(base_config_dir, str):
                base_config_dir = [base_config_dir]
            for d in base_config_dir:
                expanded_base_config_dir.append(d)
        config = BaseConfig.from_args(args, arg_flags, extra_args=extra_args, default_config_dir=default_config_dir, base_config_dir=expanded_base_config_dir, load_callback=None)

        local_args_override = {}
        if local_arg_flags & SyncFlag.SESSION:
            local_args_override['SESSION_ID'] = getattr(args, 'session_id')
            local_args_override['SESSION_RUNTIME_DIR'] = getattr(args, 'runtime_dir')
            local_args_override['SESSION_DATA_DIR'] = getattr(args, 'data_dir')
            local_args_override['SYNCER_OFFSET'] = getattr(args, 'offset')
            local_args_override['SYNCER_LIMIT'] = getattr(args, 'until')

        if local_arg_flags & SyncFlag.SOCKET:
            local_args_override['SESSION_SOCKET_PATH'] = getattr(args, 'socket')

        config.dict_override(local_args_override, 'local cli args')

        config.add(engine, 'CHAIND_ENGINE', False)

        return config
