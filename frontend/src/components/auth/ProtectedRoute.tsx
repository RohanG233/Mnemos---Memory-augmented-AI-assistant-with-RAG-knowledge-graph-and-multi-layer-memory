import { Navigate } from "react-router-dom";

import { useAuth } from "../../context/AuthContext";
import { extractTokensFromUrl } from "../../services/authService";

import type { ReactNode } from "react";

interface ProtectedRouteProps {
  children: ReactNode;
}

function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { accessToken, loading } = useAuth();

  // -----------------------------
  // Wait for authentication check
  // -----------------------------

  if (loading) {
    return <div>Loading...</div>;
  }

  // -----------------------------
  // Check if URL contains tokens (OAuth callback)
  // Don't redirect if tokens are present in URL
  // Don't remove from URL so AuthContext can extract them
  // -----------------------------

  const urlTokens = extractTokensFromUrl(false);
  if (!accessToken && !urlTokens.accessToken) {
    return <Navigate to="/login" replace />;
  }

  // -----------------------------
  // User authenticated or tokens in URL
  // -----------------------------

  return children;
}

export default ProtectedRoute;
