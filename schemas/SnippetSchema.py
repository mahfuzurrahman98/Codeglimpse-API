from pydantic import BaseModel


class SnippetSchema(BaseModel):
    title: str
    content: str
    language: str
    visibility: int
