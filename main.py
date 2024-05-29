import json
import os
from flask import Flask, render_template, redirect, abort, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import Flask, render_template
import pandas as pd

from data.db_session import create_session
from data.users import User
from data.proposals import Proposal
from data.participants import Participant
from data.tournaments import Tournament
from data import db_session
from utils import get_proposal, get_tournament
from email_sender import send_email
# from email_sender import send_email
from forms.loginform import LoginForm, RegistrationForm
from forms.addtournamentform import AddTournamentForm
from forms.addproposalform import AddProposalForm
from tables import deadlines

app = Flask(__name__)
app.config['SECRET_KEY'] = 'abcdef'
app.config['JSON_AS_ASCII'] = False
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def get_proposal(proposal_id):
    db_sess = db_session.create_session()
    curr_proposal = db_sess.query(Proposal).filter(Proposal.id == proposal_id).first()
    return curr_proposal


def get_tournament(tournament_id):
    db_sess = db_session.create_session()
    curr_tournament = db_sess.query(Tournament).filter(Tournament.id == tournament_id).first()
    return curr_tournament


def get_participant(participant_id):
    db_sess = db_session.create_session()
    curr_participant = db_sess.query(Participant).filter(Participant.id == participant_id).first()
    return curr_participant


def export_tournament_data(tournament_id):
    pass


@app.errorhandler(404)
def not_found(error):
    return "Страница не найдена", 404


@app.errorhandler(401)
def unauthorized_access(error):
    return redirect('/login')


@app.route("/")
def index():
    db_sess = db_session.create_session()
    tournaments = []
    for tournament in db_sess.query(Tournament).all():
        tournaments.append({
            "name" : tournament.name,
            "id" : tournament.id
        })
    return render_template("main page.html", title="Главная страница",
                           tournaments = tournaments,
                           is_empty = len(tournaments) == 0)


