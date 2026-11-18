"""Authentication API endpoints (M2).
Implements user registration, login, profile access, and profile update.
"""

from typing import Any
try:
    from fastapi import APIRouter, Depends, HTTPException, status
    from fastapi.security import OAuth2PasswordRequestForm
    HAS_FASTAPI = True
except ImportError:  # pragma: no cover
    HAS_FASTAPI = False
    APIRouter = object

from src.core.database import get_db
from src.core.security import create_access_token, get_current_user_id
from src.schemas.user import Token, UserCreate, UserLogin, UserResponse, UserUpdate
from src.services.user_service import (
    DuplicateEmailError,
    DuplicateUsernameError,
    UserNotFoundError,
    UserService,
)

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
        """Authenticate user with username or email and password (JSON body)."""
        user = UserService.authenticate_user(
            db, login_data.username_or_email, login_data.password
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username/email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Reject inactive users
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive.",
            )

        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username}
        )
        return {"access_token": access_token, "token_type": "bearer"}

    @router.post(
        "/token",
        response_model=Token,
        summary="OAuth2-compatible login (form data)",
        include_in_schema=True,
    )
    def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Any = Depends(get_db),
    ) -> Any:
        """OAuth2-compatible login endpoint that accepts form-encoded username + password.
        This powers the Swagger UI 'Authorize' button.
        """
        user = UserService.authenticate_user(
            db, form_data.username, form_data.password
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username/email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive.",
            )

        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username}
        )
        return {"access_token": access_token, "token_type": "bearer"}

    @router.get(
        "/me",
        response_model=UserResponse,
        summary="Get current authenticated user profile",
    )
    def get_current_user_profile(
        user_id: int = Depends(get_current_user_id),
        db: Any = Depends(get_db),
    ) -> Any:
        """Return the profile of the currently authenticated user."""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive.",
            )
        return user

    @router.patch(
        "/me",
        response_model=UserResponse,
        summary="Update current user profile",
    )
    def update_current_user_profile(
        user_update: UserUpdate,
        user_id: int = Depends(get_current_user_id),
        db: Any = Depends(get_db),
    ) -> Any:
        """Update the profile of the currently authenticated user."""
        try:
            user = UserService.update_user(db, user_id, user_update)
            return user
        except UserNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc
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

else:  # pragma: no cover
    router = None
