import { useState } from "react";

import { useAuth } from "../context/AuthContext";

function Login() {
  const { login, loading } = useAuth();

  const [error, setError] = useState<string | null>(null);

  async function handleLogin() {
    try {
      setError(null);

      await login();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <h1>ACAI</h1>

        <p>AI Memory and Knowledge Graph</p>

        {error && <p className="login-error">{error}</p>}

        <button type="button" onClick={handleLogin} disabled={loading}>
          {loading ? "Loading..." : "Continue with Google"}
        </button>
      </div>
    </div>
  );
}

export default Login;
