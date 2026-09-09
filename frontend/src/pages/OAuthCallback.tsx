import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

import { extractTokensFromUrl, saveRefreshToken } from "../services/authService";

function OAuthCallback() {
  const navigate = useNavigate();

  useEffect(() => {
    // Extract tokens from URL (both hash fragments and query parameters)
    const urlTokens = extractTokensFromUrl();

    if (urlTokens.accessToken) {
      // Store access token in sessionStorage
      sessionStorage.setItem("mnemos_access_token", urlTokens.accessToken);

      // Store refresh token if present
      if (urlTokens.refreshToken) {
        saveRefreshToken(urlTokens.refreshToken);
      }

      // Redirect to chat page
      navigate("/chat");
    } else {
      // No tokens found - redirect to login with error
      navigate("/login");
    }
  }, [navigate]);

  return (
    <div style={{
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      height: "100vh",
      fontSize: "18px",
      color: "#666"
    }}>
      Processing authentication...
    </div>
  );
}

export default OAuthCallback;