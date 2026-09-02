// API base URL — set VITE_API_URL in .env (dev) or .env.production (prod)
const API_URL: string =
  import.meta.env.VITE_API_URL ?? "http://localhost:8000";


let refreshHandler: (() => Promise<string | null>) | null = null;


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

  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };

  if (accessToken) {
    headers["Authorization"] = `Bearer ${accessToken}`;
  }

  // Always send cookies so the refresh-token cookie is
  // included when the browser calls /auth/refresh.
  const requestInit: RequestInit = {
    ...options,
    headers,
    credentials: "include",
  };

  const response = await fetch(`${API_URL}${endpoint}`, requestInit);

  // Not a 401 — return as-is
  if (response.status !== 401) {
    return response;
  }

  // No refresh handler registered
  if (!refreshHandler) {
    return response;
  }

  // Attempt token refresh
  const newAccessToken = await refreshHandler();

  if (!newAccessToken) {
    return response;
  }

  // Retry with new token
  return fetch(`${API_URL}${endpoint}`, {
    ...requestInit,
    headers: {
      ...headers,
      Authorization: `Bearer ${newAccessToken}`,
    },
  });
}


// Export base URL so other services can construct URLs if needed
export { API_URL };
