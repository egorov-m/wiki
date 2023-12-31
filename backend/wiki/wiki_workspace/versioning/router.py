from difflib import ndiff
from io import StringIO
from uuid import UUID

from fastapi import APIRouter, Depends
from lakefs_client.client import LakeFSClient
from lakefs_client.exceptions import ServiceException
from lakefs_client.model.commit import Commit
from pydantic import constr
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from wiki.common.exceptions import WikiException, WikiErrorCode
from wiki.common.schemas import WikiUserHandlerData
from wiki.database.deps import get_db
from wiki.permissions.base import BasePermission
from wiki.permissions.object.enums import ObjectPermissionMode
from wiki.user.models import User
from wiki.user.repository import UserRepository
from wiki.wiki_api_client.enums import ResponsibilityType
from wiki.wiki_storage.deps import get_storage_client
from wiki.wiki_storage.schemas import CommitMetadataScheme
from wiki.wiki_storage.services.versioning import VersioningWikiStorageService
from wiki.wiki_workspace.block.model import Block
from wiki.wiki_workspace.block.repository import BlockRepository
from wiki.wiki_workspace.block.schemas import BlockDataResponse
from wiki.wiki_workspace.common import get_block_data_by_id, get_data_blocks
from wiki.wiki_workspace.document.model import Document
from wiki.wiki_workspace.document.repository import DocumentRepository
from wiki.wiki_workspace.repository import WorkspaceRepository
from wiki.wiki_workspace.versioning.schemas import (
    VersionBlockInfo,
    VersionDocumentInfo
)
from wiki.wiki_workspace.versioning.utils import (
    get_version_block_info_list,
    get_version_document_info_list
)


versioning_workspace_router = APIRouter()


@versioning_workspace_router.get(
    "/block/{block_id}/info",
    response_model=list[VersionBlockInfo],
    status_code=status.HTTP_200_OK,
    summary="Get info as a list of all versions block"
)
async def get_list_versions_document_block(
        block_id: UUID,
        session: AsyncSession = Depends(get_db),
        storage_client: LakeFSClient = Depends(get_storage_client),
        user: WikiUserHandlerData = Depends(BasePermission(responsibility=ResponsibilityType.VIEWER))
):
    block_repository: BlockRepository = BlockRepository(session)
    block: Block = await block_repository.get_block_with_permission_by_id(user.id, block_id)

    if (not user.wiki_api_client.responsibility == ResponsibilityType.ADMIN and
            ObjectPermissionMode(block.permission_mode) < ObjectPermissionMode.INACCESSIBLE):
        raise block_repository.block_not_found_exception

    document_repository: DocumentRepository = DocumentRepository(session)
    document: Document = await document_repository.get_document_by_id(block.document_id)
    document_ids = await document_repository.get_list_ids_of_document_hierarchy(document)

    storage_service: VersioningWikiStorageService = VersioningWikiStorageService(storage_client)
    resp = storage_service.get_version_document_block(document.workspace_id, document_ids, block_id)
    results: dict = resp["results"]
    return await get_version_block_info_list(results, block, session)


@versioning_workspace_router.post(
    "/block/{block_id}/rollback",
    response_model=BlockDataResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Rollback block contents to the specified version"
)
async def version_rollback_document_block(
        block_id: UUID,
        rollback_commit_id: constr(min_length=64, max_length=64),
        session: AsyncSession = Depends(get_db),
        storage_client: LakeFSClient = Depends(get_storage_client),
        user: WikiUserHandlerData = Depends(BasePermission(responsibility=ResponsibilityType.VIEWER))
):
    """
    ## Rollback block
    The state of the specified version of the block will be received,
    an update will be performed, and a commit will be performed (a new version will appear).
    """

    user_repository: UserRepository = UserRepository(session)
    user_db: User = await user_repository.get_user_by_id(user.id)

    block_repository: BlockRepository = BlockRepository(session)
    block = await block_repository.get_block_by_id(block_id)
    if (not user.wiki_api_client.responsibility == ResponsibilityType.ADMIN and
            ObjectPermissionMode(block.permission_mode) < ObjectPermissionMode.EDITING):
        raise block_repository.block_not_found_exception

    block_rollback_data = await get_block_data_by_id(session, block_id, storage_client, rollback_commit_id)

    document_repository: DocumentRepository = DocumentRepository(session)
    document = await document_repository.get_document_by_id(block.document_id)
    document_ids = await document_repository.get_list_ids_of_document_hierarchy(document)
    workspace_repository: WorkspaceRepository = WorkspaceRepository(session)
    workspace = await workspace_repository.get_workspace_by_id(document.workspace_id)

    storage_service: VersioningWikiStorageService = VersioningWikiStorageService(storage_client)
    storage_service.upload_document_block_in_workspace_storage(content=StringIO(block_rollback_data.content),
                                                               workspace_id=workspace.id,
                                                               document_ids=document_ids,
                                                               block_id=block.id)
    resp: Commit = storage_service.commit_workspace_document_version(document.workspace_id,
                                                                     document.id,
                                                                     CommitMetadataScheme(
                                                                         committer_user_id=str(user_db.id)))
    await block_repository.create_version_block(block, resp.id)

    return BlockDataResponse(
        id=block.id,
        document_id=block.document_id,
        position=block.position,
        type_block=block.type_block,
        content=block_rollback_data.content,
        created_at=block.created_at
    )


