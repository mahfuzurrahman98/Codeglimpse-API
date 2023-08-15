from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from lib.data.languages import languages
from lib.data.themes import themes

router = APIRouter()


@router.get("/data/languages")
async def get_languages():
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'data': {
                'languages': languages
            }
        }
    )


@router.get("/data/themes")
async def get_themes():
	return JSONResponse(
		status_code=status.HTTP_200_OK,
		content={
			'data': {
				'themes': themes
			}
		}
	)
