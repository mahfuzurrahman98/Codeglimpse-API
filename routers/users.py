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
from schemas.UserSchema import (createUserSchema, loginFormSchema,
                                updateUserSchema)
from utils import Auth  # as Module
from utils.Hash import Hash  # as Class
from validators.userValidator import check_existing_user

load_dotenv()
router = APIRouter()

# Login and Register using Password


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
            'data': new_user.serialize()
        }
        return JSONResponse(status_code=201, content=resp)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/users/auth/login')
def login(
    form_data: loginFormSchema
):
    try:
        user = db.query(User).filter(
            User.email == form_data.email
        ).first()

        if not user or not Hash.verify(form_data.password, user.password):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={'detail': 'Invalid Credentials'}
            )

        access_token = Auth.create_access_token(data={'sub': user.email})
        print(access_token)
        refresh_token = Auth.create_refresh_token(data={'sub': user.email})
        response = JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                'detail': 'Login successful',
                'data': {
                    'user': user.serialize(),
                    'access_token': access_token
                }
            },
            headers={'WWW-Authenticate': 'Bearer'},
        )
        # print(response)
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            max_age=10080*60,
            expires=10080*60,
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
            detail=str(e)+' xx',
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e) + ' x2x',
        )


# Login using Google OAuth
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
        # return response.json()

        # Fetch user info using the access token from userinfo endpoint
        userinfo_response = httpx.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        if userinfo_response.status_code == 200:
            userinfo = userinfo_response.json()
            # return userinfo
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
                        data={'sub': user.email}
                    )
                    return JSONResponse(
                        status_code=status.HTTP_200_OK,
                        content={
                            'access_token': access_token
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
                status_code=401, detail="Failed to fetch user info")
    else:
        raise HTTPException(
            status_code=401, detail="Google OAuth login failed")


# Register using Google OAuth
@router.get("/users/auth/google-register")
def initiate_google_oauth_register():
    google_auth_url = f"https://accounts.google.com/o/oauth2/auth?client_id={environ.get('GOOGLE_CLIENT_ID')}&redirect_uri={environ.get('GOOGLE_REDIRECT_REGISTER_URI')}&response_type=code&scope=openid%20profile%20email"
    print(google_auth_url)
    return RedirectResponse(url=google_auth_url)


@router.get('/users/auth/google-register/callback')
def google_oauth_register_callback(code: str):
    data = {
        "code": code,
        "client_id": environ.get('GOOGLE_CLIENT_ID'),
        "client_secret": environ.get('GOOGLE_CLIENT_SECRET'),
        "redirect_uri": environ.get('GOOGLE_REDIRECT_REGISTER_URI'),
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

            user_email = userinfo.get("email")

            if user_email is not None:
                try:
                    existing_email = db.query(User).filter(
                        User.email == user_email).first()
                    if existing_email:
                        raise HTTPException(
                            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Email already registered"
                        )

                    new_user = User(
                        name=userinfo.get("name"),
                        username=userinfo.get("given_name"),
                        email=user_email,
                        password=None,
                        google_auth=1
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
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=str(e),
                    )
            else:
                raise HTTPException(
                    status_code=401, detail="Failed to fetch user info")
        else:
            raise HTTPException(
                status_code=401, detail="Failed to fetch user info")
    else:
        raise HTTPException(
            status_code=401, detail="Google OAuth failed")


@router.post('/users/auth/refreshtoken')
def refresh_token(request: Request):
    token_exception = JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={'detail': 'Unauthorized'},
        headers={'WWW-Authenticate': 'Bearer'},
    )

    token = request.cookies.get('refresh_token')
    print(token)

    if not token:
        return token_exception

    try:
        payload = Auth.decode(token)
        email = payload.get('sub')
        if not email:
            raise token_exception
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise token_exception
    except Exception:
        return token_exception

    try:
        access_token = Auth.create_access_token(data={'sub': user.email})

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                'detail': 'Authentication successful',
                'data': {
                    'user': user.serialize(),
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


@router.post('/users/auth/logout')
def logout():
    response = JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content={
            'detail': 'Logout successful',
        }
    )
    response.delete_cookie('refresh_token')
    return response
