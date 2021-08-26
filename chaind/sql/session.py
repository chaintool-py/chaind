# external imports
from chainqueue.sql.query import get_tx

class SessionIndex:

    def __init__(self, session_id):
        self.id = session_id


    def add(self, chain_spec, tx_hash, session=None):
        tx = get_tx(chain_spec, tx_hash, session=session)
        session.execute("INSERT INTO session (otx_id, session) VALUES ({},'{}')".format(tx['otx_id'], self.id))
        session.flush()


    def get(self, chain_spec, adapter, session=None):
        session = adapter.create_session(session=session)
        otxs = session.execute("SELECT tx_hash, signed_tx FROM otx WHERE otx.id = ( SELECT otx_id FROM session where session='{}')".format(self.id))
        txs = {}
        for otx in otxs:
            txs[otx[0]] = otx[1]
        adapter.release_session(session)
        return txs
