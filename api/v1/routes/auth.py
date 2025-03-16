from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from supabase import Client

from api.exceptions import (
    EmailNotConfirmedException,
    InvalidCredentialsException,
    UserAlreadyExistsException,
)
from api.v1.schemas import auth as auth_schemas
from api.v1.services import auth_service
from core.supabase import get_supabase_client

router = APIRouter()


@router.post("/signup", response_model=auth_schemas.SignupResponse)
async def signup_email_password(
    user_create: auth_schemas.UserCreate,
    supabase_client: Client = Depends(get_supabase_client),
):
    try:
        token_data = await auth_service.signup_with_email_password(
            supabase_client, user_create
        )
        return token_data
    except UserAlreadyExistsException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        if "is invalid" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Signup failed: {e}",
        )


@router.post("/login", response_model=auth_schemas.Token)
async def login_email_password(
    form_data: auth_schemas.UserLogin,
    supabase_client: Client = Depends(get_supabase_client),
):
    try:
        token_data = await auth_service.login_with_email_password(
            supabase_client, form_data.email, form_data.password
        )
        return token_data
    except InvalidCredentialsException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except EmailNotConfirmedException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {e}",
        )
