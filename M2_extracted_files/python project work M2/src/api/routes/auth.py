"""Authentication API endpoints (M2).
Implements user registration, login, and profile access.
"""

from typing import Any
try:
    from fastapi import APIRouter, Depends, HTTPException, status
    HAS_FASTAPI = True
except ImportError:  # pragma: no cover
    HAS_FASTAPI = False
    APIRouter = object

from src.core.database import get_db
from src.core.security import create_access_token
from src.schemas.user import Token, UserCreate, UserLogin, UserResponse
from src.services.user_service import DuplicateEmailError, DuplicateUsernameError, UserService

if HAS_FASTAPI:
    router = APIRouter(prefix="/auth", tags=["Authentication"])

    @router.post(
        "/register",
        response_model=UserResponse,
        status_code=status.HTTP_201_CREATED,
        summary="Register a new user account",
    )
    def register_user(
        user_in: UserCreate,
        db: Any = Depends(get_db),
    ) -> Any:
        """Register a new user with email and field validation, and duplicate checking."""
        try:
            user = UserService.create_user(db, user_in)
            return user
        except DuplicateEmailError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(exc),
            ) from exc
        except DuplicateUsernameError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(exc),
            ) from exc

    @router.post(
        "/login",
        response_model=Token,
        summary="Authenticate user and return access token",
    )
    def login_user(
        login_data: UserLogin,
        db: Any = Depends(get_db),
    ) -> Any:
        """Authenticate user with username or email and password."""
        user = UserService.authenticate_user(
            db, login_data.username_or_email, login_data.password
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username/email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username}
        )
        return {"access_token": access_token, "token_type": "bearer"}

else:  # pragma: no cover
    router = None