@app.route("/login", methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    register_form = RegistrationForm()

    if register_form.validate_on_submit():
        if register_form.password.data != register_form.password_again.data:
            flash("Пароли не совпадают, повторите попытку регистрации", "error")
            # return "Пароли не совпадают"
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == register_form.email.data).first() or db_sess.query(User).filter(
                User.username == register_form.login.data).first():
            flash("Такой пользователь уже существует", "error")

        user = User()
        user.make_new(username=register_form.login.data, email=register_form.email.data,
                      password=register_form.password.data, position=register_form.position.data)

        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')

    if login_form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(
            (User.email == login_form.login_or_email.data) or (User.username == login_form.login_or_email.data)).first()
        if user and user.check_password(login_form.password.data):
            login_user(user, remember=login_form.remember_me.data)
            return redirect("/")
        flash("Неправильный логин или пароль", "error")

    return render_template('login.html', title='Авторизация', login_form=login_form, register_form=register_form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/account', methods=["POST", "GET"])
@login_required
def account():
    if current_user.access_level == 0:
        db_sess = db_session.create_session()
        my_proposals_ids = current_user.proposals_list
        my_proposals = []
        for proposal_id in my_proposals_ids:
            current_proposal = db_sess.query(Proposal).filter(Proposal.id == proposal_id).first()
            tournament = db_sess.query(Tournament).filter(Tournament.id == current_proposal.tournament_id).first()
            participants = []
            for participant_id in current_proposal.participants_list:
                participant = get_participant(participant_id)
                participants.append(participant.username)
            proposal = {
                "tournament_name": tournament.name,
                "team": participants,
                "status": current_proposal.status
            }
            my_proposals.append(proposal)

        tournaments = []
        for tournament in db_sess.query(Tournament).all():
            tournaments.append({
                "name" : tournament.name,
                "id" : tournament.id
            })
        return render_template('index-leader.html',
                               proposals=my_proposals,
                               is_empty=len(my_proposals) == 0,
                               tournaments = tournaments,
                               is_empty_tournaments = len(tournaments) == 0)
    else:
        db_sess = db_session.create_session()
        my_tournaments_ids = current_user.tournaments_list
        my_tournaments = []
        my_proposals = []
        not_confirmed_proposals = []
        for tournament_id in my_tournaments_ids:
            current_tournament = db_sess.query(Tournament).filter(Tournament.id == tournament_id).first()
            current_tournament.update_status()
            proposal_amount = db_sess.query(Proposal).filter(
                Proposal.tournament_id == tournament_id and Proposal.status).count()
            for proposal in db_sess.query(Proposal).filter(Proposal.tournament_id == tournament_id).all():
                if not proposal.status:
                    not_confirmed_proposals.append(proposal.id)
            tournament = {
                "tournament_name": current_tournament.name,
                "proposals_amount": proposal_amount,
                "proposals_need": current_tournament.teams_amount,
                "tournament_status": deadlines[current_tournament.status],
                "date": current_tournament.get_start_date
            }
            my_tournaments.append(tournament)
        for proposal_id in not_confirmed_proposals:
            current_proposal = get_proposal(proposal_id)
            current_tournament = get_tournament(current_proposal.tournament_id)
            proposal = {
                "proposal_id": current_proposal.id,
                "team_name": current_proposal.team_name,
                "tournament_name": current_tournament.name
            }
            my_proposals.append(proposal)
        return render_template('index-judge.html',
                               tournaments=my_tournaments,
                               proposals=my_proposals,
                               is_empty_tournamnets=len(my_tournaments) == 0,
                               is_empty_proposals=len(my_proposals) == 0)


@app.route("/approve_proposal/<int:proposal_id>", methods=["POST", "GET"])
@login_required
def approve_proposal(proposal_id):
    if current_user.access_level == 0:
        return render_template("error.html", message="Вы не имеете таких прав доступа")

    db_sess = create_session()
    proposal = get_proposal(proposal_id, db_sess)

    if not proposal:
        return render_template("error.html", message="Заявка не найдена")

    proposal.approve_proposal()
    db_sess.commit()

    tournament = get_tournament(proposal.tournament_id, db_sess)
    if not tournament:
        return render_template("error.html", message="Турнир не найден")

    tournament_name = tournament.name
    for participant_id in proposal.participants_list:
        send_email(
            participant_id,
            f"""Мы рады сообщить, что заявка вашей команды - {proposal.team_name} одобрена и вы допущены до участия в соревновании '{tournament_name}'"""
        )

    return redirect("/account")


@app.route('/add_proposal/<int:tournament_id>', methods=["POST", "GET"])
@login_required
def add_proposal(tournament_id):
    if current_user.access_level == 1:
        return "Вы не можете подавать заявки на турниры"
    else:
        form = AddProposalForm()
        tournament = get_tournament(tournament_id)
        participants_ids = []
        proposal = Proposal()
        if form.validate_on_submit():
            print(True)
            db_sess = db_session.create_session()
            for part in form.participants:
                participant = Participant()
                participant.make_new(username=part.username.data,
                                     fullname=part.fullname.data, gender=part.gender.data,
                                     birth_date=str(part.birth_date.data), gto=part.gto.data,
                                     contact=part.contact.data)
                db_sess.add(participant)
                db_sess.commit()
                participants_ids.append(participant.id)
            proposal.make_new(team_id=current_user.id,
                              team_name=form.team_name.data, tournament_id=tournament_id)
            db_sess.add(proposal)
            db_sess.commit()

            user = db_sess.query(User).filter(User.id == current_user.id).first()
            user.add_proposal(proposal.id)
            db_sess.commit()

            for participant_id in participants_ids:
                proposal.add_participant(participant_id)
                db_sess.commit()

            return redirect('/account')

    return render_template('add_proposal.html', form=form, tournament_name=tournament.name)


@app.route('/edit_proposal/<int:proposal_id>', methods=["POST", "GET"])
@login_required
def edit_proposal(proposal_id):
    db_sess = db_session.create_session()
    proposal = db_sess.query(Proposal).filter(Proposal.id == proposal_id).first()
    data = {
        "id": [],
        "username": [],
        "fullname": [],
        "gender": [],
        "birth_date": [],
        "gto": [],
        "contact": []
    }
    for participant_id in proposal.participants_list:
        participant = get_participant(participant_id)
        data["id"].append(participant_id)
        data["username"].append(participant.username)
        data["fullname"].append(participant.fullname)
        data["gender"].append(participant.gender)
        data["birth_date"].append(participant.birth_date)
        data["gto"].append(participant.gto)
        data["contact"].append(participant.contact)

    if proposal:
        form = AddProposalForm()
        tournament = get_tournament(proposal.tournament_id)
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            for i in range(tournament.participants_amount):
                participant = get_participant(data["id"][i])
                participant.update(username=form.username[i].data,
                                   fullname=form.fullname[i].data, gender=form.gender[i].data,
                                   birth_date=form.birth_date[i].data, gto=form.gto[i].data,
                                   contact=form.contact[i].data)
            db_sess.commit()
    else:
        abort(404)

    return render_template('edit_proposal.html', form=form, data=data)


@app.route(rule='/delete_proposal/<int:proposal_id>', methods=["POST", "GET"])
@login_required
def delete_proposal(proposal_id):
    db_sess = create_session()
    proposal = get_proposal(proposal_id)

    if proposal:
        try:
            participants_ids = proposal.participants
            print(f"Тип participants_ids: {type(participants_ids)}")
            print(f"Значение participants_ids: {participants_ids}")

            # Ensure participants_ids is a list or iterable of integers
            if not isinstance(participants_ids, list):
                raise ValueError("participants_ids should be a list")
            for participant_id in participants_ids:
                if not isinstance(participants_ids, int):
                    raise ValueError(f"participant_id {participant_id} is not an integer")

                participant = get_participant(participant_id)
                if participant:
                    db_sess.delete(participant)
                else:
                    print(f"Участник с id {participant_id} не найден")

            user = db_sess.query(User).filter(User.id == proposal.team_id).first()
            if user:
                user.delete_proposal(proposal_id)
                db_sess.delete(proposal)
                db_sess.commit()
            else:
                print(f"Пользователь с id {proposal.team_id} не найден")
                abort(404)
        except Exception as e:
            print(f"Ошибка при удалении предложения: {e}")
            db_sess.rollback()
            abort(500)
    else:
        print(f"Предложение с id {proposal_id} не найдено")
        abort(404)

    return redirect('/account')


# Предполагая, что функции get_proposal и get_participant определены где-то в вашем коде

def get_proposal(proposal_id):
    # Пример функции для получения предложения
    db_sess = create_session()
    proposal = db_sess.query(Proposal).filter(Proposal.id == proposal_id).first()
    return proposal


def get_participant(participant_id):
    # Пример функции для получения участника
    db_sess = create_session()
    participant = db_sess.query(Participant).filter(Participant.id == participant_id).first()
    return participant


@app.route('/add_tournament', methods=["POST", "GET"])
@login_required
def add_new_tournament():
    if current_user.access_level == 0:
        return "Недостаточно прав доступа для проведения турнира"
    else:
        form = AddTournamentForm()

        if form.validate_on_submit():
            db_sess = db_session.create_session()
            new_tournament = Tournament()

            new_tournament.make_new(name=form.name.data, place=form.place.data,
                                    organizer=form.organizer.data, discipline=form.discipline.data,
                                    deadlines=form.get_deadlines(),
                                    participants_amount=form.participants_amount.data,
                                    teams_amount=form.teams_amount.data)
            db_sess.add(new_tournament)
            db_sess.commit()

            user = db_sess.query(User).filter(User.id == current_user.id).first()
            user.add_tournament(new_tournament.id)
            db_sess.commit()

            return redirect("/account")

    return render_template("add_tournament.html",
                           form=form)


@app.route('/edit_tournament/<int:tournament_id>', methods=["POST", "GET"])
@login_required
def edit_tournament(tournament_id):
    db_sess = db_session.create_session()
    tournament = db_sess.query(Tournament).filter(Tournament.id == tournament_id).first()
    if tournament:
        form = AddTournamentForm()
        if form.validate_on_submit():
            tournament.edit(name=form.name.data, place=form.place.data,
                            organizer=form.organizer.data, discipline=form.discipline.data,
                            deadlines=form.get_deadlines,
                            participants_amount=form.participants_amount.data)
            db_sess.commit()
    else:
        abort(404)
    return render_template("edit_tournament.html", form=form, tournament=tournament, user=current_user)


@app.route('/delete_tournament/<int:tournament_id>', methods=["POST", "GET"])
@login_required
def delete_tournament(tournament_id):
    db_sess = db_session.create_session()
    tournament = db_sess.query(Tournament).filter(Tournament.id == tournament_id).first()
    if tournament:
        db_sess.delete(tournament)
        if tournament_id in current_user.tournament_list():
            current_user.delete_tournament(tournament_id)
        for proposal in db_sess.query(Proposal).filter(Proposal.tournament_id == tournament_id).all():
            for participant_id in proposal.participants_list:
                participant = get_participant(participant_id)
                db_sess.delete(participant)
            user = db_sess.query(User).filter(User.id == proposal.team_id).first()
            user.delete_proposal(proposal.id)
            db_sess.delete(proposal)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/account')


@app.route('/tournament/<int:tournament_id>', methods=["GET", "POST"])
def tournament_page(tournament_id):
    current_tournament = get_tournament(tournament_id)
    if not current_tournament:
        abort(404)
    else:
        tournament = {
            "name" : current_tournament.name,
            "discipline" : current_tournament.discipline,
            "place" : current_tournament.place,
            "organizer" : current_tournament.organizer,
            "registration" : json.loads(current_tournament.deadlines)["deadlines"]["registration"],
            "start" : json.loads(current_tournament.deadlines)["deadlines"]["start"],
            "end" : json.loads(current_tournament.deadlines)["deadlines"]["end"],
            "close" : json.loads(current_tournament.deadlines)["deadlines"]["close"]
        }
    return render_template("tournament.html", tournament = tournament)


if __name__ == "__main__":
    db_session.global_init(db_file="postgres.db")
    app.debug = True
    app.run()
