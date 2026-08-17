import type { Episode } from "../../types/memory";

interface EpisodeListProps {
  episodes: Episode[];
}

function EpisodeList({ episodes }: EpisodeListProps) {
  if (episodes.length === 0) {
    return <p>No episodes stored yet.</p>;
  }

  return (
    <div className="memory-list">
      {episodes.map((episode) => (
        <div className="memory-item" key={episode.id}>
          <p>{episode.content}</p>

          {episode.metadata && (
            <small>{JSON.stringify(episode.metadata)}</small>
          )}
        </div>
      ))}
    </div>
  );
}

export default EpisodeList;
