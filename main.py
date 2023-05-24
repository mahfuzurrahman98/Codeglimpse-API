from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field, validator

app = FastAPI()


class User(BaseModel):
    name: str
    email: EmailStr
    username: str
    password: str

    @validator('name', 'username')
    def validate_blank_fields(cls, value, field):
        field_name = field.alias
        value = value.strip()
        if value == '':
            raise ValueError(f'{field_name.capitalize()} cannot be blank')
        return value

    @validator('password')
    def validate_password(cls, value):
        value = value.strip()
        if ' ' in value:
            raise ValueError('Password cannot contain spaces')
        if len(value) < 6:
            raise ValueError('Password must be at least 6 characters')
        return value


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    error_messages = {}
    for error in exc.errors():
        field = error['loc'][1]
        error_messages[field] = error['msg']
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({'detail': error_messages}),
    )


@app.get('/')
def read_root():
    return {'detail': 'Hello World'}

# make a post requesta to accepet user data to register a user


@app.post('/register')
def register_user(user: User):
    return user
