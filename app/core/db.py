import importlib
import json
import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from app.core.config import settings

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    except:
        db.rollback()
        raise
    else:
        db.commit()
    finally:
        db.close()


def init_db(session: Session) -> None:
    if settings.ENVIRONMENT != "local":
        return None

    models_module = importlib.import_module("app.models")
    with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "initial_data.json")) as f:
        initial_data = json.load(f)

    for obj in initial_data:
        model_class = getattr(models_module, obj["model"])
        db_obj = session.query(model_class).filter(model_class.__mapper__.primary_key[0] == obj["pk"]).first()
        if db_obj:
            for key, value in obj["fields"].items():
                setattr(db_obj, key, value)
        else:
            db_obj = model_class(**{model_class.__mapper__.primary_key[0].name: obj["pk"]}, **obj["fields"])
            session.add(db_obj)
        session.commit()

    return None
