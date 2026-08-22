import { NavLink } from "react-router-dom";

import { useAuth } from "../../context/AuthContext";

function Sidebar() {
  const { logout } = useAuth();

  async function handleLogout() {
    try {
      await logout();
    } catch (error) {
      console.error("Logout failed:", error);
    }
  }

  return (
    <aside className="sidebar">
      <h1>ACAI</h1>

      <nav>
        <NavLink to="/chat">Chat</NavLink>

        <NavLink to="/documents">Documents</NavLink>

        <NavLink to="/memories">Memories</NavLink>

        <NavLink to="/graph">Knowledge Graph</NavLink>
      </nav>

      <button type="button" onClick={handleLogout} className="logout-button">
        Logout
      </button>
    </aside>
  );
}

export default Sidebar;
