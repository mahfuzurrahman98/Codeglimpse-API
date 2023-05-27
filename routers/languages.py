from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from database import db
from models.ProgrammingLanguage import ProgrammingLanguage
from seeders.fake_datas.programming_languages import programming_languages

router = APIRouter()

# @router.post('/seed/languages')
# def register():
#     try:
#         for language in programming_languages:
#             name = language['name']
#             alt_name = language['alt_name']
#             active = 1  # Adjust the value as needed

#             programming_language = ProgrammingLanguage(
#                 name=name,
#                 alt_name=alt_name,
#                 active=active
#             )

#             db.add(programming_language)

#         db.commit()
#         db.close()

#         resp = {
#             'detail': 'Languages created',
#         }
#         return JSONResponse(status_code=201, content=resp)

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


@router.get('/languages')
def index():
    try:
        languages = db.query(ProgrammingLanguage).all()
        languages = [language.serialize() for language in languages]
        return JSONResponse(status_code=200, content=languages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
