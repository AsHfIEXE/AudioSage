import React from 'react';

const PlayerControls = ({ 
  nowPlaying, 
  isPlaying, 
  volume, 
  loopMode, 
  onControlAction, 
  onVolumeChange, 
  onLoopChange 
}) => {
  const formatDuration = (seconds) => {
    if (!seconds) return '0:00';
    const mins = Math.floor(parseInt(seconds) / 60);
    const secs = parseInt(seconds) % 60;
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  };

  const togglePlayPause = () => {
    onControlAction(isPlaying ? 'pause' : 'play');
  };

  const handleSkip = () => {
    onControlAction('skip');
  };

  const handleStop = () => {
    onControlAction('stop');
  };

  const toggleLoopMode = () => {
    const newMode = (loopMode + 1) % 3;
    onLoopChange(newMode);
  };

  return (
    <div className="player-controls-section">
      <div className="now-playing-display">
        {nowPlaying ? (
          <div className="track-info">
            <div className="album-art-placeholder">
              🎵
            </div>
            <div className="track-details">
              <h3>{nowPlaying.title}</h3>
              <p>{nowPlaying.artist}</p>
              <p className="album-info">{nowPlaying.album}</p>
              <div className="track-duration">
                {formatDuration(nowPlaying.duration)}
              </div>
            </div>
          </div>
        ) : (
          <div className="no-track">
            <p>No track playing</p>
          </div>
        )}
      </div>
      
      <div className="player-controls">
        <button className="control-btn" title="Stop" onClick={handleStop}>
          ⏹️
        </button>
        <button 
          className="control-btn play-pause" 
          onClick={togglePlayPause}
          title={isPlaying ? "Pause" : "Play"}
        >
          {isPlaying ? '⏸️' : '▶️'}
        </button>
        <button className="control-btn" title="Skip" onClick={handleSkip}>
          ⏭️
        </button>
        
        <div className="volume-controls">
          <span>🔈</span>
          <input
            type="range"
            min="0"
            max="200"
            value={volume}
            onChange={(e) => onVolumeChange(parseInt(e.target.value))}
            className="volume-slider"
          />
          <span>🔊</span>
          <span className="volume-display">{volume}%</span>
        </div>
        
        <button 
          className={`control-btn loop-btn ${loopMode > 0 ? 'active' : ''}`}
          onClick={toggleLoopMode}
          title={`Loop: ${['Off', 'Track', 'Queue'][loopMode]}`}
        >
          🔁
          {loopMode === 1 && '1'}
          {loopMode === 2 && '∞'}
        </button>
      </div>
    </div>
  );
};

export default PlayerControls;