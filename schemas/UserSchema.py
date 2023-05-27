from pydantic import BaseModel, EmailStr, Field, validator


class UserSchema(BaseModel):
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
