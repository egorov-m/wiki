from datetime import datetime
from typing import Optional
from uuid import UUID

from wiki.models import WikiBase
from wiki.user.schemas import UserBaseInfoResponse


class VersionWorkspaceInfoResponse(WikiBase):
    id: UUID
    workspace_id: UUID
    committer_user: UserBaseInfoResponse
    branch: str
    created_at: datetime
    parent_version_workspace_id: Optional[UUID] = None


class VersionWorkspaceInfoGraphResponse(WikiBase):
    id: UUID
    workspace_id: UUID
    committer_user: UserBaseInfoResponse
    branch: str
    created_at: datetime
    parent_version_workspace: Optional["VersionWorkspaceInfoGraphResponse"] = None