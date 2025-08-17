import React, { useState } from 'react';

const PlaylistManager = ({ playlists, onPlayPlaylist }) => {
  const [newPlaylistName, setNewPlaylistName] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);

  const handleCreatePlaylist = (e) => {
    e.preventDefault();
    if (newPlaylistName.trim()) {
      // In a real implementation, this would call an API
      console.log('Create playlist:', newPlaylistName);
      setNewPlaylistName('');
      setShowCreateForm(false);
    }
  };

  return (
    <div className="playlist-manager">
      <div className="playlist-header">
        <h2>Playlists</h2>
        <button 
          className="btn-primary"
          onClick={() => setShowCreateForm(!showCreateForm)}
        >
          {showCreateForm ? 'Cancel' : 'Create Playlist'}
        </button>
      </div>
      
      {showCreateForm && (
        <form onSubmit={handleCreatePlaylist} className="create-playlist-form">
          <input
            type="text"
            placeholder="Playlist name"
            value={newPlaylistName}
            onChange={(e) => setNewPlaylistName(e.target.value)}
            className="playlist-input"
          />
          <button type="submit" className="btn-primary">Create</button>
        </form>
      )}
      
      <div className="playlists-grid">
        {Object.keys(playlists).length > 0 ? (
          Object.entries(playlists).map(([name, playlist]) => (
            <div key={name} className="playlist-card">
              <div className="playlist-art-placeholder">🎶</div>
              <div className="playlist-info">
                <h3>{name}</h3>
                <p>{playlist.tracks.length} tracks</p>
                <button 
                  className="play-playlist-btn"
                  onClick={() => onPlayPlaylist(playlist)}
                >
                  ▶️ Play
                </button>
              </div>
            </div>
          ))
        ) : (
          <p className="no-playlists">No playlists created yet</p>
        )}
      </div>
    </div>
  );
};

export default PlaylistManager;