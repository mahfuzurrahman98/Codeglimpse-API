from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from jose import JWTError
from passlib.exc import UnknownHashError

from database import db
from models.ProgrammingLanguage import ProgrammingLanguage
from models.Snippet import Snippet
from schemas.SnippetSchema import SnippetSchema

router = APIRouter()
