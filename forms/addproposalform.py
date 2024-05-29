import datetime
from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, StringField, SelectField, BooleanField, DateField, Form, FormField, \
    FieldList
from wtforms.validators import DataRequired


class ParticipantForm(Form):
    username = StringField('Введите никнейм этого игрока',
                           validators=[DataRequired(message="Поле 'никнейм' не может быть пустым")])
    fullname = StringField('Введите ФИО этого игрока',
                           validators=[DataRequired(message="Поле 'ФИО' не может быть пустым")])
    gender = SelectField("Выберите пол данного игрока: ", choices=[("m", "Мужской"), ("w", "Женский")])
    birth_date = DateField('Введите дату рождения данного игрока')
    gto = StringField('Введите номер ГТО этого игрока',
                      validators=[DataRequired(message="Поле 'ГТО' не может быть пустым")])
    contact = StringField('Введите почту этого игрока',
                          validators=[DataRequired(message="Поле 'почта' не может быть пустым")])


class AddProposalForm(FlaskForm):
    team_name = StringField('Введите название команды',
                                validators=[DataRequired(message="Поле 'название команд' не может быть пустым")])
    participants = FieldList(FormField(ParticipantForm), min_entries=1, max_entries=1)

    submit = SubmitField('Добавить заявку')

