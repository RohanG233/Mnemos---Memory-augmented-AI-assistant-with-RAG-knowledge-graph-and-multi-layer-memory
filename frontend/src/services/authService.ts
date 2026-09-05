import { API_URL } from "./api";


interface RefreshResponse {
  access_token: string;
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

export async function refreshAccessToken(): Promise<string> {

  const response = await fetch(
    `${API_URL}/auth/refresh`,
    {
      method: "POST",
      credentials: "include",
    }
  );

  if (!response.ok) {
    throw new Error("Failed to refresh access token");
  }

  const data: RefreshResponse = await response.json();

  return data.access_token;
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

  const response = await fetch(
    `${API_URL}/auth/logout`,
    {
      method: "POST",
      credentials: "include",
    }
  );

  if (!response.ok) {
    throw new Error("Logout failed");
  }
}


// --------------------------------
// Extract OAuth access_token from URL
// Token is passed as a hash fragment: /chat#access_token=...
// Hash fragments are never sent to the server and are never
// stripped by CDN rewrite rules — more reliable than query params.
// --------------------------------

export function extractAccessTokenFromUrl(): string | null {
  // Check hash fragment first (#access_token=...)
  const hash = window.location.hash;
  if (hash && hash.includes("access_token=")) {
    const params = new URLSearchParams(hash.slice(1)); // remove leading #
    const token = params.get("access_token");
    if (token) {
      // Remove the hash from the URL bar without reloading
      window.history.replaceState({}, "", window.location.pathname);
      return token;
    }
  }

  // Fallback: check query parameter (?access_token=...) for backwards compat
  const queryParams = new URLSearchParams(window.location.search);
  const queryToken = queryParams.get("access_token");
  if (queryToken) {
    window.history.replaceState({}, "", window.location.pathname);
    return queryToken;
  }

  return null;
}
