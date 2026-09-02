import { useState } from "react";
import { useMemories } from "../hooks/useMemories";
import MemoryList from "../components/memory/MemoryList";
import EpisodeList from "../components/memory/EpisodeList";
import ProcedureList from "../components/memory/ProcedureList";

type Tab = "semantic" | "episodes" | "procedures";

const TABS: { id: Tab; label: string; icon: string }[] = [
  { id: "semantic",   label: "Long-Term Memory", icon: "🧠" },
  { id: "episodes",   label: "Episodes",         icon: "📖" },
  { id: "procedures", label: "Procedures",       icon: "⚙️" },
];

function Memories() {
  const { memories, episodes, procedures, loading, error, reload } = useMemories();
  const [activeTab, setActiveTab] = useState<Tab>("semantic");

  if (loading) {
    return (
      <main className="memory-page">
        <div className="page-header"><h1>Memory</h1></div>
        <div className="loading-state">
          <div className="loading-spinner" />
          <p>Loading memories…</p>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="memory-page">
        <div className="page-header"><h1>Memory</h1></div>
        <div className="empty-state">
          <h3>Failed to load memories</h3>
          <p>{error}</p>
          <button type="button" className="btn btn-ghost" style={{ marginTop: 14 }} onClick={reload}>
            ↺ Try again
          </button>
        </div>
      </main>
    );
  }

  const counts: Record<Tab, number> = {
    semantic:   memories.length,
    episodes:   episodes.length,
    procedures: procedures.length,
  };

  return (
    <main className="memory-page">
      <div className="page-header">
        <h1>Memory</h1>
        <div className="page-header-actions">
          <button type="button" className="btn btn-ghost" onClick={reload}>
            ↺ Refresh
          </button>
        </div>
      </div>

      <div className="memory-tabs">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            className={`memory-tab${activeTab === tab.id ? " active" : ""}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span>{tab.icon}</span>
            <span>{tab.label}</span>
            {counts[tab.id] > 0 && (
              <span className="tab-count">{counts[tab.id]}</span>
            )}
          </button>
        ))}
      </div>

      <div className="memory-section">
        {activeTab === "semantic"   && <MemoryList    memories={memories}     />}
        {activeTab === "episodes"   && <EpisodeList   episodes={episodes}     />}
        {activeTab === "procedures" && <ProcedureList procedures={procedures} />}
      </div>
    </main>
  );
}

export default Memories;
