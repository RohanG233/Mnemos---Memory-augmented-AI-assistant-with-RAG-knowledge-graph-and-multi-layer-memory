from fastapi import APIRouter, HTTPException, Cookie
from fastapi.responses import (
    JSONResponse,
    RedirectResponse,
)

from datetime import datetime, timezone

from app.auth.security import create_access_token

from app.core.config import (
    REFRESH_TOKEN_EXPIRE_DAYS,
)

from app.services.auth_Service import (
    AuthService,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


auth_service = AuthService()


# -----------------------------
# Authentication Status
# -----------------------------

@router.get("/status")
def auth_status():

    return {
        "authentication": "configured"
    }


# -----------------------------
# Google Login
# -----------------------------

@router.get("/google")
def google_login():

    authorization_url, _ = (
        auth_service.get_google_authorization_url()
    )

    return JSONResponse(
        content={
            "authorization_url": authorization_url
        }
    )


# -----------------------------
# Google Callback
# -----------------------------

@router.get("/google/callback")
def google_callback(
    code: str,
    state: str,
):

    try:

        result = (
            auth_service.handle_google_callback(
                code=code,
                state=state,
            )
        )

        response = RedirectResponse(
            url="http://localhost:5173/chat",
            status_code=302,
        )

        # -----------------------------
        # Store Refresh Token
        # -----------------------------

        response.set_cookie(
            key="refresh_token",
            value=result["refresh_token"],
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=(
                REFRESH_TOKEN_EXPIRE_DAYS
                * 24
                * 60
                * 60
            ),
            path="/",
        )

        return response

    except Exception as error:

        raise HTTPException(
            status_code=400,
            detail=(
                "Google authentication failed: "
                f"{str(error)}"
            ),
        )


# -----------------------------
# Refresh Access Token
# -----------------------------

@router.post("/refresh")
def refresh_access_token(
    refresh_token: str | None = Cookie(
        default=None
    ),
):

    # -----------------------------
    # Check Refresh Token
    # -----------------------------

    if not refresh_token:

        raise HTTPException(
            status_code=401,
            detail="Refresh token missing",
        )

    # -----------------------------
    # Find User
    # -----------------------------

    user = auth_service.get_user_by_refresh_token(
        refresh_token
    )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
        )

    # -----------------------------
    # Check Expiration
    # -----------------------------

    expires_at = user.get(
        "refresh_token_expires_at"
    )

    if not expires_at:

        raise HTTPException(
            status_code=401,
            detail="Refresh token expiration missing",
        )

    if expires_at.tzinfo is None:

        expires_at = expires_at.replace(
            tzinfo=timezone.utc
        )

    if datetime.now(timezone.utc) >= expires_at:

        auth_service.remove_refresh_token(
            user["_id"]
        )

        raise HTTPException(
            status_code=401,
            detail="Refresh token has expired",
        )


    # -----------------------------
    # Create New Access Token
    # -----------------------------

    user_id = str(
        user["_id"]
    )

    access_token = create_access_token(
        user_id
    )

    # -----------------------------
    # Rotate Refresh Token
    # -----------------------------

    (
        new_refresh_token,
        new_expires_at,
    ) = auth_service.rotate_refresh_token(
        user
    )

    # -----------------------------
    # Create Response
    # -----------------------------

    response = JSONResponse(
        content={
            "access_token": access_token
        }
    )

    # -----------------------------
    # Replace Refresh Token Cookie
    # -----------------------------

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=(
            REFRESH_TOKEN_EXPIRE_DAYS
            * 24
            * 60
            * 60
        ),
        path="/",
    )

    return response

# -----------------------------
# Logout
# -----------------------------

@router.post("/logout")
def logout(
    refresh_token: str | None = Cookie(
        default=None
    ),
):

    # -----------------------------
    # Remove Refresh Token
    # -----------------------------

    if refresh_token:

        user = auth_service.get_user_by_refresh_token(
            refresh_token
        )

        if user:

            auth_service.remove_refresh_token(
                user["_id"]
            )

    # -----------------------------
    # Create Response
    # -----------------------------

    response = JSONResponse(
        content={
            "message": "Logout successful"
        }
    )

    # -----------------------------
    # Delete Refresh Cookie
    # -----------------------------

    response.delete_cookie(
        key="refresh_token",
        path="/",
    )

    return response