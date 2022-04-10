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
        save_config_path,
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
        self.config_dir = env.get('CONFINI_DIR', base_config_dir)
        if self.config_dir == None:
            save_config_path('chaind')
            self.config_dir = load_first_config('chaind')
        self.session_runtime_dir = os.path.join(self.runtime_dir, self.session)

        if domain:
            self.runtime_dir = os.path.join(self.runtime_dir, domain)
            os.makedirs(self.runtime_dir, exist_ok=True)
            self.data_dir = os.path.join(self.data_dir, domain)
            os.makedirs(self.data_dir, exist_ok=True)
            self.config_dir = os.path.join(self.config_dir, domain)
            os.makedirs(self.config_dir, exist_ok=True)
            self.session_runtime_dir = os.path.join(self.runtime_dir, self.session)
            os.makedirs(self.session_runtime_dir, exist_ok=True)

    @property
    def session(self):
        return str(self.__session)
