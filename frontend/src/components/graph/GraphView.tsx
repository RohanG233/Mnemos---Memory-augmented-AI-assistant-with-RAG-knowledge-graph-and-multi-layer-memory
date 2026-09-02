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
      x: (index % 6) * 220,
      y: Math.floor(index / 6) * 160,
    },
    data: { label: node.id },
    style: {
      background: "rgba(99,102,241,0.15)",
      border: "1px solid rgba(99,102,241,0.4)",
      borderRadius: 10,
      color: "#e4e4e7",
      fontSize: 12,
      fontWeight: 600,
      padding: "6px 12px",
    },
  }));

  const flowEdges: Edge[] = edges.map((edge, index) => ({
    id: `edge-${index}`,
    source: edge.source,
    target: edge.target,
    label: edge.relation,
    style: { stroke: "rgba(34,211,238,0.5)", strokeWidth: 1.5 },
    labelStyle: { fill: "#e4e4e7", fontSize: 11 },
    labelBgStyle: { fill: "rgba(16,16,23,0.85)" },
    labelBgPadding: [4, 6] as [number, number],
    labelBgBorderRadius: 4,
  }));

  return (
    <div style={{ width: "100%", height: "100%" }}>
      <ReactFlow
        nodes={flowNodes}
        edges={flowEdges}
        fitView
        fitViewOptions={{ padding: 0.2 }}
      >
        <Background color="rgba(99,102,241,0.12)" gap={24} size={1} />
        <Controls
          style={{
            background: "rgba(16,16,23,0.9)",
            border: "1px solid rgba(228,228,231,0.1)",
            borderRadius: 10,
          }}
        />
        <MiniMap
          style={{
            background: "rgba(10,10,16,0.85)",
            border: "1px solid rgba(228,228,231,0.08)",
            borderRadius: 10,
          }}
          nodeColor="rgba(99,102,241,0.5)"
          maskColor="rgba(4,4,8,0.4)"
        />
      </ReactFlow>
    </div>
  );
}

export default GraphView;
