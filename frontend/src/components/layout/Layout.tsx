import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import NeuralBackground from "../background/NeuralBackground";
import CursorEffects from "../background/CursorEffects";

function Layout() {
  return (
    <div className="app-layout">
      <NeuralBackground />
      <CursorEffects />

      <Sidebar />

      <main className="main-content">
        <div className="page-transition">
          <Outlet />
        </div>
      </main>
    </div>
  );
}

export default Layout;
