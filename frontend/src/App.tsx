import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import { AuthProvider } from "./context/AuthContext";

import ProtectedRoute from "./components/auth/ProtectedRoute";

import Layout from "./components/layout/Layout";

import Home from "./pages/Home";
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
              Public intro + login
          -------------------------- */}

          <Route path="/" element={<Home />} />

          <Route path="/login" element={<Login />} />

          {/* -------------------------
              Protected Application
          -------------------------- */}

          <Route
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
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
