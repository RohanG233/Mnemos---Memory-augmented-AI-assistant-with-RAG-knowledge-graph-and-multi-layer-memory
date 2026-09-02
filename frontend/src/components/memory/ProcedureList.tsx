import type { Procedure } from "../../types/memory";
import MemoryItem from "./MemoryItem";

interface ProcedureListProps {
  procedures: Procedure[];
}

function ProcedureList({ procedures }: ProcedureListProps) {
  if (procedures.length === 0) {
    return (
      <div className="empty-state">
        <h3>No procedures yet</h3>
        <p>Tell the AI how it should behave and those instructions will be stored here.</p>
      </div>
    );
  }

  return (
    <div className="memory-list">
      {procedures.map((p) => (
        <MemoryItem
          key={p.id}
          memory={p}
          badge="Procedure"
          badgeClass="memory-badge-procedure"
        />
      ))}
    </div>
  );
}

export default ProcedureList;
