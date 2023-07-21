from sqlalchemy import and_
from typing import Annotated
from os import environ

from dotenv import load_dotenv

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
from passlib.exc import UnknownHashError

from database import db
from models.User import User
from schemas.UserSchema import createUserSchema, updateUserSchema
from utils import Auth  # as Module
from utils.Hash import Hash  # as Class
from validators.userValidator import check_existing_user

import httpx


load_dotenv()
router = APIRouter()


@router.post('/users/auth/register')
def register(
    user: Annotated[createUserSchema, Depends(check_existing_user)]
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


@router.post('/users/auth/login')
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    try:
        user = db.query(User).filter(
            User.email == form_data.email
        ).first()

        if not user or not Hash.verify(form_data.password, user.password):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={'detail': 'Invalid Credentials'},
                headers={'WWW-Authenticate': 'Bearer'},
            )

        access_token = Auth.create_access_token(data={'sub': user.email})
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


@router.get('/users/auth/profile')
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


@router.put('/user/profile')
def update_profile(request: Request, id: int, user: updateUserSchema):
    pass


@router.get("/users/auth/google-login")
def initiate_google_oauth_login():
    google_auth_url = f"https://accounts.google.com/o/oauth2/auth?client_id={environ.get('GOOGLE_CLIENT_ID')}&redirect_uri={environ.get('GOOGLE_REDIRECT_LOGIN_URI')}&response_type=code&scope=openid%20profile%20email"
    print(google_auth_url)
    return RedirectResponse(url=google_auth_url)


@router.get('/users/auth/google-login/callback')
def google_oauth_login_callback(code: str):
    data = {
        "code": code,
        "client_id": environ.get('GOOGLE_CLIENT_ID'),
        "client_secret": environ.get('GOOGLE_CLIENT_SECRET'),
        "redirect_uri": environ.get('GOOGLE_REDIRECT_LOGIN_URI'),
        "grant_type": "authorization_code",
    }

    response = httpx.post("https://oauth2.googleapis.com/token", data=data)
    if response.status_code == 200:
        access_token = response.json()["access_token"]

        # Fetch user info using the access token from userinfo endpoint
        userinfo_response = httpx.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        if userinfo_response.status_code == 200:
            userinfo = userinfo_response.json()
            user_email = userinfo.get("email")

            if user_email is not None:
                try:
                    user = db.query(User).filter(
                        and_(User.email == user_email, User.google_auth == 0)
                    ).first()

                    if not user:
                        return JSONResponse(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            content={'detail': 'Invalid Credentials'},
                            headers={'WWW-Authenticate': 'Bearer'},
                        )

                    access_token = Auth.create_access_token(
                        data={'sub': user.email})
                    return JSONResponse(
                        status_code=status.HTTP_200_OK,
                        content={
                            'access_token': access_token,
                            'token_type': 'bearer'
                        },
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
        else:
            raise HTTPException(
                status_code=401, detail="Failed to fetch user info")
    else:
        raise HTTPException(
            status_code=401, detail="Google OAuth login failed")


@router.get('/users/auth/google-auth-register/callback')
def google_oauth_register_callback(code: str):
    data = {
        "code": code,
        "client_id": environ.get('GOOGLE_CLIENT_ID'),
        "client_secret": environ.get('GOOGLE_CLIENT_SECRET'),
        "redirect_uri": environ.get('GOOGLE_REDIRECT_LOGIN_URI'),
        "grant_type": "authorization_code",
    }

    response = httpx.post("https://oauth2.googleapis.com/token", data=data)

    if response.status_code == 200:
        # Handle successful login and redirect to frontend
        access_token = response.json()["access_token"]
        # Add your custom logic here to log in the user and create a session
        # For example, store the access_token in a session cookie and use it for authentication
        redirect_url = "http://localhost:3000"  # Change to your frontend URL
        return RedirectResponse(url=redirect_url)

    raise HTTPException(status_code=401, detail="Google OAuth login failed")
