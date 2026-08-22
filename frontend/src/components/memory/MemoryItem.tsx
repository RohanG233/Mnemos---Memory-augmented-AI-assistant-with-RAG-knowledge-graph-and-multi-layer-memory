import type { Memory } from "../../types/memory";

interface MemoryItemProps {
  memory: Memory;
}

function MemoryItem({ memory }: MemoryItemProps) {
  const metadata = memory.metadata;

  const source = typeof metadata?.source === "string" ? metadata.source : null;

  const importance =
    typeof metadata?.importance === "number" ? metadata.importance : null;

  const accessCount =
    typeof metadata?.access_count === "number" ? metadata.access_count : null;

  return (
    <div className="memory-item">
      <p className="memory-content">{memory.content}</p>

      {metadata && (
        <div className="memory-metadata">
          {source && (
            <span>
              <strong>Source:</strong> {source}
            </span>
          )}

          {importance !== null && (
            <span>
              <strong>Importance:</strong> {importance}
            </span>
          )}

          {accessCount !== null && (
            <span>
              <strong>Accessed:</strong> {accessCount}{" "}
              {accessCount === 1 ? "time" : "times"}
            </span>
          )}
        </div>
      )}
    </div>
  );
}

export default MemoryItem;
