# external imports
from chainqueue.sql.query import get_otx


class SessionIndex:

    def __init__(self, session_id):
        self.id = session_id


    def add(self, chain_spec, tx_hash, session=None):
        tx = get_otx(chain_spec, tx_hash, session=session)
        session.execute("INSERT INTO session (otx_id, session) VALUES ({},'{}')".format(tx['otx_id'], self.id))
        session.flush()


    def get(self, chain_spec, adapter, session=None, status=None, not_status=0, status_target=None, before=None):
        session = adapter.create_session(session=session)
        sql = "SELECT tx_hash, signed_tx FROM otx INNER JOIN tx_cache ON otx.id = tx_cache.otx_id WHERE otx.id IN ( SELECT otx_id FROM session where session='{}')".format(self.id)
        if status != None:
            if status_target == 0:
                sql += " AND status & {} > 0".format(status)
            else:
                if status_target == None:
                    status_target = status
                sql += " AND status & {} = {}".format(status, status_target)
        if not_status > 0:
            sql += " AND status & {} = 0".format(not_status)
        if before != None:
            sql += " AND tx_cache.date_checked < '{}'".format(before.isoformat())
        otxs = session.execute(sql)

        txs = {}
        for otx in otxs:
            txs[otx[0]] = otx[1]
        adapter.release_session(session)
        return txs
