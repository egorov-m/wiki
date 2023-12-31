from typing import Optional

from fastapi import Security, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, APIKeyQuery, APIKeyHeader, APIKeyCookie
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from wiki.auth.authenticators.api_key import ApiKeyAuthenticatorInterface
from wiki.auth.authenticators.wiki_token import WikiTokenAuthenticatorInterface
from wiki.auth.enums import AuthorizationMode
from wiki.auth.utils import get_fake_admin_user_handler_data
from wiki.common.exceptions import WikiException, WikiErrorCode
from wiki.common.schemas import ExternalUserHandlerData, WikiUserHandlerData
from wiki.config import settings
from wiki.database.deps import get_db


wiki_api_key_query = APIKeyQuery(name=settings.AUTH_API_KEY_QUERY_NAME,
                                 scheme_name="WikiApiKey",
                                 auto_error=False)
wiki_api_key_header = APIKeyHeader(name=settings.AUTH_API_KEY_HEADER_NAME,
                                   scheme_name="WikiApiKey",
                                   auto_error=False)
wiki_root_api_key_header = APIKeyHeader(name=settings.AUTH_ROOT_API_KEY_HEADER_NAME,
                                        scheme_name="WikiRootApiKey",
                                        auto_error=False,
                                        description="Root key, allows you to perform actions as administrator, "
                                                    "random user data is generated.\n"
                                                    "**Limitation:** operations requiring an explicitly registered user"
                                                    "are unavailable, example.: `Create: POST /api_key/`.")
wiki_access_token_cookie = APIKeyCookie(name=settings.AUTH_ACCESS_TOKEN_COOKIE_NAME,
                                        scheme_name="WikiAccessToken",
                                        auto_error=False)
wiki_access_token_bearer = HTTPBearer(scheme_name="WikiBearer", auto_error=False)
# wiki_refresh_token_cookie = APIKeyCookie(name=settings.AUTH_REFRESH_TOKEN_COOKIE_NAME,
#                                          scheme_name="WikiRefreshToken",
#                                          auto_error=False)


class AuthUserDependency:
    authorisation_mode: AuthorizationMode
    is_available_disapproved_user: bool

    def __init__(self,
                 authorisation_mode: AuthorizationMode = AuthorizationMode.AUTHORIZED,
                 is_available_disapproved_user: bool = False):
        self.authorisation_mode = authorisation_mode
        self.is_available_disapproved_user = is_available_disapproved_user

    async def __call__(
            self,
            root_api_key_header: Optional[str] = Security(wiki_root_api_key_header),
            api_key_query: Optional[str] = Security(wiki_api_key_query),
            api_key_header: Optional[str] = Security(wiki_api_key_header),
            access_token_cookie: Optional[str] = Security(wiki_access_token_cookie),
            access_token_bearer: Optional[HTTPAuthorizationCredentials] = Security(wiki_access_token_bearer),
            session: AsyncSession = Depends(get_db),
    ) -> ExternalUserHandlerData | WikiUserHandlerData:
        if root_api_key_header is not None:
            if root_api_key_header in settings.AUTH_ROOT_API_KEYS:
                return get_fake_admin_user_handler_data()
        if self.authorisation_mode == AuthorizationMode.UNAUTHORIZED:
            try:
                user = await self._get_user(api_key_query,
                                            api_key_header,
                                            access_token_cookie,
                                            access_token_bearer,
                                            session,
                                            self.is_available_disapproved_user)
                return user or ExternalUserHandlerData()
            except WikiException:
                return ExternalUserHandlerData()
        else:
            user = await self._get_user(api_key_query,
                                        api_key_header,
                                        access_token_cookie,
                                        access_token_bearer,
                                        session,
                                        self.is_available_disapproved_user)
            if user is not None:
                return user
            else:
                raise WikiException(message="Could not validate credentials.",
                                    error_code=WikiErrorCode.AUTH_NOT_VALIDATE_CREDENTIALS,
                                    http_status_code=status.HTTP_401_UNAUTHORIZED)

    @classmethod
    async def _get_user(cls,
                        api_key_query,
                        api_key_header,
                        access_token_cookie,
                        access_token_bearer,
                        session,
                        is_available_disapproved_user):
        if api_key_query is not None or api_key_header is not None:
            authenticator = ApiKeyAuthenticatorInterface(session)
            return await authenticator.validate(api_key_query or api_key_header,
                                                is_available_disapproved_user)
        if access_token_cookie is not None or access_token_bearer is not None:
            if access_token_bearer is not None:
                if not access_token_bearer.scheme == "Bearer":
                    raise WikiException(
                        message="Invalid authentication scheme.",
                        error_code=WikiErrorCode.AUTH_NOT_VALIDATE_CREDENTIALS,
                        http_status_code=status.HTTP_403_FORBIDDEN
                    )
            authenticator = WikiTokenAuthenticatorInterface(session)
            return await authenticator.validate(access_token_cookie or access_token_bearer.credentials,
                                                is_available_disapproved_user)
