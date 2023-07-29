from typing import Optional
from lib.data.programming_languages import programming_languages
from pydantic import BaseModel, field_validator

ext_list = [lang['ext'] for lang in programming_languages]


class createSnippetSchema(BaseModel):
    title: str
    source_code: str
    language: str
    tags: Optional[str] = None
    visibility: int
    pass_code: Optional[str] = None
    theme: str
    font_size: int

    @field_validator('title')
    def validate_blank_title_field(cls, value):
        value = value.strip()
        if value == '':
            raise ValueError('Title cannot be blank')
        return value

    @field_validator('source_code')
    def validate_blank_source_code_field(cls, value):
        value = value.strip()
        if value == '':
            raise ValueError('Source code cannot be blank')
        return value

    @field_validator('language')
    def validate_language_field(cls, value):
        value = value.strip()
        if value not in ext_list:
            raise ValueError('Invalid language')
        return value

    @field_validator('pass_code')
    def validate_pass_code_field(cls, value, values):
        if values.data['visibility'] == 2 and value is None:
            raise ValueError('Pass code is mandatory')

        if value is not None and not value.isalnum():
            raise ValueError('Invalid pass code')

        if value is not None and len(value) != 6:
            raise ValueError('Pass code should be 6 characters')
        return value


class updateSnippetSchema(BaseModel):
    title: Optional[str]
    content: Optional[str]
    language: Optional[int]
    visibility: Optional[int]
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
