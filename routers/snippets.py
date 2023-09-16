from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse

from database import db
from models.Snippet import Snippet, get_language
from schemas.SnippetSchema import (createSnippetSchema, privateSnippetSchema,
                                   updateSnippetSchema)
from sqlalchemy import desc
from utils import UID
from validators.snippetValidator import (
    validate_snippet,
    validate_new_snippet,
    validate_edit_snippet,
    validate_update_snippet,
    validate_delete_snippet,
)

from middlewares import get_current_user

router = APIRouter()


# create a snippet
@router.post('/snippets')
def store(
    request: Request,
    snippet: Annotated[createSnippetSchema, Depends(validate_new_snippet)],
    user=Depends(get_current_user),
):
    try:
        new_snippet = Snippet(
            uid=UID.generate(),
            title=snippet.title,
            source_code=snippet.source_code,
            language=snippet.language,
            tags=snippet.tags,
            visibility=snippet.visibility,
            pass_code=snippet.pass_code if snippet.pass_code is not None else None,
            theme=snippet.theme if snippet.theme is not None else 'monokai',
            user_id=user.get('id')
        )
        db.add(new_snippet)
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                'detail': 'Snippet create successfully',
                'data': {
                    'snippet': new_snippet.serialize()
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# get only your snippets
@router.get('/snippets/my')
def get_my_snippets(
    request: Request,
    user=Depends(get_current_user),
    q: str = '',
    page: int = 1,
    limit: int = 10,
):
    try:
        title_condition = Snippet.title.ilike(f"%{q}%")
        tag_condition = Snippet.tags.ilike(f"%{q}%")

        snippets = (
            db.query(Snippet)
            .filter(
                Snippet.user_id == user.get('id'),
                title_condition | tag_condition
            )
            .limit(limit)
            .offset((page - 1) * limit)
            .all()
        )

        if len(snippets) == 0:
            return JSONResponse(
                status_code=404,
                content={
                    'detail': 'No snippets found',
                }
            )

        snippets = [snippet.serialize() for snippet in snippets]
        # filer only the title, tags, language, visibility, created_at, updated_at
        for snippet in snippets:
            del snippet['source_code']
            if snippet['visibility'] == 2:
                del snippet['pass_code']
            del snippet['theme']

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


# get all public snippets
@router.get('/snippets')
def index(
    request: Request,
    q: str = '',
    page: int = 1,
    limit: int = 10,
):
    try:
        title_condition = Snippet.title.ilike(f"%{q}%")
        tag_condition = Snippet.tags.ilike(f"%{q}%")

        total_count = (
            db.query(Snippet)
            .filter(
                Snippet.visibility == 1,
                title_condition | tag_condition
            )
            .count()
        )

        snippets = (
            db.query(Snippet)
            .filter(
                Snippet.visibility == 1,
                title_condition | tag_condition
            )
            .order_by(desc(Snippet.created_at))
            .limit(limit)  
            .offset((page - 1) * limit)
            .all()
        )

        if len(snippets) == 0:
            return JSONResponse(
                status_code=404,
                content={
                    'detail': 'No snippets found',
                }
            )

        snippets = [snippet.serialize() for snippet in snippets]
        for snippet in snippets:
            del snippet['id']
            del snippet['visibility']
            del snippet['updated_at']
            snippet['mode'] = get_language(snippet['_lang'])['mode']
            del snippet['_lang']
            snippet['source_code'] = snippet['source_code'][:200] if len(
                snippet['source_code']) > 200 else snippet['source_code']

        return JSONResponse(
            status_code=200,
            content={
                'detail': 'Snipppets fetched successfully',
                'data': {
                    'snippets': snippets,
                    'total': total_count
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# get a single snippet
@router.get('/snippets/{uid}')
def show(request: Request, snippet: Snippet = Depends(validate_snippet)):
    try:
        _snippet = snippet.serialize()
        del _snippet['id']
        del _snippet['visibility']
        del _snippet['updated_at']
        _snippet['mode'] = get_language(_snippet['_lang'])['mode']
        del _snippet['_lang']

        return JSONResponse(
            status_code=200,
            content={
                'detail': 'Snipppet fetched successfully',
                'data': {
                    'snippet': _snippet
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# get a private snippet with passcode
@router.post('/snippets/private/{uid}')
def show_private_snippet(request: Request, uid: str, form_data: privateSnippetSchema):
    try:
        snippet = db.query(Snippet).filter(
            Snippet.uid == uid
        ).first()

        if snippet is None:
            return JSONResponse(
                status_code=404,
                content={
                    'detail': 'Snippets not found',
                }
            )

        if (snippet.pass_code != form_data.pass_code):
            return JSONResponse(
                status_code=403,
                content={
                    'detail': 'Access denied, provide the correct passcode'
                }
            )

        _snippet = snippet.serialize()
        del _snippet['id']
        del _snippet['visibility']
        del _snippet['updated_at']
        _snippet['mode'] = get_language(_snippet['_lang'])['mode']
        del _snippet['_lang']

        return JSONResponse(
            status_code=200,
            content={
                'detail': 'Snipppet fetched successfully',
                'data': {
                    'snippet': _snippet
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# edit a single snippet
@router.get('/snippets/{uid}/edit')
def edit(
    request: Request,
    uid: str,
    snippet: Snippet = Depends(validate_edit_snippet)
):
    try:
        _snippet = snippet.serialize()
        del _snippet['id']
        del _snippet['created_at']
        del _snippet['updated_at']
        del _snippet['owner']

        _snippet['mode'] = get_language(_snippet['_lang'])['mode']
        _snippet['language'] = _snippet['_lang']

        del _snippet['_lang']

        return JSONResponse(
            status_code=200,
            content={
                'detail': 'Snipppet fetched successfully',
                'data': {
                    'snippet': _snippet
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# update a snippet
@router.put('/snippets/{uid}')
def update(
    request: Request,
    uid: str,
    snippet: Annotated[updateSnippetSchema, Depends(validate_update_snippet)],
    user=Depends(get_current_user)
):
    try:
        existing_snippet = db.query(Snippet).filter(Snippet.uid == uid).first()

        if snippet.title is not None:
            snippet.title = snippet.title.strip()
        if snippet.source_code is not None:
            existing_snippet.source_code = snippet.source_code
        if snippet.language is not None:
            existing_snippet.language = snippet.language
        if snippet.tags is not None:
            existing_snippet.visibility = snippet.visibility
        if snippet.visibility is not None:
            existing_snippet.pass_code = snippet.pass_code
        if snippet.theme is not None:
            existing_snippet.theme = snippet.theme

        db.commit()

        return JSONResponse(
            status_code=200,
            content={
                'detail': 'Snippet updated successfully'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# delete a snippet
@router.delete('/snippets/{uid}')
def destroy(
    request: Request,
    uid: str,
    user=Depends(get_current_user),
    snippet: Snippet = Depends(validate_delete_snippet)
):
    try:
        db.delete(snippet)
        db.commit()

        return JSONResponse(
            status_code=204,
            content={
                'detail': 'Snippet deleted successfully',
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
