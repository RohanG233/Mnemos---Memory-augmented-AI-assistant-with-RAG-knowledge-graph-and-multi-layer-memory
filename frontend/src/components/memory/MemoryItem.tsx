import type { Memory } from "../../types/memory";

interface MemoryItemProps {
  memory: Memory;
}

function MemoryItem({ memory }: MemoryItemProps) {
  return (
    <div className="memory-item">
      <p>{memory.content}</p>

      {memory.metadata && <small>{JSON.stringify(memory.metadata)}</small>}
    </div>
  );
}

export default MemoryItem;
