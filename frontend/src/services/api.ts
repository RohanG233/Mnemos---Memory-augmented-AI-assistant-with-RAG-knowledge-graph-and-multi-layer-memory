import { refreshAccessToken } from "./authService";

const API_URL = "http://localhost:8000";


let refreshHandler:
  | (() => Promise<string | null>)
  | null = null;


// -----------------------------
// Register Refresh Handler
// -----------------------------

export function setRefreshHandler(
  handler: () => Promise<string | null>
) {
  refreshHandler = handler;
}


// -----------------------------
// API Fetch
// -----------------------------

export async function apiFetch(
  endpoint: string,
  options: RequestInit = {},
  accessToken: string | null
): Promise<Response> {

  // -----------------------------
  // Send Original Request
  // -----------------------------

  const response = await fetch(
    `${API_URL}${endpoint}`,
    {
      ...options,

      headers: {
        ...options.headers,

        ...(accessToken
          ? {
              Authorization:
                `Bearer ${accessToken}`,
            }
          : {}),
      },
    }
  );

  // -----------------------------
  // Request Successful
  // -----------------------------

  if (response.status !== 401) {
    return response;
  }

  // -----------------------------
  // No Refresh Handler
  // -----------------------------

  if (!refreshHandler) {
    return response;
  }

  // -----------------------------
  // Refresh Access Token
  // -----------------------------

  const newAccessToken =
    await refreshHandler();

  if (!newAccessToken) {
    return response;
  }

  // -----------------------------
  // Retry Original Request
  // -----------------------------

  return fetch(
    `${API_URL}${endpoint}`,
    {
      ...options,

      headers: {
        ...options.headers,

        Authorization:
          `Bearer ${newAccessToken}`,
      },
    }
  );
}