import { useGraph } from "../hooks/useGraph";
import GraphView from "../components/graph/GraphView";
import GraphControls from "../components/graph/GraphControls";

function Graph() {
  const { nodes, edges, loading, error, reload } = useGraph();

  if (loading) {
    return (
      <main className="graph-page">
        <div className="page-header"><h1>Knowledge Graph</h1></div>
        <div className="loading-state">
          <div className="loading-spinner" />
          <p>Loading graph…</p>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="graph-page">
        <div className="page-header"><h1>Knowledge Graph</h1></div>
        <div className="empty-state">
          <h3>Failed to load graph</h3>
          <p>{error}</p>
          <button type="button" className="btn btn-ghost" style={{ marginTop: 14 }} onClick={reload}>
            ↺ Try again
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className="graph-page">
      <div className="page-header">
        <h1>Knowledge Graph</h1>
        <div className="page-header-actions">
          <div className="graph-stats">
            <span className="graph-stat-chip"><span>{nodes.length}</span> nodes</span>
            <span className="graph-stat-chip"><span>{edges.length}</span> edges</span>
          </div>
          <GraphControls onRefresh={reload} />
        </div>
      </div>

      {nodes.length === 0 ? (
        <div className="empty-state">
          <h3>No graph data yet</h3>
          <p>Upload documents or send a few messages to start building your knowledge graph.</p>
        </div>
      ) : (
        <div className="graph-canvas-wrapper">
          <GraphView nodes={nodes} edges={edges} />
        </div>
      )}
    </main>
  );
}

export default Graph;
