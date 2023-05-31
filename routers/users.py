from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
from passlib.exc import UnknownHashError

from database import db
from models.User import User
from schemas.UserSchema import UserSchema
from utils import Auth  # as Module
from utils.Hash import Hash  # as Class
from validators.userValidator import check_existing_user

router = APIRouter()


@router.post('/auth/register')
def register(
    user: Annotated[UserSchema, Depends(check_existing_user)]
):
    try:
        new_user = User(
            name=user.name,
            username=user.username,
            email=user.email,
            password=Hash.make(user.password)
        )

        db.add(new_user)
        db.commit()

        resp = {
            'detail': 'User created',
            'data': {
                'id': new_user.id,
                'name': new_user.name,
                'username': new_user.username,
                'email': new_user.email,
            }
        }
        return JSONResponse(status_code=201, content=resp)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
                content={'detail': 'Invalid Credentials'},
                headers={'WWW-Authenticate': 'Bearer'},
            )

        access_token = Auth.create_access_token(data={'sub': user.username})
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


@router.get('/auth/profile')
def profile(token: str = Depends(OAuth2PasswordBearer(tokenUrl='/auth/login'))):
    try:
        payload = Auth.decode(token)
        username = payload.get('sub')
        user = db.query(User).filter(User.username == username).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found'
            )

        user_data = {
            'id': user.id,
            'name': user.name,
            'username': user.username,
            'email': user.email
        }

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                'detail': 'Profile data fetched successfully',
                'data': user_data
            }
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Unauthorized',
            headers={'WWW-Authenticate': 'Bearer'}
        )
