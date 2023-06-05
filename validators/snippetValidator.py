from fastapi import HTTPException, Request, status

from database import db
from models.Snippet import Snippet
from models.User import User
from schemas.SnippetSchema import SnippetSchema


def check_valid_snippet(request: Request, snippet: SnippetSchema):
    snippet.title = snippet.title.strip()
    snippet.content = snippet.content.strip()
    snippet.share_with = snippet.share_with.strip() if snippet.share_with else None

    any_snippet = db.query(Snippet).filter(
        Snippet.title == snippet.title
    ).first()
    if any_snippet:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Snippet with this title already exist'
        )

    if (snippet.visibility == 2):
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

    return snippet
