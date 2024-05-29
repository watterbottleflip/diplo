from data.db_session import create_session
from data.participants import Participant
from data.proposals import Proposal
from data.tournaments import Tournament


def get_proposal(proposal_id, db_sess):
    return db_sess.query(Proposal).get(proposal_id)


def get_tournament(tournament_id, db_sess):
    return db_sess.query(Tournament).get(tournament_id)


def get_participant(participant_id):
    db_sess = create_session()
    return db_sess.query(Participant).get(participant_id)
