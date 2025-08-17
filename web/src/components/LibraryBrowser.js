import React, { useState } from 'react';

const LibraryBrowser = ({ library, onPlayTrack }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('title');

  const filteredLibrary = library.filter(track => 
    !searchQuery || 
    track.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    track.artist.toLowerCase().includes(searchQuery.toLowerCase()) ||
    track.album.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const sortedLibrary = [...filteredLibrary].sort((a, b) => {
    if (sortBy === 'title') {
      return a.title.localeCompare(b.title);
    } else if (sortBy === 'artist') {
      return a.artist.localeCompare(b.artist);
    } else if (sortBy === 'album') {
      return a.album.localeCompare(b.album);
    }
    return 0;
  });

  const formatDuration = (seconds) => {
    if (!seconds) return '0:00';
    const mins = Math.floor(parseInt(seconds) / 60);
    const secs = parseInt(seconds) % 60;
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  };

  return (
    <div className="library-browser">
      <div className="library-header">
        <h2>Music Library</h2>
        <div className="library-controls">
          <div className="search-container">
            <input
              type="text"
              placeholder="Search music..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
            <button className="search-btn">🔍</button>
          </div>
          
          <div className="sort-controls">
            <label>Sort by:</label>
            <select 
              value={sortBy} 
              onChange={(e) => setSortBy(e.target.value)}
              className="sort-select"
            >
              <option value="title">Title</option>
              <option value="artist">Artist</option>
              <option value="album">Album</option>
            </select>
          </div>
        </div>
        
        <div className="library-stats">
          <span>{library.length} tracks available</span>
        </div>
      </div>
      
      <div className="tracks-grid">
        {sortedLibrary.map((track, index) => (
          <div key={index} className="track-card">
            <div className="track-art-placeholder">🎵</div>
            <div className="track-details">
              <h4 className="track-title">{track.title}</h4>
              <p className="track-artist">{track.artist}</p>
              <p className="track-album">{track.album}</p>
              <div className="track-meta">
                <span className="track-duration">
                  {formatDuration(track.duration)}
                </span>
                <button 
                  className="play-track-btn"
                  onClick={() => onPlayTrack(track)}
                >
                  ▶️ Play
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default LibraryBrowser;