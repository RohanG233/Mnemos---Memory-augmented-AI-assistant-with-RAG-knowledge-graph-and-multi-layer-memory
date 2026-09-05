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


  // --------------------------------
  // Persist token to sessionStorage
  // so page refreshes don't lose login
  // --------------------------------

  function storeToken(token: string | null) {
    if (token) {
      sessionStorage.setItem(SESSION_TOKEN_KEY, token);
    } else {
      sessionStorage.removeItem(SESSION_TOKEN_KEY);
    }
    setAccessToken(token);
  }


  // --------------------------------
  // Restore authentication on mount
  // --------------------------------

  useEffect(() => {
    if (hasRestoredRef.current) return;
    hasRestoredRef.current = true;

    async function restoreAuth() {

      // 1. Check for token in URL hash/query (just returned from OAuth)
      const urlToken = extractAccessTokenFromUrl();
      if (urlToken) {
        storeToken(urlToken);
        setLoading(false);
        return;
      }

      // 2. Check sessionStorage (page refresh within same session)
      const sessionToken = sessionStorage.getItem(SESSION_TOKEN_KEY);
      if (sessionToken) {
        setAccessToken(sessionToken);
        setLoading(false);
        return;
      }

      // 3. Try HttpOnly cookie refresh (works when cookie is present)
      try {
        const token = await refreshAccessToken();
        storeToken(token);
      } catch {
        storeToken(null);
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
      storeToken(token);
      return token;
    } catch {
      storeToken(null);
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
      storeToken(null);
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
