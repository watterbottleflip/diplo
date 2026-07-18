import datetime
import unittest

import main
from data.participants import Participant
from data.proposals import Proposal
from data.users import User


class DummySession:
    def query(self, model):
        return self

    def get(self, entity_id):
        return {"id": entity_id}


class MainHelperTests(unittest.TestCase):
    def test_get_proposal_accepts_session_argument(self):
        self.assertEqual(main.get_proposal(7, DummySession()), {"id": 7})

    def test_get_tournament_accepts_session_argument(self):
        self.assertEqual(main.get_tournament(11, DummySession()), {"id": 11})

    def test_proposal_participants_list_handles_empty_data(self):
        proposal = Proposal()
        proposal.participants = None
        self.assertEqual(proposal.participants_list, [])

    def test_user_lists_handle_empty_data(self):
        user = User()
        user.proposals = None
        user.tournaments = None
        self.assertEqual(user.proposals_list, [])
        self.assertEqual(user.tournaments_list, [])

    def test_birth_date_normalization(self):
        participant = Participant()
        self.assertEqual(participant.normalize_birth_date(datetime.date(2000, 5, 6)), "2000-05-06")
        self.assertEqual(participant.normalize_birth_date("2001-07-08"), "2001-07-08")


if __name__ == "__main__":
    unittest.main()
