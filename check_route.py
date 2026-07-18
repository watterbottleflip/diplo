import main
from data.db_session import global_init


global_init('dbname.db')
app = main.app
app.testing = True
with app.test_client() as client:
    response = client.get('/tournament/1')
    print('status:', response.status_code)
    print(response.get_data(as_text=True)[:4000])
