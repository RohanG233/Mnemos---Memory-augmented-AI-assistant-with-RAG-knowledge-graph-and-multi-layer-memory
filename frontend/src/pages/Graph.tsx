import { useGraph } from "../hooks/useGraph";

import GraphView from "../components/graph/GraphView";
import GraphControls from "../components/graph/GraphControls";

function Graph() {
  const { nodes, edges, loading, error, reload } = useGraph();

  if (loading) {
    return (
      <main>
        <h1>Knowledge Graph</h1>
        <p>Loading graph...</p>
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
