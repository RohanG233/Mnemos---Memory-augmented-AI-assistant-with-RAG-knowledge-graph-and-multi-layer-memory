import type { Memory } from "../../types/memory";
import MemoryItem from "./MemoryItem";

interface MemoryListProps {
  memories: Memory[];
}

function MemoryList({ memories }: MemoryListProps) {
  if (memories.length === 0) {
    return <p>No memories stored yet.</p>;
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
