# SPDX-License-Identifier: GPL-3.0-or-later

# standard imports
import os
import logging
import sys
import argparse

# external imports
from hexathon import add_0x
from chaind import Environment
import chainlib.cli
from chainlib.chain import ChainSpec
from chainqueue.db import dsn_from_config
from chainqueue.sql.backend import SQLBackend
from chaind.sql.session import SessionIndex
from chainqueue.adapters.sessionindex import SessionIndexAdapter
from chainqueue.cli import Outputter
from chainqueue.enum import (
        StatusBits,
        all_errors,
        )


logging.basicConfig(level=logging.WARNING)
logg = logging.getLogger()

script_dir = os.path.dirname(os.path.realpath(__file__)) 
config_dir = os.path.join(script_dir, '..', 'data', 'config')

arg_flags = chainlib.cli.argflag_std_base | chainlib.cli.Flag.CHAIN_SPEC
argparser = chainlib.cli.ArgumentParser(
    arg_flags,
    description="""Lists and queue items by session id, filterable by timestamp and state.

By default all columns will be displayed. Columns can be explicitly selected instead by passing one or more column names using the -o,--column flag. Valid column names are: chainspec, hash, statustext, statuscode.
""")
argparser.add_argument('--backend', type=str, default='sql', help='Backend to use (currently only "sql")')
argparser.add_argument('--start', type=str, help='Oldest transaction hash to include in results')
argparser.add_argument('--end', type=str, help='Newest transaction hash to include in results')
argparser.add_argument('--error', action='store_true', help='Only show transactions which have error state')
argparser.add_argument('--pending', action='store_true', help='Omit finalized transactions')
argparser.add_argument('--status-mask', type=int, dest='status_mask', help='Manually specify status bitmask value to match (overrides --error and --pending)')
argparser.add_argument('--summary', action='store_true', help='output summary for each status category')
argparser.add_argument('--address', dest='address', type=str, help='filter by address')
argparser.add_argument('-o', '--column', dest='column', action='append', type=str, help='add a column to display')
argparser.add_positional('session_id', type=str, help='Ethereum address of recipient')
args = argparser.parse_args()
extra_args = {
    'address': None,
    'backend': None,
    'start': None,
    'end': None,
    'error': None,
    'pending': None,
    'status_mask': None,
    'summary': None,
    'column': None,
    'session_id': 'SESSION_ID',
        }

env = Environment(domain='eth', env=os.environ)

config = chainlib.cli.Config.from_args(args, arg_flags, extra_args=extra_args, base_config_dir=config_dir)

if config.get('SESSION_DATA_DIR') == None:
    config.add(env.data_dir, 'SESSION_DATA_DIR', exists_ok=True)

chain_spec = ChainSpec.from_chain_str(config.get('CHAIN_SPEC'))

status_mask = config.get('_STATUS_MASK', None)
not_status_mask = None
if status_mask == None:
    if config.get('_ERROR'):
        status_mask = all_errors()
    if config.get('_PENDING'):
        not_status_mask = StatusBits.FINAL

tx_getter = None
session_method = None
if config.get('_BACKEND') == 'sql':
    from chainqueue.sql.query import get_tx_cache as tx_getter
    from chainqueue.runnable.sql import setup_backend
    from chainqueue.db.models.base import SessionBase
    setup_backend(config, debug=config.true('DATABASE_DEBUG'))
    session_method = SessionBase.create_session
else:
    raise NotImplementedError('backend {} not implemented'.format(config.get('_BACKEND')))

if config.get('DATABASE_ENGINE') == 'sqlite':
    config.add(os.path.join(config.get('SESSION_DATA_DIR'), config.get('DATABASE_NAME') + '.sqlite'), 'DATABASE_NAME', exists_ok=True)
 
dsn = dsn_from_config(config)
backend = SQLBackend(dsn, debug=config.true('DATABASE_DEBUG'))
session_index_backend = SessionIndex(config.get('SESSION_ID'))
adapter = SessionIndexAdapter(backend, session_index_backend=session_index_backend)
output_cols = config.get('_COLUMN')

def main():
   outputter = Outputter(chain_spec, sys.stdout, tx_getter, session_method=session_method, decode_status=config.true('_RAW'), cols=output_cols)
   txs = session_index_backend.get(chain_spec, adapter)
   if config.get('_SUMMARY'):
        for k in txs.keys():
            outputter.add(k)
        outputter.decode_summary()
   else:
        for k in txs.keys():
            outputter.decode_single(k)


if __name__ == '__main__':
    main()
