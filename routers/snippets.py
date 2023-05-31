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
    try:
        new_snippet = Snippet(
            title=snippet.title,
            content=snippet.content,
            language=snippet.language,
            visibility=snippet.visibility,
            title=snippet.title,
            title=snippet.title,
        )
        db.add(new_snippet)
        db.commit()
        return JSONResponse(
            status_code=200,
            content={'detail': 'asdf'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
