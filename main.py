from os import environ

from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from database import Base, engine
from middlewares import authenticate
from routers import languages, snippets, users
from seeders import seed

app = FastAPI()
Base.metadata.create_all(engine)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    error_messages = {}
    status_code = 422
    for error in exc.errors():
        if len(error['loc']) > 1:
            error_messages[error['loc'][1]] = error['msg']
        else:
            status_code = 415
            error_messages[error['loc'][0]] = error['msg']

    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder({'detail': error_messages}),
    )


app.include_router(snippets.router)
app.include_router(users.router)
app.include_router(languages.router)
# app.include_router(seed.router)
# app.middleware('http')(authenticate)
