import { useMemories } from "../hooks/useMemories";

import MemoryList from "../components/memory/MemoryList";
import EpisodeList from "../components/memory/EpisodeList";
import ProcedureList from "../components/memory/ProcedureList";

function Memories() {
  const { memories, episodes, procedures, loading, error, reload } =
    useMemories();

  if (loading) {
    return (
      <main>
        <h1>Memory</h1>
        <div className="loading-state">
          <div className="loading-spinner" />
          <p>Loading memories...</p>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main>
        <h1>Memory</h1>

        <p>{error}</p>

        <button onClick={reload}>Try Again</button>
      </main>
    );
  }

  return (
    <main className="memory-page">
      <div className="memory-header">
        <h1>Memory</h1>

        <button onClick={reload}>Refresh</button>
      </div>

      <section>
        <h2>Long-Term Memories</h2>

        <MemoryList memories={memories} />
      </section>

      <section>
        <h2>Episodes</h2>

        <EpisodeList episodes={episodes} />
      </section>

      <section>
        <h2>Procedures</h2>

        <ProcedureList procedures={procedures} />
      </section>
    </main>
  );
}

export default Memories;
