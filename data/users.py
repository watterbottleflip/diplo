import datetime
import json
import sqlalchemy
from sqlalchemy import orm
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    username = sqlalchemy.Column(sqlalchemy.String,
                                 index=True, unique=True, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    proposals = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    tournaments = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    position = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    @property
    def access_level(self):
        level = {
            "user": 0,
            "judge": 1
        }
        return level[self.position]

    def make_new(self, username, email, password, position):
        self.username = username
        self.email = email
        self.set_password(password)
        self.position = position
        self.proposals = json.dumps({"proposals": []})
        self.tournaments = json.dumps({"tournaments": []})

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return self.password == password or check_password_hash(self.password, password)

    @property
    def proposals_list(self):
        return json.loads(self.proposals)['proposals']

    def add_proposal(self, proposal_id):
        proposal_list = self.proposals_list
        proposal_list.append(proposal_id)
        print(proposal_list)
        self.proposals = json.dumps({'proposals': proposal_list})

    def delete_proposal(self, proposal_id):
        proposal_list = self.proposals_list
        if proposal_id in proposal_list:
            proposal_list.remove(proposal_id)
        self.proposals = json.dumps({'proposals': proposal_list})

    @property
    def tournaments_list(self):
        return json.loads(self.tournaments)['tournaments']

    def add_tournament(self, tournament_id):
        tournaments_list = self.tournaments_list
        tournaments_list.append(tournament_id)
        self.tournaments = json.dumps({'tournaments': tournaments_list})

    def delete_tournament(self, tournament_id):
        tournament_list = self.tournaments_list
        if tournament_id in tournament_list:
            tournament_list.remove(tournament_id)
        self.tournaments = json.dumps({'tournaments': tournament_list})
