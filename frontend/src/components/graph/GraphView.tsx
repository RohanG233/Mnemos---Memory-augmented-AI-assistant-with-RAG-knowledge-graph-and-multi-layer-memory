import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  type Node,
  type Edge,
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";

import type {
  GraphNode as BackendNode,
  GraphEdge as BackendEdge,
} from "../../types/graph";

interface GraphViewProps {
  nodes: BackendNode[];
  edges: BackendEdge[];
}

function GraphView({ nodes, edges }: GraphViewProps) {
  const flowNodes: Node[] = nodes.map((node, index) => ({
    id: node.id,
    position: {
      x: (index % 5) * 200,
      y: Math.floor(index / 5) * 150,
    },
    data: {
      label: node.id,
    },
  }));

  const flowEdges: Edge[] = edges.map((edge, index) => ({
    id: `edge-${index}`,
    source: edge.source,
    target: edge.target,
    label: edge.relation,
  }));

  return (
    <div
      style={{
        width: "100%",
        height: "600px",
      }}
    >
      <ReactFlow nodes={flowNodes} edges={flowEdges} fitView>
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>
  );
}

export default GraphView;
