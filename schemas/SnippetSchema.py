from enum import Enum
from typing import Optional

from pydantic import BaseModel, constr, validator


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

    class Config:
        use_enum_values = True

    @validator('title', 'content')
    def validate_blank_fields(cls, value, field):
        field_name = field.alias
        value = value.strip()
        if value == '':
            raise ValueError(f'{field_name.capitalize()} cannot be blank')
        return value


class updateSnippetSchema(BaseModel):
    title: Optional[str]
    content: Optional[str]
    language: Optional[int]
    visibility: Optional[VisibilityEnum]
    share_with: Optional[str]

    class Config:
        use_enum_values = True

    @validator('title', 'content', 'language', 'share_with')
    def validate_fields(cls, value, field):
        field_name = field.alias
        value = value.strip()
        if value is not None and not isinstance(value, field.type_):
            raise ValueError(f'Invalid type for "{field_name}" field')
        return value
