import type { Memory } from "../../types/memory";
import MemoryItem from "./MemoryItem";

interface MemoryListProps {
  memories: Memory[];
}

function MemoryList({ memories }: MemoryListProps) {
  if (memories.length === 0) {
    return (
      <div className="empty-state">
        <h3>No long-term memories yet</h3>
        <p>Share personal facts or preferences in chat and they'll be stored here.</p>
      </div>
    );
  }

  return (
    <div className="memory-list">
      {memories.map((m) => (
        <MemoryItem key={m.id} memory={m} badge="Semantic" badgeClass="memory-badge-semantic" />
      ))}
    </div>
  );
}

export default MemoryList;
