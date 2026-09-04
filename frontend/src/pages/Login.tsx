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

        {/* Logo mark */}
        <div style={{
          width: 52,
          height: 52,
          borderRadius: 14,
          background: "var(--grad)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: 24,
          color: "#08080c",
          fontWeight: 800,
          margin: "0 auto 20px",
          boxShadow: "0 8px 28px rgba(99,102,241,0.45)",
        }}>
          ✦
        </div>

        <h1>Mnemos</h1>
        <p>Memory-Augmented AI</p>

        {error && <p className="login-error">{error}</p>}

        <button
          type="button"
          className="login-btn"
          onClick={handleLogin}
          disabled={loading}
        >
          {loading ? "Loading…" : "Continue with Google"}
        </button>

        <p style={{
          marginTop: 20,
          fontSize: 12,
          color: "var(--text-muted)",
          lineHeight: 1.6,
        }}>
          By continuing you agree to our terms of service.
        </p>

      </div>
    </div>
  );
}

export default Login;
