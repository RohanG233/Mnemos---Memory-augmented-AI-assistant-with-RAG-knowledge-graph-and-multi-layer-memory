import type { Memory } from "../../types/memory";

interface MemoryItemProps {
  memory: Memory;
  badge?: string;
  badgeClass?: string;
}

function MemoryItem({ memory, badge, badgeClass }: MemoryItemProps) {
  const meta = memory.metadata;
  const source = typeof meta?.source === "string" ? meta.source : null;
  const importance = typeof meta?.importance === "number" ? meta.importance : null;
  const accessCount = typeof meta?.access_count === "number" ? meta.access_count : null;

  return (
    <div className="memory-item">
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 8 }}>
        <p className="memory-content">{memory.content}</p>
        {badge && (
          <span className={`memory-badge ${badgeClass ?? ""}`}>{badge}</span>
        )}
      </div>

      {importance !== null && (
        <div className="memory-importance-bar">
          <div
            className="memory-importance-fill"
            style={{ width: `${Math.round(importance * 100)}%` }}
          />
        </div>
      )}

      {meta && (
        <div className="memory-metadata">
          {source && (
            <span><strong>source</strong> {source}</span>
          )}
          {importance !== null && (
            <span><strong>importance</strong> {importance.toFixed(2)}</span>
          )}
          {accessCount !== null && (
            <span><strong>accessed</strong> {accessCount}×</span>
          )}
        </div>
      )}
    </div>
  );
}

export default MemoryItem;
