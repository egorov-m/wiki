from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, Uuid, String, DateTime, ForeignKey
from uuid_extensions import uuid7

from wiki.common.models import EnabledDeletedMixin
from wiki.database.core import Base
from wiki.wiki_api_client.enums import ResponsibilityType
from wiki.wiki_api_client.schemas import WikiApiClientInfoResponse


class WikiApiClient(Base, EnabledDeletedMixin):
    id = Column(Uuid, default=uuid7, primary_key=True, nullable=False)
    description = Column(String(256), nullable=True)
    responsibility = Column(String, nullable=False, default=str(ResponsibilityType.VIEWER))

    def __init__(self,
                 description: Optional[str] = None,
                 responsibility: ResponsibilityType = ResponsibilityType.VIEWER,
                 is_enabled: bool = True):
        self.description = description
        self.responsibility = str(responsibility)
        self.is_enabled = is_enabled

    def get_response_info(self):
        return WikiApiClientInfoResponse(
            id=self.id,
            description=self.description,
            responsibility=self.responsibility,
            is_enabled=self.is_enabled
        )


class WikiApiKey(Base, EnabledDeletedMixin):
    id = Column(Uuid, default=uuid7, primary_key=True, nullable=False)
    api_key_hash = Column(String(512), nullable=False, index=True, unique=True)
    api_key_prefix = Column(String(8), nullable=False)
    expires_date = Column(DateTime(timezone=True), nullable=False)

    owner_id = Column(ForeignKey("wiki_api_client.id"), nullable=False)

    def __init__(self,
                 api_key_hash: str,
                 api_key_prefix: str,
                 expires_date: datetime,
                 owner_id: UUID):
        self.api_key_hash = api_key_hash
        self.api_key_prefix = api_key_prefix
        self.expires_date = expires_date
        self.owner_id = owner_id
