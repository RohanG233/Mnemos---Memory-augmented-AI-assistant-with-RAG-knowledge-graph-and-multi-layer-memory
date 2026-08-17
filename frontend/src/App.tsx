import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Layout from "./components/layout/Layout";

import Chat from "./pages/Chat";
import Upload from "./pages/Upload";
import Memories from "./pages/Memories";
import Graph from "./pages/Graph";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/chat" replace />} />

          <Route path="chat" element={<Chat />} />

          <Route path="documents" element={<Upload />} />

          <Route path="memories" element={<Memories />} />

          <Route path="graph" element={<Graph />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
