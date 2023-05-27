from datetime import datetime, timedelta
from os import environ
from typing import Annotated

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.exc import UnknownHashError

from database import db
from models.User import User
from schemas.UserSchema import UserSchema
from utils.Hash import Hash
from validators.userValidator import check_existing_user

router = APIRouter()

load_dotenv()


@router.post('/auth/register')
def register(
    user: Annotated[UserSchema, Depends(check_existing_user)]
):
    try:
        new_user = User(
            name=user.name,
            username=user.username,
            email=user.email,
            password=user.password
        )

        db.add(new_user)
        db.commit()

        resp = {
            'message': 'User created',
            'data': {
                'user': {
                    'id': new_user.id,
                    'name': new_user.name,
                    'username': new_user.username,
                    'email': new_user.email,
                }
            }
        }
        return JSONResponse(status_code=201, content=resp)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta if expires_delta else datetime.utcnow()

    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(
        to_encode,
        environ.get('SECRET_KEY'),
        algorithm=environ.get('ALGORITHM')
    )
    return encoded_jwt


@router.post('/auth/login')
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    try:
        user = db.query(User).filter(
            User.username == form_data.username
        ).first()

        if not user or not Hash.verify(form_data.password, user.password):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={'message': 'Invalid Credentials'},
                headers={'WWW-Authenticate': 'Bearer'},
            )
        access_token_expires = timedelta(
            minutes=int(environ.get('ACCESS_TOKEN_EXPIRE_MINUTES'))
        )

        access_token = create_access_token(
            data={'sub': user.username}, expires_delta=access_token_expires
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={'access_token': access_token, 'token_type': 'bearer'},
        )
    except UnknownHashError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
