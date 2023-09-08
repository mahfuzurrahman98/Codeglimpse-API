from typing import Optional

from fastapi import HTTPException, status
from pydantic import BaseModel, field_validator


class createSnippetSchema(BaseModel):
    title: str
    source_code: str
    language: str
    tags: Optional[list[str]] = None
    visibility: int
    pass_code: Optional[str] = None
    theme: str

    @field_validator('title')
    def validate_blank_title_field(cls, value):
        value = value.strip()
        if value == '':
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Title cannot be blank'
            )
        return value

    @field_validator('source_code')
    def validate_blank_source_code_field(cls, value):
        value = value.strip()
        if value == '':
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Source code cannot be blank'
            )
        return value

    @field_validator('visibility')
    def validate_visibility_field(cls, value):
        if value not in [1, 2]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Invalid visibility'
            )
        return value

    @field_validator('theme')
    def validate_blank_theme_field(cls, value):
        value = value.strip()
        if value == '':
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Theme cannot be blank'
            )
        return value


class updateSnippetSchema(BaseModel):
    title: Optional[str] = None
    source_code: Optional[str] = None
    language: Optional[str] = None
    tags: Optional[list[str]] = None
    visibility: Optional[int] = None
    pass_code: Optional[str] = None
    theme: Optional[str] = None

    @field_validator('title')
    def validate_title_field(cls, value):
        value = value.strip()
        if value is not None and not isinstance(value, str):
            raise ValueError('Invalid type for title field')
        return value

    @field_validator('source_code')
    def validate_content_field(cls, value):
        value = value.strip()
        if value is not None and not isinstance(value, str):
            raise ValueError('Invalid type for source code field')
        return value

    @field_validator('language')
    def validate_language_field(cls, value):
        value = value.strip()
        if value is not None and not isinstance(value, str):
            raise ValueError('Invalid type for language field')
        return value

    @field_validator('visibility')
    def validate_visibility_field(cls, value):
        if value is not None and value not in [1, 2]:
            raise ValueError('Invalid type for visibility field')
        return value

    @field_validator('theme')
    def validate_theme_field(cls, value):
        value = value.strip()
        if value is not None and not isinstance(value, str):
            raise ValueError('Invalid type for theme field')
        return value


class privateSnippetSchema(BaseModel):
    pass_code: str

    @field_validator('pass_code')
    def validate_pass_code_field(cls, value):
        value = value.strip()
        if value == '':
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Pass code is mandatory'
            )

        if not value.isalnum():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Invalid pass code'
            )

        if len(value) != 6:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Pass code must be 6 characters long'
            )

        return value
