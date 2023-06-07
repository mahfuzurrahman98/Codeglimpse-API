from enum import Enum
from typing import Optional

from pydantic import BaseModel


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


class updateSnippetSchema(BaseModel):
    title: Optional[str]
    content: Optional[str]
    language: Optional[int]
    visibility: Optional[VisibilityEnum]
    share_with: Optional[str]

    class Config:
        use_enum_values = True
