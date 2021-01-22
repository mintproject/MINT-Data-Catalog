from contextlib import contextmanager
from dcat_service.settings import Settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

db = Settings.get_instance().database
# db_host = os.environ.get("DB_HOST"),
# db_port = os.environ.get("DB_PORT")
# db_username = os.environ.get("DB_USERNAME")
# db_password = os.environ.get("DB_PASSWORD")
# db_name = os.environ.get("DB_NAME")
if db.host == 'localhost':
    db.host = "host.docker.internal"

connection_string = f"postgresql+psycopg2://{db.user}:{db.password}@{db.host}:{db.port}/{db.db_name}"
engine = create_engine(connection_string, echo=False)
Session = sessionmaker(bind=engine, expire_on_commit=False)


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations"""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
