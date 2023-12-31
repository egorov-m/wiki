from fastapi import APIRouter, Depends
from fastapi_pagination import Page, paginate
from fastapi_pagination.utils import disable_installed_extensions_check
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from wiki.common.schemas import BaseResponse, WikiUserHandlerData
from wiki.database.deps import get_db
from wiki.permissions.base import BasePermission
from wiki.user.models import User
from wiki.user.repository import UserRepository
from wiki.user.schemas import (
    UserFullInfoResponse,
    UserIdentifiers,
    UserUpdate,
    CreateVerifiedUser,
    CreateUser,
    UserFilter
)
from wiki.user.utils import get_user_info, get_user_db_by_user_identifiers
from wiki.wiki_api_client.enums import ResponsibilityType
from wiki.wiki_api_client.models import WikiApiClient
from wiki.wiki_api_client.repository import WikiApiClientRepository
from wiki.wiki_api_client.schemas import CreateWikiApiClient

user_router = APIRouter()
disable_installed_extensions_check()


@user_router.post(
    "/verified",
    response_model=UserFullInfoResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Create a verified user (has access to the system)"
)
async def create_verified_user(
        create_user: CreateVerifiedUser,
        user: WikiUserHandlerData = Depends(BasePermission(responsibility=ResponsibilityType.ADMIN)),
        session: AsyncSession = Depends(get_db)
):
    user_repository: UserRepository = UserRepository(session)
    api_client_repository: WikiApiClientRepository = WikiApiClientRepository(session)
    user_db = await user_repository.create_user(CreateUser(
        email=create_user.email,
        username=create_user.username,
        first_name=create_user.first_name,
        last_name=create_user.last_name,
        second_name=create_user.second_name,
        position=create_user.position,
        is_user_agreement_accepted=create_user.is_user_agreement_accepted))
    api_client_db: WikiApiClient = await api_client_repository.create_wiki_api_client(CreateWikiApiClient(
        description=create_user.wiki_api_client.description,
        responsibility=create_user.wiki_api_client.responsibility,
        is_enabled=create_user.wiki_api_client.is_enabled
    ))
    updated_user: user = await user_repository.update_user(user_db.id,
                                                           is_verified_email=create_user.is_verified_email,
                                                           is_enabled=create_user.is_enabled,
                                                           wiki_api_client_id=api_client_db.id)
    return await get_user_info(updated_user, session)


@user_router.get(
    "/me",
    response_model=UserFullInfoResponse,
    status_code=status.HTTP_200_OK,
    summary="Get info about the current user",
)
async def get_me(
        user: WikiUserHandlerData = Depends(BasePermission(is_available_disapproved_user=True,
                                                           responsibility=ResponsibilityType.VIEWER)),
        session: AsyncSession = Depends(get_db)
):
    user_repository: UserRepository = UserRepository(session)
    user_db: User = await user_repository.get_user_by_id(user.id)
    return await get_user_info(user_db, session)


@user_router.get(
    "/info",
    response_model=UserFullInfoResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user by id or username or email"
)
async def get_user(
        user: WikiUserHandlerData = Depends(BasePermission(responsibility=ResponsibilityType.ADMIN)),
        session: AsyncSession = Depends(get_db),
        user_identifiers: UserIdentifiers = Depends()
):
    user_repository: UserRepository = UserRepository(session)
    user_db = await get_user_db_by_user_identifiers(user_identifiers, user_repository)

    return await get_user_info(user_db, session)


@user_router.get(
    "/all",
    response_model=Page[UserFullInfoResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all users"
)
async def get_users(
        filter_user: UserFilter = Depends(UserFilter),
        user: WikiUserHandlerData = Depends(BasePermission(responsibility=ResponsibilityType.ADMIN)),
        session: AsyncSession = Depends(get_db)
):
    user_repository: UserRepository = UserRepository(session)
    users: list[User] = await user_repository.get_all_users_filter(filter_user)

    result_users: list[UserFullInfoResponse] = []
    for us in users:
        append_user = await get_user_info(us, session)
        result_users.append(append_user)

    return paginate(result_users)


@user_router.delete(
    "/",
    response_model=BaseResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete user"
)
async def delete_user(
        user: WikiUserHandlerData = Depends(BasePermission(responsibility=ResponsibilityType.ADMIN)),
        user_identifiers: UserIdentifiers = Depends(),
        session: AsyncSession = Depends(get_db)
):
    user_repository: UserRepository = UserRepository(session)
    user_db = await get_user_db_by_user_identifiers(user_identifiers, user_repository)

    msg = f"User id: {user_db.id} username: {user_db.username}, email: {user_db.email} deleted"
    await user_repository.mark_user_deleted(user_db.id)

    return BaseResponse(
        msg=msg
    )


@user_router.put(
    "/",
    response_model=UserFullInfoResponse,
    status_code=status.HTTP_200_OK,
    summary="Update user"
)
async def update_user(user_update: UserUpdate,
                      user: WikiUserHandlerData = Depends(BasePermission(responsibility=ResponsibilityType.ADMIN)),
                      session: AsyncSession = Depends(get_db),
                      user_identifiers: UserIdentifiers = Depends()):
    user_repository: UserRepository = UserRepository(session)
    user_db = await get_user_db_by_user_identifiers(user_identifiers, user_repository)

    updated_user: User = await user_repository.update_user(
        user_db.id,
        email=user_update.email,
        username=user_update.username,
        first_name=user_update.first_name,
        last_name=user_update.last_name,
        second_name=user_update.second_name,
        position=user_update.position,
        is_enabled=user_update.is_enabled,
        is_user_agreement_accepted=user_update.is_user_agreement_accepted,
        is_verified_email=user_update.is_verified_email,
        wiki_api_client_id=user_update.wiki_api_client_id
    )

    return await get_user_info(updated_user, session)
