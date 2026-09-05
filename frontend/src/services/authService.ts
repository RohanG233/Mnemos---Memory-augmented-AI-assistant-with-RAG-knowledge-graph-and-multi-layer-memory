import { API_URL } from "./api";


interface RefreshResponse {
  access_token: string;
  refresh_token: string;
}


// --------------------------------
// Session storage keys
// --------------------------------

const REFRESH_TOKEN_KEY = "mnemos_refresh_token";

export function saveRefreshToken(token: string | null): void {
  if (token) {
    sessionStorage.setItem(REFRESH_TOKEN_KEY, token);
  } else {
    sessionStorage.removeItem(REFRESH_TOKEN_KEY);
  }
}

export function loadRefreshToken(): string | null {
  return sessionStorage.getItem(REFRESH_TOKEN_KEY);
}


// --------------------------------
// Start Google Login
// --------------------------------

export async function loginWithGoogle(): Promise<void> {

  const response = await fetch(
    `${API_URL}/auth/google`,
    { credentials: "include" }
  );

  if (!response.ok) {
    throw new Error("Failed to start Google login");
  }

  const data = await response.json();

  window.location.href = data.authorization_url;
}


// --------------------------------
// Refresh Access Token
// --------------------------------

export async function refreshAccessToken(): Promise<RefreshResponse> {

  const refreshToken = loadRefreshToken();

  const response = await fetch(
    `${API_URL}/auth/refresh`,
    {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        refresh_token: refreshToken,
      }),
    }
  );

  if (!response.ok) {
    throw new Error("Failed to refresh access token");
  }

  const data: RefreshResponse = await response.json();

  // Store the rotated refresh token
  saveRefreshToken(data.refresh_token);

  return data;
}


// --------------------------------
// Get Current User
// --------------------------------

export interface UserInfo {
  id: string;
  email: string;
  name: string;
  picture?: string;
}

export async function getCurrentUser(
  accessToken: string
): Promise<UserInfo> {

  const response = await fetch(
    `${API_URL}/auth/me`,
    {
      headers: { Authorization: `Bearer ${accessToken}` },
      credentials: "include",
    }
  );

  if (!response.ok) {
    throw new Error("Failed to fetch current user");
  }

  return response.json();
}


// --------------------------------
// Logout
// --------------------------------

export async function logout(): Promise<void> {

  const refreshToken = loadRefreshToken();

  const response = await fetch(
    `${API_URL}/auth/logout`,
    {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        refresh_token: refreshToken,
      }),
    }
  );

  // Clear the refresh token regardless of response
  saveRefreshToken(null);

  if (!response.ok) {
    throw new Error("Logout failed");
  }
}


// --------------------------------
// Extract OAuth tokens from URL
// Tokens are passed as hash fragments: /chat#access_token=...&refresh_token=...
// Hash fragments are never sent to the server and are never
// stripped by CDN rewrite rules — more reliable than query params.
// --------------------------------

export interface ExtractedTokens {
  accessToken: string | null;
  refreshToken: string | null;
}

export function extractTokensFromUrl(): ExtractedTokens {
  const result: ExtractedTokens = { accessToken: null, refreshToken: null };

  // Check hash fragment first (#access_token=...&refresh_token=...)
  const hash = window.location.hash;
  if (hash && hash.includes("access_token=")) {
    const params = new URLSearchParams(hash.slice(1)); // remove leading #
    const accessToken = params.get("access_token");
    const refreshToken = params.get("refresh_token");

    if (accessToken) {
      result.accessToken = accessToken;
    }
    if (refreshToken) {
      result.refreshToken = refreshToken;
    }

    // Remove the hash from the URL bar without reloading
    window.history.replaceState({}, "", window.location.pathname);
    return result;
  }

  // Fallback: check query parameter (?access_token=...) for backwards compat
  const queryParams = new URLSearchParams(window.location.search);
  const queryToken = queryParams.get("access_token");
  if (queryToken) {
    result.accessToken = queryToken;
    window.history.replaceState({}, "", window.location.pathname);
  }

  return result;
}
