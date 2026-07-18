import main
from data.db_session import global_init, create_session
from data.tournaments import Tournament

global_init('dbname.db')
sess = create_session()
print('tournaments count:', sess.query(Tournament).count())
for t in sess.query(Tournament).all():
    print(t.id, t.name)
