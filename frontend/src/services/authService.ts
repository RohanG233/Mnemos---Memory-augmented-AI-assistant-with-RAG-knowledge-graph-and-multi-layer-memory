const API_URL = "http://localhost:8000";


interface RefreshResponse {
  access_token: string;
}


// --------------------------------
// Start Google Login
// --------------------------------

export async function loginWithGoogle() {

  const response = await fetch(
    `${API_URL}/auth/google`,
    {
      credentials: "include",
    }
  );

  if (!response.ok) {

    throw new Error(
      "Failed to start Google login"
    );
  }

  const data = await response.json();

  window.location.href =
    data.authorization_url;
}


// --------------------------------
// Refresh Access Token
// --------------------------------

export async function refreshAccessToken():
  Promise<string> {

  const response = await fetch(
    `${API_URL}/auth/refresh`,
    {
      method: "POST",

      credentials: "include",
    }
  );

  if (!response.ok) {

    throw new Error(
      "Failed to refresh access token"
    );
  }

  const data: RefreshResponse =
    await response.json();

  return data.access_token;
}


// --------------------------------
// Logout
// --------------------------------

export async function logout() {

  const response = await fetch(
    `${API_URL}/auth/logout`,
    {
      method: "POST",

      credentials: "include",
    }
  );

  if (!response.ok) {

    throw new Error(
      "Logout failed"
    );

  }

}