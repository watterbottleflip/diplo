import datetime
import json
import math

import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin

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

    def build_grid(self, participants):
        if not participants:
            return []

        normalized = []
        for participant in participants:
            if isinstance(participant, dict):
                name = participant.get("name") or participant.get("team_name") or "Команда"
                normalized.append({"name": name, "winner": None})
            else:
                normalized.append({"name": participant, "winner": None})

        if len(normalized) % 2 != 0:
            normalized.append({"name": "BYE", "winner": None})

        size = 1
        while size < len(normalized):
            size *= 2
        while len(normalized) < size:
            normalized.append({"name": "BYE", "winner": None})

        rounds = []
        current_round = list(normalized)
        total_rounds = int(math.log2(len(current_round)))

        for round_index in range(total_rounds):
            matches = []
            for match_index in range(0, len(current_round), 2):
                left = current_round[match_index]
                right = current_round[match_index + 1] if match_index + 1 < len(current_round) else {"name": "BYE", "winner": None}
                matches.append({
                    "label": f"Матч {match_index // 2 + 1}",
                    "left": {"name": left.get("name") or "BYE", "winner": None},
                    "right": {"name": right.get("name") or "BYE", "winner": None},
                    "winner": None,
                })

            if round_index == total_rounds - 1:
                round_name = "Финал"
            else:
                round_name = f"1/{2 ** (total_rounds - round_index)} финала"

            rounds.append({
                "name": round_name,
                "matches": matches,
            })

            current_round = [
                {"name": None, "winner": None}
                for _ in range(len(matches))
            ]

        self.grid = json.dumps({"grid": rounds})
        return rounds

    def update_grid_from_selection(self, rounds_data):
        if not rounds_data:
            return
        normalized = []
        for round_data in rounds_data:
            matches = []
            for match in round_data.get("matches", []):
                left = match.get("left") or {}
                right = match.get("right") or {}
                matches.append({
                    "label": match.get("label") or "Матч",
                    "left": {"name": left.get("name") or "BYE", "winner": None},
                    "right": {"name": right.get("name") or "BYE", "winner": None},
                    "winner": None,
                })
            normalized.append({
                "name": round_data.get("name") or "Раунд",
                "matches": matches,
            })
        self.grid = json.dumps({"grid": normalized})
        return normalized

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
