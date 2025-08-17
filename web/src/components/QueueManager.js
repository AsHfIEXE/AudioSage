import React from 'react';

const QueueManager = ({ queue, nowPlaying, onSkip, onClear }) => {
  const formatDuration = (seconds) => {
    if (!seconds) return '0:00';
    const mins = Math.floor(parseInt(seconds) / 60);
    const secs = parseInt(seconds) % 60;
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  };

  return (
    <div className="queue-manager">
      <div className="queue-header">
        <h2>Queue ({queue.length})</h2>
        <div className="queue-actions">
          <button className="btn-secondary" onClick={onSkip}>Skip</button>
          <button className="btn-secondary" onClick={onClear}>Clear</button>
        </div>
      </div>
      
      <div className="queue-list">
        {nowPlaying && (
          <div className="queue-item current">
            <span className="queue-position">▶</span>
            <div className="queue-track-info">
              <div className="queue-title">{nowPlaying.title}</div>
              <div className="queue-artist">{nowPlaying.artist}</div>
            </div>
            <div className="queue-duration">
              {formatDuration(nowPlaying.duration)}
            </div>
          </div>
        )}
        
        {queue.length > 0 ? (
          queue.map((track, index) => (
            <div key={index} className="queue-item">
              <span className="queue-position">{index + 1}</span>
              <div className="queue-track-info">
                <div className="queue-title">{track.title}</div>
                <div className="queue-artist">{track.artist}</div>
              </div>
              <div className="queue-duration">
                {formatDuration(track.duration)}
              </div>
            </div>
          ))
        ) : (
          <p className="empty-queue">Queue is empty</p>
        )}
      </div>
    </div>
  );
};

export default QueueManager;