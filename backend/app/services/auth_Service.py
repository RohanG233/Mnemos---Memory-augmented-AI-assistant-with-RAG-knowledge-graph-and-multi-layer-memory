from datetime import datetime, timezone, timedelta

from requests_oauthlib import OAuth2Session

from app.auth.security import (
    create_access_token,
    create_refresh_token,
)

from app.core.config import (
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_REDIRECT_URI,
    GOOGLE_AUTHORIZATION_URL,
    GOOGLE_TOKEN_URL,
    GOOGLE_USER_INFO_URL,
    GOOGLE_SCOPES,
    REFRESH_TOKEN_EXPIRE_DAYS,
)

from app.core.database import users_collection


class AuthService:

    # -----------------------------
    # Create Google Authorization URL
    # -----------------------------

    def get_google_authorization_url(self):

        google = OAuth2Session(
            GOOGLE_CLIENT_ID,
            redirect_uri=GOOGLE_REDIRECT_URI,
            scope=GOOGLE_SCOPES,
        )

        authorization_url, state = (
            google.authorization_url(
                GOOGLE_AUTHORIZATION_URL
            )
        )

        return authorization_url, state


        # -----------------------------
    # Get User By Refresh Token
    # -----------------------------

    def get_user_by_refresh_token(
        self,
        refresh_token: str,
    ):

        return users_collection.find_one(
            {
                "refresh_token": refresh_token
            }
        )


    # -----------------------------
    # Remove Refresh Token
    # -----------------------------

    def remove_refresh_token(
        self,
        user_id,
    ):

        users_collection.update_one(
            {
                "_id": user_id
            },
            {
                "$unset": {
                    "refresh_token": "",
                    "refresh_token_expires_at": "",
                }
            }
        )


    # -----------------------------
    # Handle Google Callback
    # -----------------------------

    def handle_google_callback(
        self,
        code: str,
        state: str,
    ):

        google = OAuth2Session(
            GOOGLE_CLIENT_ID,
            redirect_uri=GOOGLE_REDIRECT_URI,
            state=state,
            scope=GOOGLE_SCOPES,
        )

        # -----------------------------
        # Exchange authorization code
        # -----------------------------

        google.fetch_token(
            GOOGLE_TOKEN_URL,
            code=code,
            client_secret=GOOGLE_CLIENT_SECRET,
        )

        # -----------------------------
        # Get Google User Information
        # -----------------------------

        response = google.get(
            GOOGLE_USER_INFO_URL
        )

        response.raise_for_status()

        user_info = response.json()

        google_id = user_info["id"]

        # -----------------------------
        # Find Existing User
        # -----------------------------

        user = users_collection.find_one(
            {
                "google_id": google_id
            }
        )

        # -----------------------------
        # Create User
        # -----------------------------

        if not user:

            new_user = {
                "google_id": google_id,
                "email": user_info["email"],
                "name": user_info["name"],
                "picture": user_info.get("picture"),
                "created_at": datetime.now(
                    timezone.utc
                ),
            }

            result = users_collection.insert_one(
                new_user
            )

            user = users_collection.find_one(
                {
                    "_id": result.inserted_id
                }
            )

        # -----------------------------
        # User ID
        # -----------------------------

        user_id = str(
            user["_id"]
        )

        # -----------------------------
        # Create Access Token
        # -----------------------------

        access_token = create_access_token(
            user_id
        )

        # -----------------------------
        # Create Refresh Token
        # -----------------------------

        refresh_token = create_refresh_token()

        refresh_token_expires_at = (
            datetime.now(timezone.utc)
            + timedelta(
                days=REFRESH_TOKEN_EXPIRE_DAYS
            )
        )

        # -----------------------------
        # Store Refresh Token
        # -----------------------------

        users_collection.update_one(
            {
                "_id": user["_id"]
            },
            {
                "$set": {
                    "refresh_token": refresh_token,
                    "refresh_token_expires_at":
                        refresh_token_expires_at,
                }
            }
        )

        # -----------------------------
        # Return Authentication Result
        # -----------------------------

        return {
            "access_token": access_token,

            "refresh_token": refresh_token,

            "user": {
                "id": user_id,
                "google_id": user["google_id"],
                "email": user["email"],
                "name": user["name"],
                "picture": user.get("picture"),
            },
        }


    def get_user_by_refresh_token(
        self,
        refresh_token: str,
    ):

        return users_collection.find_one(
            {
                "refresh_token": refresh_token
            }
        )


    # -----------------------------
    # Remove Refresh Token
    # -----------------------------

    def remove_refresh_token(
        self,
        user_id,
    ):

        users_collection.update_one(
            {
                "_id": user_id
            },
            {
                "$unset": {
                    "refresh_token": "",
                    "refresh_token_expires_at": "",
                }
            }
        )


        # -----------------------------
    # Rotate Refresh Token
    # -----------------------------

    def rotate_refresh_token(
        self,
        user,
    ):

        new_refresh_token = create_refresh_token()

        new_expires_at = (
            datetime.now(timezone.utc)
            + timedelta(
                days=REFRESH_TOKEN_EXPIRE_DAYS
            )
        )

        users_collection.update_one(
            {
                "_id": user["_id"]
            },
            {
                "$set": {
                    "refresh_token": new_refresh_token,
                    "refresh_token_expires_at":
                        new_expires_at,
                }
            }
        )

        return (
            new_refresh_token,
            new_expires_at,
        )