interface GraphNodeProps {
  label: string;
}

function GraphNode({ label }: GraphNodeProps) {
  return <div className="graph-node">{label}</div>;
}

export default GraphNode;
