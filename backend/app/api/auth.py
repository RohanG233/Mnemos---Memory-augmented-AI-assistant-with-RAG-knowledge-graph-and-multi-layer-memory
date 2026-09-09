import logging
import os
from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Cookie, Depends, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel

from app.auth.dependencies import get_current_user
from app.auth.security import create_access_token
from app.core.config import (
    FRONTEND_URL,
    REFRESH_TOKEN_EXPIRE_DAYS,
)
from app.core.database import users_collection
from app.services.auth_Service import AuthService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

auth_service = AuthService()

# Use secure cookies in production (HTTPS).
# Set COOKIE_SECURE=false only for local HTTP development.
_REFRESH_MAX_AGE = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60


def _set_refresh_cookie(response, refresh_token: str) -> None:
    """Attach the HttpOnly refresh-token cookie to a response (best-effort fallback)."""
    cookie_secure = os.getenv("COOKIE_SECURE", "true").lower() != "false"
    cookie_samesite = "none" if cookie_secure else "lax"

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=cookie_secure,
        samesite=cookie_samesite,
        max_age=_REFRESH_MAX_AGE,
        path="/",
    )


# -----------------------------
# Request body schemas
# -----------------------------

class RefreshRequest(BaseModel):
    refresh_token: Optional[str] = None

class LogoutRequest(BaseModel):
    refresh_token: Optional[str] = None


# -----------------------------
# Authentication Status
# -----------------------------

@router.get("/status")
def auth_status():
    return {"authentication": "configured"}


# -----------------------------
# Current User
# -----------------------------

@router.get("/me")
def get_me(user_id: str = Depends(get_current_user)):
    try:
        oid = ObjectId(user_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    user = users_collection.find_one({"_id": oid})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user_id,
        "email": user.get("email"),
        "name": user.get("name"),
        "picture": user.get("picture"),
    }


# -----------------------------
# Google Login
# -----------------------------

@router.get("/google")
def google_login():
    authorization_url, _ = auth_service.get_google_authorization_url()
    return JSONResponse(content={"authorization_url": authorization_url})


# -----------------------------
# Google Callback
# -----------------------------

@router.get("/google/callback")
def google_callback(code: str, state: str):
    try:
        result = auth_service.handle_google_callback(code=code, state=state)
    except Exception:
        logger.exception("Google OAuth callback failed")
        raise HTTPException(
            status_code=400,
            detail="Google authentication failed.",
        )

    # Redirect to the frontend chat page.
    # Pass both access_token AND refresh_token as URL hash fragments.
    # Hash fragments are never sent to the server and are never
    # stripped by CDN rewrite rules — safer than query parameters.
    redirect_url = (
        f"{FRONTEND_URL}/chat"
        f"#access_token={result['access_token']}"
        f"&refresh_token={result['refresh_token']}"
    )

    response = RedirectResponse(url=redirect_url, status_code=302)
    # Still set cookie as a best-effort fallback for same-origin setups
    _set_refresh_cookie(response, result["refresh_token"])
    return response


# -----------------------------
# Refresh Access Token
# -----------------------------

@router.post("/refresh")
def refresh_access_token(
    body: RefreshRequest = None,
    refresh_token: str | None = Cookie(default=None),
):
    # Prefer the body token; fall back to cookie for backwards compat
    token = None
    if body and body.refresh_token:
        token = body.refresh_token
    elif refresh_token:
        token = refresh_token

    if not token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    user = auth_service.get_user_by_refresh_token(token)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    expires_at = user.get("refresh_token_expires_at")

    if not expires_at:
        raise HTTPException(status_code=401, detail="Refresh token expiration missing")

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if datetime.now(timezone.utc) >= expires_at:
        auth_service.remove_refresh_token(user["_id"])
        raise HTTPException(status_code=401, detail="Refresh token has expired")

    user_id = str(user["_id"])
    access_token = create_access_token(user_id)

    new_refresh_token, _ = auth_service.rotate_refresh_token(user)

    response = JSONResponse(content={
        "access_token": access_token,
        "refresh_token": new_refresh_token,
    })
    # Still set cookie as a best-effort fallback
    _set_refresh_cookie(response, new_refresh_token)
    return response


# -----------------------------
# Logout
# -----------------------------

@router.post("/logout")
def logout(
    body: LogoutRequest = None,
    refresh_token: str | None = Cookie(default=None),
):
    # Prefer body token; fall back to cookie
    token = None
    if body and body.refresh_token:
        token = body.refresh_token
    elif refresh_token:
        token = refresh_token

    if token:
        user = auth_service.get_user_by_refresh_token(token)
        if user:
            auth_service.remove_refresh_token(user["_id"])

    response = JSONResponse(content={"message": "Logout successful"})
    cookie_secure = os.getenv("COOKIE_SECURE", "true").lower() != "false"
    cookie_samesite = "none" if cookie_secure else "lax"
    response.delete_cookie(
        key="refresh_token",
        path="/",
        httponly=True,
        secure=cookie_secure,
        samesite=cookie_samesite,
    )
    return response
