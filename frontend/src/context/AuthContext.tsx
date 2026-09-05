import {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";

import type { ReactNode } from "react";

import {
  loginWithGoogle,
  refreshAccessToken,
  logout as logoutRequest,
  extractAccessTokenFromUrl,
} from "../services/authService";

import { setRefreshHandler } from "../services/api";


// sessionStorage key — survives page refresh but not tab close.
// Used as a fallback when the HttpOnly cookie is blocked cross-origin.
const SESSION_TOKEN_KEY = "mnemos_access_token";

function saveSession(token: string | null) {
  if (token) {
    sessionStorage.setItem(SESSION_TOKEN_KEY, token);
  } else {
    sessionStorage.removeItem(SESSION_TOKEN_KEY);
  }
}

function loadSession(): string | null {
  return sessionStorage.getItem(SESSION_TOKEN_KEY);
}


interface AuthContextType {
  accessToken: string | null;
  loading: boolean;
  login: () => Promise<void>;
  refresh: () => Promise<string | null>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);


export function AuthProvider({ children }: { children: ReactNode }) {

  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const hasRestoredRef = useRef(false);


  function storeToken(token: string | null) {
    saveSession(token);
    setAccessToken(token);
  }


  useEffect(() => {
    if (hasRestoredRef.current) return;
    hasRestoredRef.current = true;

    async function restoreAuth() {

      // 1. Fresh OAuth callback — token is in the URL hash fragment
      //    (#access_token=...). Clear any stale session first.
      const urlToken = extractAccessTokenFromUrl();
      if (urlToken) {
        saveSession(null); // clear stale token before storing new one
        storeToken(urlToken);
        setLoading(false);
        return;
      }

      // 2. Page refresh — reuse session token if present.
      //    Validate it by calling /auth/me before trusting it.
      const sessionToken = loadSession();
      if (sessionToken) {
        try {
          // Quick validation: if /auth/me returns 200, token is still valid
          const { API_URL } = await import("../services/api");
          const res = await fetch(`${API_URL}/auth/me`, {
            headers: { Authorization: `Bearer ${sessionToken}` },
            credentials: "include",
          });
          if (res.ok) {
            setAccessToken(sessionToken);
            setLoading(false);
            return;
          }
          // Token rejected — try to refresh silently
          saveSession(null);
        } catch {
          saveSession(null);
        }
      }

      // 3. Try HttpOnly cookie refresh (works when cookie is not blocked)
      try {
        const token = await refreshAccessToken();
        storeToken(token);
      } catch {
        // Cookie blocked or expired — user must log in again
        storeToken(null);
      } finally {
        setLoading(false);
      }
    }

    restoreAuth();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);


  async function login(): Promise<void> {
    await loginWithGoogle();
  }


  async function refresh(): Promise<string | null> {
    try {
      const token = await refreshAccessToken();
      storeToken(token);
      return token;
    } catch {
      // Refresh failed — clear stale session so user gets login prompt
      storeToken(null);
      return null;
    }
  }

  useEffect(() => {
    setRefreshHandler(refresh);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);


  async function logout(): Promise<void> {
    try {
      await logoutRequest();
    } finally {
      storeToken(null);
    }
  }


  return (
    <AuthContext.Provider value={{ accessToken, loading, login, refresh, logout }}>
      {children}
    </AuthContext.Provider>
  );
}


export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}
