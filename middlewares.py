from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from database import db
from models.User import User
from utils import Auth
import re

load_dotenv()


async def authenticate(request: Request, call_next):
    path = request.url.path
    edit_route_pattern = r'/snippets/[a-zA-Z0-9]+/edit'

    is_edit_route = False
    if re.search(edit_route_pattern, path):
        is_edit_route = True

    x = '/snippets' in path and request.method == 'GET' and not is_edit_route and '/snippets/my' not in path

    if (
        path == '/' or
        '/auth/' in path or
        '/docs' in path or
        '/redoc' in path or
        '/openapi.json' in path or
        ('/snippets/private' in path and request.method == 'POST') or
        (
            '/snippets' in path and request.method == 'GET' and
            (
                not is_edit_route and
                '/snippets/my' not in path
            )
        ) or

        '/data/languages' in path or
        '/data/themes' in path or
        request.method == 'OPTIONS'
    ):
        return await call_next(request)

    token_exception = JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={'detail': 'Unauthorized'},
        headers={'WWW-Authenticate': 'Bearer'},
    )

    token = request.headers.get('Authorization')

    if not token or not token.startswith('Bearer '):
        return token_exception

    token = token.replace('Bearer ', '')

    try:
        payload = Auth.decode_access_token(token)
        email = payload.get('sub')
        if not email:
            raise token_exception

    except Exception as e:
        return token_exception

    user = db.query(User).filter(User.email == email).first()
    if not user:
        return token_exception

    request.state.user = {
        'id': user.id,
        'name': user.name,
        'username': user.username,
        'email': user.email
    }

    response = await call_next(request)
    return response
