from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from seeders.fake_datas.programming_languages import programming_languages
from seeders.languageSeeder import seed_programming_languages

router = APIRouter()


@router.post('/seed/languages')
def register():
    try:
        seed_programming_languages(programming_languages)
        return JSONResponse(status_code=201, content={'detail': 'Languages are inserted'})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
