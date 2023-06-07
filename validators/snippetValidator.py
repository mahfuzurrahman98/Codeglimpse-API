from fastapi import HTTPException, Request, status

from database import db
from models.Snippet import Snippet
from models.User import User
from schemas.SnippetSchema import createSnippetSchema, updateSnippetSchema


def check_protected_snippet(request: Request, snippet: Snippet):
    if (snippet.share_with is None):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='mention the user ids'
        )

    share_with_ids = snippet.share_with.strip().split(',')
    # print(share_with_ids)
    if (len(share_with_ids) == 0):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='mention the user ids by comma separated'
        )

    for user_id in share_with_ids:
        try:
            int(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='each user id must be an integer'
            )

    for user_id in share_with_ids:
        if (request.state.user.get('id') == int(user_id)):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='You don\'t need to share with yourself'
            )
        user = db.query(User).filter(User.id == user_id).first()
        if (user is None):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f'{user_id} not a valid user id'
            )


def validate_new_snippet(request: Request, snippet: createSnippetSchema):
    snippet.title = snippet.title.strip()
    snippet.content = snippet.content.strip()
    snippet.share_with = snippet.share_with.strip() if snippet.share_with else None

    conflicting_snippet = db.query(Snippet).filter(
        Snippet.title == snippet.title
    ).first()
    if conflicting_snippet:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Snippet with this title already exist'
        )

    if (snippet.visibility == 2):
        check_protected_snippet(request, snippet)

    return snippet


def validate_update_snippet(request: Request, id: int, update_snippet: updateSnippetSchema):
    existing_snippet = db.query(Snippet).filter(Snippet.id == id).first()

    if existing_snippet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Snippet not found'
        )

    if update_snippet.title is not None:
        update_snippet.title = update_snippet.title.strip()

        # Check if the updated title conflicts with any other snippet
        conflicting_snippet = db.query(Snippet).filter(
            Snippet.title == update_snippet.title,
            Snippet.id != existing_snippet.id
        ).first()
        if conflicting_snippet:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Snippet with this title already exists'
            )

    if update_snippet.content is not None:
        update_snippet.content = update_snippet.content.strip()

    if update_snippet.visibility is not None:
        if update_snippet.visibility == 2:
            check_protected_snippet(request, update_snippet)
        else:
            update_snippet.share_with = ''

    return update_snippet


def validate_delete_snippet(request: Request, id: int):
    existing_snippet = db.query(Snippet).filter(Snippet.id == id).first()

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
