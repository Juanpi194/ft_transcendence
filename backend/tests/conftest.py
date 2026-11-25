from typing import Generator

import pytest
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine, Base
from app import models  # noqa: F401

DATABASE_SUFFIX = '_test'


@pytest.fixture
def db() -> Generator[Session, None, None]:
    if (engine.url.database is None or
        not engine.url.database.endswith(DATABASE_SUFFIX)):
        pytest.fail("Database name used for tests must end with "
                    f"{DATABASE_SUFFIX}")
    Base.metadata.create_all(engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(engine)
