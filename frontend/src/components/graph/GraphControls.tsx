interface GraphControlsProps {
  onRefresh: () => void;
}

function GraphControls({ onRefresh }: GraphControlsProps) {
  return (
    <div className="graph-controls">
      <button onClick={onRefresh}>Refresh Graph</button>
    </div>
  );
}

export default GraphControls;
