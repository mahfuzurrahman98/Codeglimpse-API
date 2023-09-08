from fastapi import HTTPException, Request, status

from database import db
from lib.data.languages import languages
from lib.data.themes import themes
from models.Snippet import Snippet
from models.User import User
from schemas.SnippetSchema import createSnippetSchema, updateSnippetSchema
from utils.helpers import tags_arr_to_str

ext_list = [lang['ext'] for lang in languages]
theme_list = [theme['value'] for theme in themes]


def isOnlyAlphaNeumeric(string: str):
    return string.isalnum() and not string.isalpha() and not string.isnumeric()


def validate_new_snippet(request: Request, snippet: createSnippetSchema):
    snippet.title = snippet.title.strip()
    snippet.source_code = snippet.source_code.strip()
    snippet.language = snippet.language.strip()

    if snippet.language not in ext_list:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Invalid language'
        )

    if snippet.theme not in theme_list:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Invalid theme'
        )

    if snippet.visibility == 2:
        if snippet.pass_code is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Pass code is mandatory'
            )

        if not isOnlyAlphaNeumeric(snippet.pass_code):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Invalid pass code'
            )

        if len(snippet.pass_code) != 6:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Pass code should be 6 characters'
            )

    if snippet.tags and len(snippet.tags) > 0:
        snippet.tags = ','.join(snippet.tags)
    else:
        snippet.tags = None

    return snippet


def validate_update_snippet(request: Request, uid: str, update_snippet: updateSnippetSchema):
    existing_snippet = db.query(Snippet).filter(Snippet.uid == uid).first()

    if existing_snippet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Snippet not found'
        )

    if request.state.user.get('id') != existing_snippet.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You don\'t have permission to edit this snippet'
        )

    if update_snippet.title is not None:
        update_snippet.title = update_snippet.title.strip()

    if update_snippet.source_code is not None:
        update_snippet.source_code = update_snippet.source_code.strip()

    if update_snippet.language is not None:
        update_snippet.language = update_snippet.language.strip()

    if update_snippet.visibility is not None and update_snippet.visibility == 2:
        if update_snippet.pass_code is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Pass code is mandatory'
            )

        if not update_snippet.pass_code.isalnum():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Invalid pass code'
            )

        if len(update_snippet.pass_code) != 6:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Pass code should be 6 characters'
            )

    if update_snippet.tags is not None:
        if len(update_snippet.tags) > 0:
            update_snippet.tags = tags_arr_to_str(update_snippet.tags)

    if update_snippet.theme is not None:
        update_snippet.theme = update_snippet.theme.strip()

    return update_snippet


def validate_delete_snippet(request: Request, uid: str):
    existing_snippet = db.query(Snippet).filter(Snippet.uid == uid).first()

    if existing_snippet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Snippet not found'
        )

    # check if the user requesting to delet ethe snippet is the owner of the snippet
    if request.state.user.get('id') != existing_snippet.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You don\'t have permission to delete this snippet'
        )

    return existing_snippet


def validate_snippet(request: Request, uid: str):
    snippet = db.query(Snippet).filter(Snippet.uid == uid).first()

    if snippet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Snippet not found'
        )

    if snippet.visibility == 2:  # private
        if hasattr(request.state, 'user') and request.state.user.get('id') == snippet.user_id:
            return snippet

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='This is a private snippet'
        )
    else:
        return snippet


def validate_edit_snippet(request: Request, uid: str):
    snippet = db.query(Snippet).filter(Snippet.uid == uid).first()

    if snippet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Snippet not found'
        )

    if hasattr(request.state, 'user') and request.state.user.get('id') == snippet.user_id:
        return snippet
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You are not autrhroized to edit this snippet'
        )
