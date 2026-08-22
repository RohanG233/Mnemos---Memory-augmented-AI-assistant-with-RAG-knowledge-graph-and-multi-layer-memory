import { createContext, useContext, useEffect, useState } from "react";

import type { ReactNode } from "react";

import {
  loginWithGoogle,
  refreshAccessToken,
  logout as logoutRequest,
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
  // Restore Authentication
  // --------------------------------

  useEffect(() => {
    async function restoreAuth() {
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

  async function login() {
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
  }, []);

  // --------------------------------
  // Logout
  // --------------------------------

  async function logout() {
    await logoutRequest();

    setAccessToken(null);
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
