from fastapi import HTTPException, status

from database import db
from models.User import User
from schemas.UserSchema import UserSchema


def check_existing_user(user: UserSchema):
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email already registered"
        )

    existing_username = db.query(User).filter(
        User.username == user.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Username already taken"
        )

    return user
