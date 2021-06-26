from sqlalchemy import create_engine, orm, engine

Base = orm.declarative_base()


def generate_engine(
    url: str,
) -> engine.Engine:
    engine = create_engine(url, echo=True)
    from .User import User
    from .Note import Note

    Base.metadata.create_all(engine)

    return engine
