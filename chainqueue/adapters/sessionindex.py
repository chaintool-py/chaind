# standard imports
import datetime

# external imports
from hexathon import add_0x
from chainqueue.adapters.base import Adapter
from chainqueue.enum import StatusBits


class SessionIndexAdapter(Adapter):

    def __init__(self, backend, session_index_backend=None, pending_retry_threshold=0, error_retry_threshold=0):
        super(SessionIndexAdapter, self).__init__(backend, pending_retry_threshold=pending_retry_threshold, error_retry_threshold=error_retry_threshold)
        self.session_index_backend = session_index_backend


    def add(self, bytecode, chain_spec, session=None):
        tx = self.translate(bytecode, chain_spec)
        r = self.backend.create(chain_spec, tx['nonce'], tx['from'], tx['hash'], add_0x(bytecode.hex()), session=session)
        if r:
            session.rollback()
            session.close()
            return None
        r = self.backend.cache(tx, session=session)
        if self.session_index_backend != None:
            session.flush()
            self.session_index_backend.add(chain_spec, tx['hash'], session=session)
        session.commit()
        return tx['hash']


    def upcoming(self, chain_spec, session=None):
        txs = self.backend.get(chain_spec, self.translate, session=session, status=StatusBits.QUEUED, not_status=StatusBits.IN_NETWORK)
        before = datetime.datetime.utcnow() - self.error_retry_threshold
        errored_txs = self.backend.get(chain_spec, self.translate, session=session, status=StatusBits.LOCAL_ERROR, not_status=StatusBits.FINAL, before=before, requeue=True)
        for tx_hash in errored_txs.keys():
            txs[tx_hash] = errored_txs[tx_hash]
        return txs



