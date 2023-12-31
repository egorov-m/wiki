import re

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, declared_attr

from wiki.config import settings

engine: AsyncEngine = create_async_engine(url=settings.get_db_url(),
                                          pool_pre_ping=True,
                                          pool_size=settings.DB_POOL_SIZE,
                                          max_overflow=settings.DB_MAX_OVERFLOW)

get_session: sessionmaker = sessionmaker(engine, class_=AsyncSession)


def resolve_table_name(name):
    """Resolves table names to their mapped names."""
    names = re.split("(?=[A-Z])", name)
    return "_".join([x.lower() for x in names if x])


class CustomBase:
    @declared_attr
    def __tablename__(self):
        return resolve_table_name(self.__name__)


Base = declarative_base(cls=CustomBase)
