from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from jose import JWTError
from passlib.exc import UnknownHashError

from database import db
from models.ProgrammingLanguage import ProgrammingLanguage
from models.Snippet import Snippet
from schemas.SnippetSchema import SnippetSchema
from validators.snippetValidator import check_valid_snippet

router = APIRouter()


@router.post('/snippets')
def store(snippet: Annotated[SnippetSchema, Depends(check_valid_snippet)]):
    print(snippet)
    return JSONResponse(
        status_code=200,
        content={'detail': 'asdf'}
    )
