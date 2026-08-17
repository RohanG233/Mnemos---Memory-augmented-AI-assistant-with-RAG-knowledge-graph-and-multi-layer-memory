import type { Procedure } from "../../types/memory";

interface ProcedureListProps {
  procedures: Procedure[];
}

function ProcedureList({ procedures }: ProcedureListProps) {
  if (procedures.length === 0) {
    return <p>No procedures stored yet.</p>;
  }

  return (
    <div className="memory-list">
      {procedures.map((procedure) => (
        <div className="memory-item" key={procedure.id}>
          <p>{procedure.content}</p>

          {procedure.metadata && (
            <small>{JSON.stringify(procedure.metadata)}</small>
          )}
        </div>
      ))}
    </div>
  );
}

export default ProcedureList;
