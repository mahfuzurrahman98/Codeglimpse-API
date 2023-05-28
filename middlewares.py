from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from database import db
from models.User import User
from utils import Auth

load_dotenv()


async def authenticate(request: Request, call_next):
    if (request.url.path.startswith("/auth/login")):
        return await call_next(request)

    token_exception = JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={'detail': 'Invalid token'},
        headers={'WWW-Authenticate': 'Bearer'},
    )

    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        return token_exception

    token = token.replace("Bearer ", "")

    try:
        payload = Auth.decode(token)
        username = payload.get("sub")
        if not username:
            raise token_exception
    except Exception:
        return token_exception

    user = db.query(User).filter(User.username == username).first()
    if not user:
        return token_exception

    request.state.user = user

    response = await call_next(request)
    return response


async def get_current_user(token: Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl='/auth/login'))]):
    token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Invalid tokoen',
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = Auth.decode(token)
        username: str = payload.get("sub")
        if username is None:
            raise token_exception

    except JWTError:
        raise token_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise token_exception
    return user
