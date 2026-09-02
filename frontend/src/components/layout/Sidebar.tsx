import { NavLink } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

const NAV_ITEMS = [
  { to: "/chat",      icon: "💬", label: "Chat" },
  { to: "/documents", icon: "📄", label: "Documents" },
  { to: "/memories",  icon: "🧠", label: "Memory" },
  { to: "/graph",     icon: "🕸️",  label: "Knowledge Graph" },
];

function Sidebar() {
  const { logout } = useAuth();

  async function handleLogout() {
    try { await logout(); }
    catch (err) { console.error("Logout failed:", err); }
  }

  return (
    <aside className="sidebar">
      {/* Brand */}
      <div className="sidebar-brand">
        <div className="sidebar-logo">✦</div>
        <h1>ACAI</h1>
      </div>

      {/* Navigation */}
      <nav>
        {NAV_ITEMS.map(({ to, icon, label }) => (
          <NavLink key={to} to={to}>
            <span className="nav-icon">{icon}</span>
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="sidebar-footer">
        <button
          type="button"
          className="logout-button"
          onClick={handleLogout}
        >
          <span className="nav-icon">↩</span>
          Logout
        </button>
      </div>
    </aside>
  );
}

export default Sidebar;
