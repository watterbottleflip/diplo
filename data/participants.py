import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Participant(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = "participants"

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    username = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    fullname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    gender = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    birth_date = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    gto = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    contact = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    def make_new(self, username, fullname, gender, birth_date, gto, contact):
        self.username = username
        self.fullname = fullname
        self.gender = gender
        self.birth_date = birth_date
        self.gto = gto
        self.contact = contact

    def update(self, username, fullname, gender, birth_date, gto, contact):
        self.username = username
        self.fullname = fullname
        self.gender = gender
        self.birth_date = birth_date
        self.gto = gto
        self.contact = contact