from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from jose import JWTError
from passlib.exc import UnknownHashError

from database import db
from models.ProgrammingLanguage import ProgrammingLanguage
from models.Snippet import Snippet
from schemas.SnippetSchema import createSnippetSchema
from validators.snippetValidator import (validate_new_snippet,
                                         validate_update_snippet)

router = APIRouter()


@router.post('/snippets')
def store(request: Request, snippet: Annotated[createSnippetSchema, Depends(validate_new_snippet)]):
    return JSONResponse(
        status_code=200,
        content={
            'snippet': snippet
        }
    )
    try:
        new_snippet = Snippet(
            uid=str(uuid4()),
            title=snippet.title,
            content=snippet.content,
            language=snippet.language,
            visibility=snippet.visibility,
            user_id=request.state.user.get('id'),
            share_with=snippet.share_with
        )
        db.add(new_snippet)
        db.commit()

        return JSONResponse(
            status_code=200,
            content={
                'detail': 'Snippet create successfully',
                'data': {
                    'snippet': {
                        'id': new_snippet.id,
                        'uid': new_snippet.uid,
                        'title': new_snippet.title,
                        'content': new_snippet.content,
                        'language': new_snippet.programming_language.name
                    }
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/snippets/{id}')
def show(request: Request, id: int):
    try:
        snippet = db.query(Snippet).filter(
            Snippet.id == id
        ).first()

        if snippet is None:
            return JSONResponse(
                status_code=404,
                content={
                    'detail': 'Snippets not found',
                }
            )

        if (snippet.user_id != request.state.user.get('id')):
            share_with_ids = snippet.share_with.split(',')
            if (
                    snippet.visibility == 1 or
                    (
                        snippet.visibility == 2 and
                        request.state.user.get('id') not in share_with_ids
                    )
            ):
                return JSONResponse(
                    status_code=403,
                    content={
                        'detail': 'Access denied',
                    }
                )

        snippet = snippet.serialize()
        return JSONResponse(
            status_code=200,
            content={
                'detail': 'Snipppet fetched successfully',
                'data': {
                    'snippet': snippet
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/snippets')
def index(request: Request):
    try:
        snippets = db.query(Snippet).filter(
            Snippet.user_id == request.state.user.get('id')
        ).all()

        if len(snippets) == 0:
            return JSONResponse(
                status_code=404,
                content={
                    'detail': 'You have no snippets yet',
                }
            )

        snippets = [snippet.serialize() for snippet in snippets]
        return JSONResponse(
            status_code=200,
            content={
                'detail': 'Snipppets fetched successfully',
                'data': {
                    'snippets': snippets
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
