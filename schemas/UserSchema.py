from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator


class loginFormSchema(BaseModel):
    email: EmailStr
    password: str

    @field_validator('password')
    def validate_password(cls, value):
        value = value.strip()
        if ' ' in value:
            raise ValueError('Password cannot contain spaces')
        if len(value) < 6:
            raise ValueError('Password must be at least 6 characters')
        return value


class callbackSchema(BaseModel):
    code: str

    @field_validator('code')
    def validate_code(cls, value):
        value = value.strip()
        if value == '':
            raise ValueError('Code cannot be blank')
        return value


class createUserSchema(BaseModel):
    name: str
    email: EmailStr
    username: str
    password: str

    @field_validator('name')
    def validate_blank_name_field(cls, value):
        value = value.strip()
        if value == '':
            raise ValueError('Name cannot be blank')
        return value

    @field_validator('username')
    def validate_blank_username_field(cls, value):
        value = value.strip()
        if value == '':
            raise ValueError('Username cannot be blank')
        return value

    @field_validator('password')
    def validate_password(cls, value):
        value = value.strip()
        if ' ' in value:
            raise ValueError('Password cannot contain spaces')
        if len(value) < 6:
            raise ValueError('Password must be at least 6 characters')
        return value


class updateUserSchema(BaseModel):
    # name: Optional[str]

    # @field_validator('name')
    # def validate_blank_field(cls, value, field):
    #     field_name = field.alias
    #     value = value.strip() if field_name != 'lnaguage' else value
    #     if value == '':
    #         raise ValueError(f'{field_name.capitalize()} cannot be blank')
    #     return value

    # @field_validator('name')
    # def validate_name(cls, value):
    #     if value and not value.strip():
    #         raise ValueError('Name cannot be blank if provided')
    #     return value
    pass
