import { NavLink } from "react-router-dom";

function Sidebar() {
  return (
    <aside className="sidebar">
      <h1>ACAI</h1>

      <nav>
        <NavLink to="/chat">Chat</NavLink>

        <NavLink to="/documents">Documents</NavLink>

        <NavLink to="/memories">Memories</NavLink>

        <NavLink to="/graph">Knowledge Graph</NavLink>
      </nav>
    </aside>
  );
}

export default Sidebar;
