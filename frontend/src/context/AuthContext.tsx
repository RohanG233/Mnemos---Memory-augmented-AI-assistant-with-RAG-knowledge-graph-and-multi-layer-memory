import {
  createContext,
  useContext,
  useEffect,
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


// --------------------------------
// Auth Provider
// --------------------------------

export function AuthProvider({ children }: { children: ReactNode }) {

  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);


  // --------------------------------
  // Restore Authentication on mount
  // --------------------------------

  useEffect(() => {

    async function restoreAuth() {

      // 1. Check if the backend just redirected back with a token in the URL
      //    (after Google OAuth callback)
      const urlToken = extractAccessTokenFromUrl();

      if (urlToken) {
        setAccessToken(urlToken);
        setLoading(false);
        return;
      }

      // 2. Try to silently refresh via the HttpOnly cookie
      try {
        const token = await refreshAccessToken();
        setAccessToken(token);
      } catch {
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

  // Register the refresh handler with apiFetch
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


// --------------------------------
// Auth Hook
// --------------------------------

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }

  return context;
}
