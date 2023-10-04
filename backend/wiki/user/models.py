from typing import Optional

from sqlalchemy import Column, String, Uuid, Boolean
from uuid_extensions import uuid7

from wiki.database.core import Base


class User(Base):
    id = Column(Uuid, default=uuid7, primary_key=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=True)
    display_name = Column(String, nullable=True)

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    second_name = Column(String, nullable=True)

    is_deleted = Column(Boolean, nullable=False, default=False)
    is_trusted = Column(Boolean, nullable=False, default=False)

    def __init__(self,
                 email: str,
                 first_name: str,
                 last_name: str,
                 display_name: Optional[str] = None,
                 username: Optional[str] = None,
                 second_name: Optional[str] = None):
        self.email = email
        self.username = username
        self.display_name = display_name
        self.first_name = first_name
        self.last_name = last_name
        self.second_name = second_name
