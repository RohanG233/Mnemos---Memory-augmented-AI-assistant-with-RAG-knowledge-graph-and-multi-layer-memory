interface GraphControlsProps {
  onRefresh: () => void;
}

function GraphControls({ onRefresh }: GraphControlsProps) {
  return (
    <div className="graph-controls">
      <button type="button" onClick={onRefresh}>
        ↺ Refresh
      </button>
    </div>
  );
}

export default GraphControls;
