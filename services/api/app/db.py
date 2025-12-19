from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, create_engine

from app.core.config import settings

engine = create_engine(settings.database_url, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
