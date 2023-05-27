from fastapi import FastAPI
from fastapi.middleware.authentication import JWTAuthMiddleware
from fastapi_jwt_auth import JWTAuth

app = FastAPI()

# Configure the JWT auth middleware
jwt = JWTAuth(secret='my_secret')
app.add_middleware(JWTAuthMiddleware, jwt=jwt)

# Define the login endpoint


@app.post("/login")
async def login(username: str, password: str):
    """Login endpoint.

    Args:
      username: The user's username.
      password: The user's password.

    Returns:
      A JSON response containing the access token and refresh token.
    """

    # Check if the user exists and the password is correct
    user = await get_user(username, password)
    if not user:
        return JSONResponse(status_code=401, content={"detail": "Invalid username or password"})

    # Generate the access and refresh tokens
    access_token = jwt.create_access_token(subject=user.id)
    refresh_token = jwt.create_refresh_token(subject=user.id)

    # Return the tokens
    return JSONResponse({
        "access_token": access_token,
        "refresh_token": refresh_token,
    })

# Define the refresh endpoint


@app.post("/refresh")
async def refresh(refresh_token: str):
    """Refresh endpoint.

    Args:
      refresh_token: The user's refresh token.

    Returns:
      A JSON response containing the new access token.
    """

    # Validate the refresh token
    try:
        user = await jwt.decode_refresh_token(refresh_token)
    except JWTDecodeError:
        return JSONResponse(status_code=401, content={"detail": "Invalid refresh token"})

    # Generate a new access token
    access_token = jwt.create_access_token(subject=user.id)

    # Return the new access token
    return JSONResponse({
        "access_token": access_token,
    })
