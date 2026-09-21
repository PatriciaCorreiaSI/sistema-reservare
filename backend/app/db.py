import os
from collections.abc import Iterator

from sqlalchemy import URL, create_engine
from sqlalchemy.orm import Session, sessionmaker


def url_do_ambiente() -> URL:
    POSTGRES_USER = os.environ["POSTGRES_USER"]
    POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]
    POSTGRES_DB = os.environ["POSTGRES_DB"]
    DB_HOST = os.environ["DB_HOST"]
    url = URL.create(
        drivername="postgresql+psycopg",
        username=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=DB_HOST,
        database=POSTGRES_DB,
    )

    return url


engine = create_engine(url_do_ambiente())
FabricaDeSessao = sessionmaker(bind=engine)


def obter_sessao() -> Iterator[Session]:
    sessao = FabricaDeSessao()
    try:
        yield sessao
        sessao.commit()
    except Exception:
        sessao.rollback()
        raise
    finally:
        sessao.close()
