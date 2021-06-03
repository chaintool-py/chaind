# standard imports
import os
import uuid

# external imports
import chainqueue
import chainsyncer
from xdg.BaseDirectory import (
        xdg_data_dirs,
        get_runtime_dir,
        load_first_config,
        )


class Environment:

    def __init__(self, domain=None, session=None, env={}):
        if not session:
            session = env.get('CHAIND_SESSION')
        if not session:
            session = uuid.uuid4()
        self.__session = session

        if not domain:
            domain = env.get('CHAIND_DOMAIN')

        base_config_dir = load_first_config('chaind')
        self.runtime_dir = os.path.join(get_runtime_dir(), 'chaind')
        self.data_dir = os.path.join(xdg_data_dirs[0], 'chaind')
        self.config_dir = env.get('CONFINI_DIR', os.path.join(base_config_dir))
        self.session_runtime_dir = os.path.join(self.runtime_dir, self.session)

        if domain:
            self.runtime_dir = os.path.join(self.runtime_dir, domain)
            self.data_dir = os.path.join(self.data_dir, domain)
            self.config_dir = os.path.join(self.config_dir, domain)
            self.session_runtime_dir = os.path.join(self.runtime_dir, self.session)

    @property
    def session(self):
        return str(self.__session)
