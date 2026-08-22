import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import { AuthProvider } from "./context/AuthContext";

import ProtectedRoute from "./components/auth/ProtectedRoute";

import Layout from "./components/layout/Layout";

import Chat from "./pages/Chat";
import Upload from "./pages/Upload";
import Memories from "./pages/Memories";
import Graph from "./pages/Graph";
import Login from "./pages/Login";

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* -------------------------
              Login Route
          -------------------------- */}

          <Route path="/login" element={<Login />} />

          {/* -------------------------
              Protected Application
          -------------------------- */}

          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/chat" replace />} />

            <Route path="chat" element={<Chat />} />

            <Route path="documents" element={<Upload />} />

            <Route path="memories" element={<Memories />} />

            <Route path="graph" element={<Graph />} />
          </Route>

          {/* -------------------------
              Unknown Route
          -------------------------- */}

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
