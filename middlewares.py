from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from jose import JWTError, jwt

from database import db
from models.User import User
from utils import Auth


async def authenticate(request: Request, call_next):
    try:
        token = request.headers.get("Authorization")
        payload = Auth.decode(token)
        username = payload.get('sub')
        user = db.query(User).filter(User.username == username).first()

        if not user:
            raise HTTPException(
                tatus_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid token',
                headers={'WWW-Authenticate': 'Bearer'}
            )
        response = await call_next(request)
        return response
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token',
            headers={'WWW-Authenticate': 'Bearer'}
        )
