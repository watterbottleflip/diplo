import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
import json
from .db_session import SqlAlchemyBase


class Tournament(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'tournaments'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String,
                             index=True, unique=True, nullable=True)
    place = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    organizer = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    discipline = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    participants_amount = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    teams_amount = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    deadlines = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    judges = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    participants = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    grid = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    results = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    status = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    def make_new(self, name, place, organizer, discipline, deadlines, participants_amount, teams_amount):
        self.name = name
        self.place = place
        self.organizer = organizer
        self.discipline = discipline
        self.deadlines = json.dumps({"deadlines": deadlines})
        self.participants_amount = participants_amount
        self.teams_amount = teams_amount
        self.status = 0
        self.grid = json.dumps({"grid": []})

    def add_results(self, results):
        self.results = results

    @property
    def get_start_date(self):
        date = json.loads(self.deadlines)["deadlines"]["start"]
        return str(date).split()[0].split("-")[::-1]

    def update_status(self):
        status = json.loads(self.deadlines)['deadlines']
        if datetime.datetime.today() > datetime.datetime.strptime(status["registration"], "%Y-%m-%d"):
            self.status = 1
        if datetime.datetime.today() > datetime.datetime.strptime(status["start"], "%Y-%m-%d"):
            self.status = 2
        if datetime.datetime.today() > datetime.datetime.strptime(status["end"], "%Y-%m-%d"):
            self.status = 3
        if datetime.datetime.today() > datetime.datetime.strptime(status["close"], "%Y-%m-%d"):
            self.status = 4

    def delete(self, session):
        session.delete(self)
        session.commit()

    def edit(self, name, place, organizer, discipline, deadlines, participants_amount, teams_amount):
        self.name = name
        self.place = place
        self.organizer = organizer
        self.discipline = discipline
        self.deadlines = deadlines
        self.participants_amount = participants_amount
        self.teams_amount = teams_amount
        self.status = 0