@versioning_workspace_router.post(
    "/document/{document_id}/rollback",
    response_model=list[BlockDataResponse],
    status_code=status.HTTP_202_ACCEPTED,
    summary="Rollback document contents to the specified version"
)
async def version_rollback_document(
        document_id: UUID,
        rollback_commit_id: constr(min_length=64, max_length=64),
        session: AsyncSession = Depends(get_db),
        storage_client: LakeFSClient = Depends(get_storage_client),
        user: WikiUserHandlerData = Depends(BasePermission(responsibility=ResponsibilityType.VIEWER))
):
    """
    ## Rollback document
    The state of the specified version of the document will be retrieved,
    all blocks will be updated, and a commit will be performed (a new version will appear).
    """

    user_repository: UserRepository = UserRepository(session)
    user_db: User = await user_repository.get_user_by_id(user.id)

    document_repository: DocumentRepository = DocumentRepository(session)
    document = await document_repository.get_document_by_id(document_id)

    if (not user.wiki_api_client.responsibility == ResponsibilityType.ADMIN and
            ObjectPermissionMode(document.permission_mode) < ObjectPermissionMode.EDITING):
        raise document_repository.document_not_found_exception

    rollback_data_blocks = await get_data_blocks(session,
                                                 user,
                                                 document_id,
                                                 rollback_commit_id,
                                                 storage_client)
    block_repository: BlockRepository = BlockRepository(session)
    rollback_blocks_ids = [item.id for item in rollback_data_blocks]
    blocks = await block_repository.get_all_block_by_document_id(document_id)

    document_ids = await document_repository.get_list_ids_of_document_hierarchy(document)
    workspace_repository: WorkspaceRepository = WorkspaceRepository(session)
    workspace = await workspace_repository.get_workspace_by_id(document.workspace_id)

    storage_service: VersioningWikiStorageService = VersioningWikiStorageService(storage_client)
    for item in rollback_data_blocks:
        storage_service.upload_document_block_in_workspace_storage(content=StringIO(item.content),
                                                                   workspace_id=workspace.id,
                                                                   document_ids=document_ids,
                                                                   block_id=item.id)

    # Hack, bad solution: Do a cleanup of these blocks that did not exist in the commit we are rolling back to
    for block in blocks:
        if not UUID(str(block.id)) in rollback_blocks_ids:
            storage_service.upload_document_block_in_workspace_storage(content=StringIO(""),
                                                                       workspace_id=workspace.id,
                                                                       document_ids=document_ids,
                                                                       block_id=block.id)

    try:
        resp: Commit = storage_service.commit_workspace_document_version(document.workspace_id,
                                                                         document.id,
                                                                         CommitMetadataScheme(
                                                                             committer_user_id=str(user_db.id)))
    except Exception:
        raise WikiException(
            message="The current state is identical to the one being rolled back to.",
            error_code=WikiErrorCode.VERSIONING_ROLLBACK_ERROR,
            http_status_code=status.HTTP_304_NOT_MODIFIED
        )

    # Block sets may vary from version to version.
    # When executing rollback, you need to restore and delete blocks.
    block_repository = BlockRepository(session)
    rollback_id_blocks = [item.id for item in rollback_data_blocks]
    current_blocks = await block_repository.get_all_block_by_document_id(document_id)
    for block in current_blocks:
        await block_repository.create_version_block(block, resp.id)

    current_id_blocks = [item.id for item in current_blocks]
    on_delete = set(current_id_blocks) - set(rollback_id_blocks)
    on_restore = set(rollback_id_blocks) - set(current_id_blocks)
    for i in on_delete:
        await block_repository.mark_block_deleted(i)
    for i in on_restore:
        await block_repository.mark_block_undeleted(i)
    # --------------------------------------------------------------------------------------

    return rollback_data_blocks


@versioning_workspace_router.get(
    "/block/{block_id}/diff",
    response_model=str,
    status_code=status.HTTP_200_OK,
    summary="Get the difference between the blocks"
)
async def get_diff_versions_document_block(
        block_id: UUID,
        commit_id_1: constr(min_length=64, max_length=64),
        commit_id_2: constr(min_length=64, max_length=64),
        session: AsyncSession = Depends(get_db),
        storage_client: LakeFSClient = Depends(get_storage_client),
        user: WikiUserHandlerData = Depends(BasePermission(responsibility=ResponsibilityType.VIEWER))
):
    """
    Find the difference between the contents of the block versions in diff format.
    """

    block_data_1 = await get_block_data_by_id(session, block_id, storage_client, commit_id_1)
    block_data_2 = await get_block_data_by_id(session, block_id, storage_client, commit_id_2)
    diff_list = ndiff(block_data_2.content.splitlines(), block_data_1.content.splitlines())
    diff = "\n".join(diff_list)

    return diff


@versioning_workspace_router.get(
    "/document/{document_id}/info",
    response_model=list[VersionDocumentInfo],
    status_code=status.HTTP_200_OK,
    summary="Get info as a list of all versions document"
)
async def get_list_versions_document(
        document_id: UUID,
        session: AsyncSession = Depends(get_db),
        storage_client: LakeFSClient = Depends(get_storage_client),
        user: WikiUserHandlerData = Depends(BasePermission(responsibility=ResponsibilityType.VIEWER))
):
    document_repository: DocumentRepository = DocumentRepository(session)
    document: Document = await document_repository.get_document_by_id(document_id)

    if (not user.wiki_api_client.responsibility == ResponsibilityType.ADMIN and
            ObjectPermissionMode(document.permission_mode) < ObjectPermissionMode.EDITING):
        raise document_repository.document_not_found_exception

    document_ids = await document_repository.get_list_ids_of_document_hierarchy(document)

    storage_service: VersioningWikiStorageService = VersioningWikiStorageService(storage_client)
    resp = storage_service.get_versions_document(document.workspace_id, document_ids)
    results: dict = resp["results"]
    return await get_version_document_info_list(results, document, session)
