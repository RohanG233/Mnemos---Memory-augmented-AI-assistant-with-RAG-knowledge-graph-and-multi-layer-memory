import { Navigate } from "react-router-dom";

import { useAuth } from "../../context/AuthContext";

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
  // User not authenticated
  // -----------------------------

  if (!accessToken) {
    return <Navigate to="/login" replace />;
  }

  // -----------------------------
  // User authenticated
  // -----------------------------

  return children;
}

export default ProtectedRoute;
