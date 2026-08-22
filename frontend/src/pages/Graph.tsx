import { useGraph } from "../hooks/useGraph";

import GraphView from "../components/graph/GraphView";
import GraphControls from "../components/graph/GraphControls";

function Graph() {
  const { nodes, edges, loading, error, reload } = useGraph();

  if (loading) {
    return (
      <main>
        <h1>Knowledge Graph</h1>

        <div className="loading-state">
          <div className="loading-spinner" />
          <p>Loading graph...</p>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main>
        <h1>Knowledge Graph</h1>

        <p>{error}</p>

        <button onClick={reload}>Try Again</button>
      </main>
    );
  }

  return (
    <main>
      <div>
        <h1>Knowledge Graph</h1>

        <p>
          {nodes.length} nodes · {edges.length} relationships
        </p>

        <GraphControls onRefresh={reload} />
      </div>

      <GraphView nodes={nodes} edges={edges} />
    </main>
  );
}

export default Graph;
