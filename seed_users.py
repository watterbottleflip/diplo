from data import db_session
from data.users import User


def seed_users():
    db_session.global_init("dbname.db")
    db_sess = db_session.create_session()

    existing = db_sess.query(User).filter(User.username.in_(["captain", "organizer"])).all()
    if existing:
        for user in existing:
            print(f"User already exists: {user.username}")
        return

    captain = User()
    captain.make_new(username="captain", email="captain@example.com", password="captain123", position="user")

    organizer = User()
    organizer.make_new(username="organizer", email="organizer@example.com", password="organizer123", position="judge")

    db_sess.add_all([captain, organizer])
    db_sess.commit()
    print("Seed users created successfully")


if __name__ == "__main__":
    seed_users()
