from enum import Enum
from typing import Optional

from pydantic import BaseModel, field_validator


class VisibilityEnum(Enum):
    ONE = 1
    TWO = 2
    THREE = 3


class createSnippetSchema(BaseModel):
    title: str
    content: str
    language: int
    visibility: VisibilityEnum
    share_with: Optional[str]

    @field_validator('title')
    def validate_blank_title_field(cls, value):
        value = value.strip()
        if value == '':
            raise ValueError('Title cannot be blank')
        return value

    @field_validator('content')
    def validate_blank_content_field(cls, value):
        value = value.strip()
        if value == '':
            raise ValueError('Content cannot be blank')
        return value


class updateSnippetSchema(BaseModel):
    title: Optional[str]
    content: Optional[str]
    language: Optional[int]
    visibility: Optional[VisibilityEnum]
    share_with: Optional[str]

    @field_validator('title')
    def validate_title_field(cls, value):
        value = value.strip()
        if value is not None and not isinstance(value, cls.title.type):
            raise ValueError('Invalid type for title field')
        return value

    @field_validator('content')
    def validate_content_field(cls, value):
        value = value.strip()
        if value is not None and not isinstance(value, cls.content.type):
            raise ValueError('Invalid type for content field')
        return value

    @field_validator('language')
    def validate_language_field(cls, value):
        value = value.strip()
        if value is not None and not isinstance(value, cls.language.type):
            raise ValueError('Invalid type for language field')
        return value

    @field_validator('share_with')
    def validate_share_with_field(cls, value):
        value = value.strip()
        if value is not None and not isinstance(value, cls.share_with.type):
            raise ValueError('Invalid type for share_with field')
        return value
