import type { Episode } from "../../types/memory";
import MemoryItem from "./MemoryItem";

interface EpisodeListProps {
  episodes: Episode[];
}

function EpisodeList({ episodes }: EpisodeListProps) {
  if (episodes.length === 0) {
    return (
      <div className="empty-state">
        <h3>No episodes yet</h3>
        <p>Significant decisions and milestones from your conversations will appear here.</p>
      </div>
    );
  }

  return (
    <div className="memory-list">
      {episodes.map((ep) => (
        <MemoryItem
          key={ep.id}
          memory={ep}
          badge="Episode"
          badgeClass="memory-badge-episode"
        />
      ))}
    </div>
  );
}

export default EpisodeList;
