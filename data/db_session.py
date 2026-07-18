import os
import sqlalchemy as sa
import sqlalchemy.ext.declarative as dec
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session

SqlAlchemyBase = orm.declarative_base()

__factory = None


def global_init(db_file):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    if db_file.startswith("postgresql") or db_file.startswith("postgres"):
        conn_str = db_file
    elif "://" in db_file:
        conn_str = db_file
    else:
        conn_str = f"sqlite:///{os.path.abspath(db_file)}"

    print(f"Подключение к базе данных по адресу {conn_str}")

    engine = sa.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    if __factory is None:
        raise RuntimeError("База данных не инициализирована. Вызовите global_init() перед созданием сессии.")
    return __factory()
