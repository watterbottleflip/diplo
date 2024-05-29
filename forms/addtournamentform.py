import datetime
from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, StringField, SelectField, BooleanField, DateField, RadioField
from wtforms.validators import DataRequired


class AddTournamentForm(FlaskForm):
    name = StringField('Введите название соревнования',
                       validators=[DataRequired(message="Поле 'название' не может быть пустым")])
    place = StringField('Введите место проведения соревнования',
                        validators=[DataRequired(message="Поле 'место' не может быть пустым")])
    organizer = StringField('Введите организатора соревнования',
                            validators=[DataRequired(message="Поле 'организатор' не может быть пустым")])
    discipline = StringField('Введите игру, по которой будет проводиться соревнование',
                             validators=[DataRequired(message="Поле 'дисциплина' не может быть пустым")])
    participants_amount = StringField('Введите колличество участников в одной команде',
                                      validators=[DataRequired(message="Данное поле не может быть пустым")])
    teams_amount = RadioField('Количество комманд',
                               choices = [(2, "2"), (4, "4"), (8, "8"), (16, "16"), (32, "32"), (64, "64")])
    registration_time = DateField('Введите дату начала регистрации'
                                  )
    start_time = DateField('Введите дату открытия соревнования'
                           )
    end_time = DateField('Введите дату окончания соревнования'
                         )
    closure_time = DateField('Введите дату закрытия соревнования'
                             )
    submit = SubmitField('Создать турнир')


    def get_deadlines(self):
        deadlines = {
            "registration": str(self.registration_time.data),
            "start": str(self.start_time.data),
            "end": str(self.end_time.data),
            "close": str(self.closure_time.data)
        }
        return deadlines
