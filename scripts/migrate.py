#!/usr/bin/python
import os
import argparse
import logging

# external imports
import alembic
from alembic.config import Config as AlembicConfig
import confini
import chainqueue.db
import chainsyncer.db

# local imports
from chaind import Environment

logging.basicConfig(level=logging.WARNING)
logg = logging.getLogger()

rootdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
dbdir = os.path.join(rootdir, 'chaind', 'db')
configdir = os.path.join(rootdir, 'chaind', 'data', 'config')
default_migrations_dir = os.path.join(dbdir, 'migrations')

env = Environment(env=os.environ)

argparser = argparse.ArgumentParser()
argparser.add_argument('-c', type=str, default=env.config_dir, help='config directory')
argparser.add_argument('--env-prefix', default=os.environ.get('CONFINI_ENV_PREFIX'), dest='env_prefix', type=str, help='environment prefix for variables to overwrite configuration')
argparser.add_argument('--data-dir', dest='data_dir', type=str, help='data directory')
argparser.add_argument('--migrations-dir', dest='migrations_dir', default=default_migrations_dir, type=str, help='path to alembic migrations directory')
argparser.add_argument('--reset', action='store_true', help='reset exsting database')
argparser.add_argument('-v', action='store_true', help='be verbose')
argparser.add_argument('-vv', action='store_true', help='be more verbose')
args = argparser.parse_args()

if args.vv:
    logging.getLogger().setLevel(logging.DEBUG)
elif args.v:
    logging.getLogger().setLevel(logging.INFO)

# process config
logg.debug('loading config from {}'.format(args.c))
config = confini.Config(configdir, args.env_prefix, override_dirs=[args.c])
config.process()
args_override = {
            'SESSION_DATA_DIR': getattr(args, 'data_dir'),
        }
config.dict_override(args_override, 'cli args')

if config.get('DATABASE_ENGINE') == 'sqlite':
    config.add(os.path.join(config.get('SESSION_DATA_DIR'), config.get('DATABASE_NAME') + '.sqlite'), 'DATABASE_NAME', True)
 
config.censor('PASSWORD', 'DATABASE')

logg.debug('config loaded:\n{}'.format(config))
config.add(os.path.join(args.migrations_dir, config.get('DATABASE_ENGINE')), '_MIGRATIONS_DIR', True)
if not os.path.isdir(config.get('_MIGRATIONS_DIR')):
    logg.debug('migrations dir for engine {} not found, reverting to default'.format(config.get('DATABASE_ENGINE')))
    config.add(os.path.join(args.migrations_dir, 'default'), '_MIGRATIONS_DIR', True)

os.makedirs(config.get('SESSION_DATA_DIR'), exist_ok=True)

dsn = chainqueue.db.dsn_from_config(config)

def main():
    logg.info('using migrations dir {}'.format(config.get('_MIGRATIONS_DIR')))
    logg.info('using db {}'.format(dsn))
    ac = AlembicConfig(os.path.join(config.get('_MIGRATIONS_DIR'), 'alembic.ini'))
    ac.set_main_option('sqlalchemy.url', dsn)
    ac.set_main_option('script_location', config.get('_MIGRATIONS_DIR'))

    if args.reset:
        logg.debug('reset is set, purging existing content')
        alembic.command.downgrade(ac, 'base')

    alembic.command.upgrade(ac, 'head')


if __name__ == '__main__':
    main()
