from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse

from database import db
from middlewares import get_current_user
from models.ProgrammingLanguage import ProgrammingLanguage
from schemas.UserSchema import UserSchema

router = APIRouter()


@router.get('/languages')
def index(request: Request):
    try:
        languages = db.query(ProgrammingLanguage).all()
        languages = [language.serialize() for language in languages]
        return JSONResponse(status_code=200, content=languages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
