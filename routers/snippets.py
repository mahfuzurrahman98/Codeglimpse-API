from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse

from database import db
from models.Snippet import Snippet
from schemas.SnippetSchema import createSnippetSchema, updateSnippetSchema
from validators.snippetValidator import (validate_new_snippet,
                                         validate_update_snippet)

router = APIRouter()


@router.post('/snippets')
def store(request: Request, snippet: Annotated[createSnippetSchema, Depends(validate_new_snippet)]):
    try:
        new_snippet = Snippet(
            uid=str(uuid4()),
            title=snippet.title,
            content=snippet.content,
            language=snippet.language,
            visibility=snippet.visibility,
            user_id=request.state.user.get('id'),
            share_with=snippet.share_with if snippet.visibility == 2 else None
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


@router.put('/snippets/{id}')
def update_snippet(id: int, request: Request, snippet: SnippetSchema = Depends(validate_update_snippet), db: Session = Depends(get_db)):
    # Find the snippet to update
    existing_snippet = db.query(Snippet).filter(Snippet.id == id).first()
    if not existing_snippet:
        raise HTTPException(status_code=404, detail='Snippet not found')

    # Update the snippet attributes based on the request
    existing_snippet.title = snippet.title
    existing_snippet.content = snippet.content
    existing_snippet.language = snippet.language
    existing_snippet.visibility = snippet.visibility
    existing_snippet.share_with = snippet.share_with if snippet.visibility == 2 else None

    try:
        db.commit()
        return {
            'detail': 'Snippet updated successfully',
            'data': {
                'snippet': {
                    'id': existing_snippet.id,
                    'uid': existing_snippet.uid,
                    'title': existing_snippet.title,
                    'content': existing_snippet.content,
                    'language': existing_snippet.programming_language.name
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
