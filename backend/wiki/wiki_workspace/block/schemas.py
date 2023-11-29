from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import constr

from wiki.models import WikiBase
from wiki.wiki_workspace.block.model import TypeBlock


class CreateBlock(WikiBase):
    document_id: UUID
    position: int
    type_block: TypeBlock


class UpdateBlockInfo(WikiBase):
    block_id: UUID
    position: Optional[int] = None


class UpdateBlockData(WikiBase):
    block_id: UUID
    type_block: TypeBlock
    content: str  # WYSIWYG


class BlockInfoResponse(WikiBase):
    id: UUID
    document_id: UUID
    position: int
    type_block: TypeBlock
    created_at: datetime


class BlockDataResponse(BlockInfoResponse):
    content: str  # WYSIWYG
    link: Optional[str] = None
