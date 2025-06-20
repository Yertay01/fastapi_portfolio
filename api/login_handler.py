from datetime import timedelta
from typing import Union

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

import settings
from api.schemas import Token
from db.dals import UserDAL
from db.models import User
from db.session import get_db
from hashing import Hasher
from security import create_access_token

from api.actions.auth import authenticate_user
from api.actions.auth import get_current_user_from_token
from api.schemas import Token
from db.session import get_db
from security import create_access_token

login_router = APIRouter()

    
@login_router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data = {"sub": user.email, "other_custom_data": [1,2,3,4]},
        expires_delta = access_token_expires,
    )                              
    return {"access_token": access_token, "token_type": "bearer"}


@login_router.get("/test_auth_endpoint")
async def sample_endpoint_under_jwt(
    current_user: User = Depends(get_current_user_from_token)
):
    return {"Success": True, "current_user": current_user}