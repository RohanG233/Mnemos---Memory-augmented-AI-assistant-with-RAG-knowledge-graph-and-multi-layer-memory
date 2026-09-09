import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

import { extractTokensFromUrl, saveRefreshToken } from "../services/authService";
import { useAuth } from "../context/AuthContext";

function OAuthCallback() {
  const navigate = useNavigate();
  const { storeToken } = useAuth();

  useEffect(() => {
    // Extract tokens from URL (both hash fragments and query parameters)
    const urlTokens = extractTokensFromUrl();

    if (urlTokens.accessToken) {
      // Store access token
      storeToken(urlTokens.accessToken);

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
  }, [navigate, storeToken]);

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