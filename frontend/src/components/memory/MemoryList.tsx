import type { Memory } from "../../types/memory";
import MemoryItem from "./MemoryItem";

interface MemoryListProps {
  memories: Memory[];
}

function MemoryList({ memories }: MemoryListProps) {
  if (memories.length === 0) {
    return (
      <div className="empty-state">
        <h3>No memories yet</h3>
        <p>Your stored memories will appear here.</p>
      </div>
    );
  }

  return (
    <div className="memory-list">
      {memories.map((memory) => (
        <MemoryItem key={memory.id} memory={memory} />
      ))}
    </div>
  );
}

export default MemoryList;
