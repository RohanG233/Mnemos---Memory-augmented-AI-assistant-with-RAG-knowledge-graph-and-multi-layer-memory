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

  // Prevent the refresh call from running if we already have
  // a token from the URL (OAuth callback) — avoids a race where
  // restoreAuth clobbers the just-extracted token with a 401.
  const hasRestoredRef = useRef(false);


  useEffect(() => {
    // Guard: only run once even in React StrictMode double-invoke
    if (hasRestoredRef.current) return;
    hasRestoredRef.current = true;

    async function restoreAuth() {

      // 1. Check for access_token in the URL (OAuth callback redirect)
      const urlToken = extractAccessTokenFromUrl();

      if (urlToken) {
        // We have a fresh token from the just-completed OAuth flow.
        // Store it and stop — do NOT call /auth/refresh here because:
        //   a) we don't need to (we have the token already)
        //   b) the HttpOnly cookie may not be readable yet in the
        //      browser due to cross-site redirect cookie timing
        setAccessToken(urlToken);
        setLoading(false);
        return;
      }

      // 2. No URL token — try to silently restore via the HttpOnly cookie
      try {
        const token = await refreshAccessToken();
        setAccessToken(token);
      } catch {
        // Cookie missing, expired, or invalid — user must log in
        setAccessToken(null);
      } finally {
        setLoading(false);
      }
    }

    restoreAuth();
  }, []);


  // --------------------------------
  // Login
  // --------------------------------

  async function login(): Promise<void> {
    await loginWithGoogle();
  }


  // --------------------------------
  // Refresh Token
  // --------------------------------

  async function refresh(): Promise<string | null> {
    try {
      const token = await refreshAccessToken();
      setAccessToken(token);
      return token;
    } catch {
      setAccessToken(null);
      return null;
    }
  }

  useEffect(() => {
    setRefreshHandler(refresh);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);


  // --------------------------------
  // Logout
  // --------------------------------

  async function logout(): Promise<void> {
    try {
      await logoutRequest();
    } finally {
      setAccessToken(null);
    }
  }


  return (
    <AuthContext.Provider
      value={{
        accessToken,
        loading,
        login,
        refresh,
        logout,
      }}
    >
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
