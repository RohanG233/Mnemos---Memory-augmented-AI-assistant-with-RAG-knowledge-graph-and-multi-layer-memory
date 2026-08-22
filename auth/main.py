from fastapi import FastAPI
from fastapi import Response, Header, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from requests_oauthlib import OAuth2Session
from bson import ObjectId
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from pymongo import MongoClient
from pydantic import BaseModel
from dotenv import load_dotenv

from jose import jwt
from fastapi import Response
import secrets
from fastapi import Cookie

from datetime import datetime, timezone, timedelta
import os


# Load environment variables
load_dotenv()

print("CLIENT ID:", os.getenv("GOOGLE_CLIENT_ID"))
print(
    "CLIENT SECRET LOADED:",
    os.getenv("GOOGLE_CLIENT_SECRET") is not None
)

app = FastAPI()
security = HTTPBearer()

# =========================================================
# MongoDB
# =========================================================

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)

db = client["acai"]

users_collection = db["users"]


# =========================================================
# User Model
# =========================================================

class User(BaseModel):
    google_id: str
    email: str
    name: str
    picture: str | None = None
    created_at: datetime


# Make Google ID unique
users_collection.create_index(
    "google_id",
    unique=True
)


# =========================================================
# Google OAuth Configuration
# =========================================================

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

REDIRECT_URI = "http://localhost:8000/auth/google/callback"

AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/auth"

TOKEN_URL = "https://oauth2.googleapis.com/token"

USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]


JWT_SECRET = os.getenv("JWT_SECRET")
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7



def create_access_token(user_id: str):
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "user_id": user_id,
        "exp": expire
    }
    token = jwt.encode(
        payload,
        JWT_SECRET,
        algorithm="HS256"
    )
    return token



def create_refresh_token():
    return secrets.token_urlsafe(64)


def verify_access_token(token: str):

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=["HS256"]
        )

        user_id = payload.get("user_id")

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid access token"
            )

        return user_id

    except jwt.ExpiredSignatureError:

        raise HTTPException(
            status_code=401,
            detail="Access token has expired"
        )

    except jwt.JWTError:

        raise HTTPException(
            status_code=401,
            detail="Invalid access token"
        )

# =========================================================
# Home
# =========================================================

@app.get("/")
def home():

    return {
        "message": "Home page"
    }


# =========================================================
# Google Login
# =========================================================

@app.get("/auth/google")
def google_login():

    google = OAuth2Session(
        CLIENT_ID,
        redirect_uri=REDIRECT_URI,
        scope=SCOPES
    )

    authorization_url, state = google.authorization_url(
        AUTHORIZATION_URL
    )

    return RedirectResponse(authorization_url)


@app.get("/test-cookie")
def test_cookie():

    response = JSONResponse(
        content={"message": "Cookie test"}
    )

    response.set_cookie(
        key="test_cookie",
        value="hello",
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=3600,
        path="/"
    )

    return response


@app.get("/auth/me")
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    access_token = credentials.credentials

    user_id = verify_access_token(access_token)

    user = users_collection.find_one({
        "_id": ObjectId(user_id)
    })

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "id": str(user["_id"]),
        "google_id": user["google_id"],
        "email": user["email"],
        "name": user["name"],
        "picture": user.get("picture")
    }


@app.post("/auth/refresh")
def refresh_access_token(
    refresh_token: str | None = Cookie(default=None)
):

    if not refresh_token:
        raise HTTPException(
            status_code=401,
            detail="Refresh token missing"
        )

    user = users_collection.find_one({
        "refresh_token": refresh_token
    })

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    expires_at = user.get("refresh_token_expires_at")

    if not expires_at:
        raise HTTPException(
            status_code=401,
            detail="Refresh token expiration missing"
        )

    # MongoDB may return a timezone-aware datetime,
    # but normalize it just in case.
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if datetime.now(timezone.utc) >= expires_at:

        users_collection.update_one(
            {"_id": user["_id"]},
            {
                "$unset": {
                    "refresh_token": "",
                    "refresh_token_expires_at": ""
                }
            }
        )

        raise HTTPException(
            status_code=401,
            detail="Refresh token has expired"
        )

    user_id = str(user["_id"])

    access_token = create_access_token(user_id)

    return {
        "access_token": access_token
    }


