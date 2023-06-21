from starlette.requests import Request

from src.app.auth import router, oauth
from src.app.config import settings

innopolis_sso = oauth.register(
    "innopolis",
    client_id=settings.INNOPOLIS_SSO_CLIENT_ID,
    client_secret=settings.INNOPOLIS_SSO_CLIENT_SECRET,
    # OAuth client will fetch configuration on first request
    server_metadata_url="https://sso.university.innopolis.ru/adfs/.well-known/openid-configuration",
    client_kwargs={"scope": "openid"}
)
redirect_uri = "https://innohassle.campus.innopolis.university/oauth2/callback"


@router.get("/innopolis/login")
async def login_via_innopolis(request: Request):
    return await oauth.innopolis.authorize_redirect(request, redirect_uri)


@router.get("/innopolis/token")
async def auth_via_innopolis(request: Request):
    token = await oauth.innopolis.authorize_access_token(request)
    user_info = token['userinfo']
    email = user_info["email"]
    name = user_info["commonname"]
    # TODO: Create user and return JWT
    return {"email": email, "name": name}
