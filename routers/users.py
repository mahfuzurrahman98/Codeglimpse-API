from datetime import datetime, timedelta
from os import environ
from typing import Annotated

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from passlib.exc import UnknownHashError
from sqlalchemy import and_

from database import db
from models.User import User
from schemas.UserSchema import (
    createUserSchema,
    loginFormSchema,
    callbackSchema,
    updateUserSchema
)
from utils import Auth  # as Module
from utils.Hash import Hash  # as Class
from validators.userValidator import check_existing_user

load_dotenv()
router = APIRouter()


# # Register using Password
# @router.post('/users/auth/register')
# def register(
#     user: Annotated[createUserSchema, Depends(check_existing_user)]
# ):
#     try:
#         new_user = User(
#             name=user.name,
#             username=user.username,
#             email=user.email,
#             password=Hash.make(user.password)
#         )

#         db.add(new_user)
#         db.commit()

#         resp = {
#             'detail': 'User created',
#             'data': new_user.serialize()
#         }
#         return JSONResponse(status_code=201, content=resp)

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# # Login using Password
# @router.post('/users/auth/login')
# def login(
#     form_data: loginFormSchema
# ):
#     try:
#         user = db.query(User).filter(
#             User.email == form_data.email
#         ).first()

#         if not user or not Hash.verify(form_data.password, user.password):
#             return JSONResponse(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 content={'detail': 'Invalid Credentials'}
#             )

#         access_token = Auth.create_access_token(data={'sub': user.email})
#         print(access_token)
#         refresh_token = Auth.create_refresh_token(data={'sub': user.email})
#         response = JSONResponse(
#             status_code=status.HTTP_200_OK,
#             content={
#                 'detail': 'Login successful',
#                 'data': {
#                     'user': user.serialize(),
#                     'access_token': access_token
#                 }
#             },
#             headers={'WWW-Authenticate': 'Bearer'},
#         )
#         # print(response)
#         response.set_cookie(
#             key='refresh_token',
#             value=refresh_token,
#             max_age=environ.get('REFRESH_TOKEN_EXPIRE_MINUTES'),
#             expires=environ.get('REFRESH_TOKEN_EXPIRE_MINUTES'),
#             # path='/api/v1/users/auth/refreshtoken',
#             path='/',
#             secure=False,
#             httponly=True,
#             samesite="strict",
#         )
#         return response

#     except UnknownHashError as e:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=str(e)+' xx',
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=str(e) + ' x2x',
#         )


# Login using Google OAuth
@router.post('/users/auth/google-login')
def google_oauth_login(form_data: callbackSchema):
    data = {
        "code": form_data.code,
        "client_id": environ.get('GOOGLE_CLIENT_ID'),
        "client_secret": environ.get('GOOGLE_CLIENT_SECRET'),
        "redirect_uri": environ.get('GOOGLE_REDIRECT_URI'),
        "grant_type": "authorization_code",
    }

    response = httpx.post("https://oauth2.googleapis.com/token", data=data)
    if response.status_code == 200:
        access_token = response.json()["access_token"]

        userinfo_response = httpx.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        if userinfo_response.status_code == 200:
            userinfo = userinfo_response.json()

            response_message = 'Login successful'
            try:
                user = db.query(User).filter(
                    and_(
                        User.email == userinfo.get("email"),
                        User.google_auth == 1
                    )
                ).first()

                if not user:
                    try:
                        user = User(
                            name=userinfo.get("name"),
                            username=userinfo.get("given_name"),
                            email=userinfo.get("email"),
                            google_auth=1
                        )

                        db.add(user)
                        db.commit()
                        response_message = 'Welcome to Codeglimpse!'
                    except Exception as e:
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e)+'err from create user',
                        )

                access_token = Auth.create_access_token(
                    data={'sub': user.email}
                )
                refresh_token = Auth.create_refresh_token(
                    data={'sub': user.email}
                )

                _user = user.serialize()
                _user['picture'] = userinfo.get('picture')
                response = JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        'detail': response_message,
                        'data': {
                            'user': _user,
                            'access_token': access_token
                        }
                    }
                )

                max_age_minutes = int(
                    environ.get('REFRESH_TOKEN_EXPIRE_MINUTES')
                )
                max_age_seconds = max_age_minutes * 60

                response.set_cookie(
                    key='refresh_token',
                    value=refresh_token,
                    max_age=max_age_seconds,
                    expires=max_age_seconds,
                    # path='/api/v1/users/auth/refreshtoken',
                    path='/',
                    secure=False,
                    httponly=True,
                    samesite="strict",
                )
                return response
            except UnknownHashError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e)+'err from hash',
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(e)+'err from filter user',
                )

        else:
            raise HTTPException(
                status_code=401, detail="Failed to fetch user info")
    else:
        raise HTTPException(
            status_code=401, detail="Google OAuth login failed")


# refresh token
@router.post('/users/auth/refreshtoken')
def refresh_token(request: Request):
    token_exception = JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'detail': 'Unauthorized'},
        headers={'WWW-Authenticate': 'Bearer'},
    )

    token = request.cookies.get('refresh_token')

    if not token:
        return token_exception

    try:
        payload = Auth.decode_refresh_token(token)
        email = payload.get('sub')
        if not email:
            raise token_exception
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise token_exception

        _user = user.serialize()
        _user['picture'] = ''
    except Exception:
        return token_exception

    try:
        access_token = Auth.create_access_token(data={'sub': user.email})

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                'detail': 'Authentication successful',
                'data': {
                    'user': _user,
                    'access_token': access_token,
                }
            },
            headers={'WWW-Authenticate': 'Bearer'},
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


# Logout
@router.post('/users/auth/logout')
def logout(request: Request):
    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'detail': 'Logout successful',
        }
    )
    response.delete_cookie('refresh_token')
    return response
