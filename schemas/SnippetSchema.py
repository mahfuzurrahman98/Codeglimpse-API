from typing import Optional

from pydantic import BaseModel


class SnippetSchema(BaseModel):
    title: str
    content: str
    language: str
    visibility: int
    share_with: Optional[str]