@app.post("/auth/logout")
def logout(
    refresh_token: str | None = Cookie(default=None)
):

    if refresh_token:
        users_collection.update_one(
            {"refresh_token": refresh_token},
            {
                "$unset": {
                    "refresh_token": "",
                    "refresh_token_expires_at": ""
                }
            }
        )

    response = JSONResponse(
        content={
            "message": "Logout successful"
        }
    )

    response.delete_cookie(
        key="refresh_token",
        path="/"
    )

    return response



# def verify_access_token(token: str):

#     print("TOKEN RECEIVED:", token)

#     try:
#         payload = jwt.decode(
#             token,
#             JWT_SECRET,
#             algorithms=["HS256"]
#         )

#         print("DECODED PAYLOAD:", payload)

#         user_id = payload.get("user_id")

#         if not user_id:
#             raise HTTPException(
#                 status_code=401,
#                 detail="user_id missing from token"
#             )

#         return user_id

#     except jwt.ExpiredSignatureError:
#         print("TOKEN EXPIRED")

#         raise HTTPException(
#             status_code=401,
#             detail="Access token has expired"
#         )

#     except jwt.JWTError as e:
#         print("JWT ERROR:", e)

#         raise HTTPException(
#             status_code=401,
#             detail=f"Invalid access token: {str(e)}"
#         )

# =========================================================
# Google Callback
# =========================================================

@app.get("/auth/google/callback")
def google_callback(code: str, state: str):

    google = OAuth2Session(
        CLIENT_ID,
        redirect_uri=REDIRECT_URI,
        state=state,
        scope=SCOPES
    )

    # Exchange Google authorization code for tokens
    token = google.fetch_token(
        TOKEN_URL,
        code=code,
        client_secret=CLIENT_SECRET
    )

    # Get Google user information
    response = google.get(USER_INFO_URL)
    user_info = response.json()

    google_id = user_info["id"]

    # Check if user already exists
    user = users_collection.find_one({
        "google_id": google_id
    })

    # Create new user if necessary
    if not user:

        new_user = {
            "google_id": google_id,
            "email": user_info["email"],
            "name": user_info["name"],
            "picture": user_info.get("picture"),
            "created_at": datetime.now(timezone.utc)
        }

        result = users_collection.insert_one(new_user)

        user = users_collection.find_one({
            "_id": result.inserted_id
        })

        print("New user created:", user["email"])

    else:

        print("Existing user:", user["email"])

    # =====================================================
    # Create application tokens
    # =====================================================

    user_id = str(user["_id"])

    access_token = create_access_token(user_id)

    refresh_token = create_refresh_token()

    refresh_token_expires_at = (
        datetime.now(timezone.utc)
        + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )

    print("NEW REFRESH TOKEN:", refresh_token)
    print(
        "NEW REFRESH TOKEN EXPIRES:",
        refresh_token_expires_at
    )

    # =====================================================
    # Store refresh token in MongoDB
    # =====================================================

    users_collection.update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "refresh_token": refresh_token,
                "refresh_token_expires_at": refresh_token_expires_at
            }
        }
    )

    # Get updated user from MongoDB
    user = users_collection.find_one({
        "_id": user["_id"]
    })

    # =====================================================
    # Create response
    # =====================================================

    response = JSONResponse(
        content={
            "message": "Google login successful",

            "access_token": access_token,

            "user": {
                "id": str(user["_id"]),
                "google_id": user["google_id"],
                "email": user["email"],
                "name": user["name"],
                "picture": user.get("picture")
            }
        }
    )

    # Store refresh token in HttpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/"
    )

    return response