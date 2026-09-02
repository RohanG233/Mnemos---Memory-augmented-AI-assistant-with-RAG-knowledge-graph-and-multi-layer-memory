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
// (set by backend callback redirect)
// --------------------------------

export function extractAccessTokenFromUrl(): string | null {
  const params = new URLSearchParams(window.location.search);
  const token = params.get("access_token");

  if (token) {
    // Remove from URL bar without triggering a page reload
    const cleanUrl = window.location.pathname;
    window.history.replaceState({}, "", cleanUrl);
  }

  return token;
}
