import React, { useState, useEffect } from 'react';
import PlayerControls from './components/PlayerControls';
import QueueManager from './components/QueueManager';
import LibraryBrowser from './components/LibraryBrowser';
import PlaylistManager from './components/PlaylistManager';
import './App.css';

function App() {
  const [nowPlaying, setNowPlaying] = useState(null);
  const [queue, setQueue] = useState([]);
  const [library, setLibrary] = useState([]);
  const [playlists, setPlaylists] = useState([]);
  const [isPlaying, setIsPlaying] = useState(false);
  const [volume, setVolume] = useState(100);
  const [loopMode, setLoopMode] = useState(0);
  const [activeTab, setActiveTab] = useState('library');
  const [guildId, setGuildId] = useState(123456789);
  const [directUrl, setDirectUrl] = useState('');
  const [serverUrl, setServerUrl] = useState('http://localhost:3000');

  // Load data from API
  useEffect(() => {
    // Load library
    fetch('http://localhost:5000/api/library')
      .then(res => res.json())
      .then(data => setLibrary(data))
      .catch(err => console.error('Library load error:', err));
    
    // Load server URL
    fetch('http://localhost:3000/api/config')
      .then(res => res.json())
      .then(data => setServerUrl(data.baseUrl))
      .catch(err => console.error('Server config load error:', err));
    
    // Poll for player state
    const interval = setInterval(() => {
      fetch(`http://localhost:5000/api/player/${guildId}`)
        .then(res => res.json())
        .then(data => {
          setNowPlaying(data.current_track);
          setQueue(data.queue);
          setIsPlaying(data.is_playing);
          setVolume(Math.round(data.volume * 100));
          setLoopMode(data.loop_mode);
        })
        .catch(err => console.error('Player state error:', err));
    }, 2000);
    
    return () => clearInterval(interval);
  }, [guildId]);

  const handleControlAction = async (action, payload = {}) => {
    try {
      const response = await fetch(`http://localhost:5000/api/control/${guildId}/${action}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });
      
      const data = await response.json();
      if (data.current_track) {
        setNowPlaying(data.current_track);
        setQueue(data.queue);
        setIsPlaying(data.is_playing);
        setVolume(Math.round(data.volume * 100));
        setLoopMode(data.loop_mode);
      }
    } catch (error) {
      console.error('Control action error:', error);
    }
  };

  const handlePlayUrl = async () => {
    if (!directUrl) return;
    
    try {
      const response = await fetch(`http://localhost:5000/api/playurl/${guildId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: directUrl }),
      });
      
      const data = await response.json();
      if (data.status === 'ok') {
        alert(`Playing: ${directUrl}`);
        setDirectUrl('');
      } else {
        alert('Error playing URL');
      }
    } catch (error) {
      console.error('Error playing URL:', error);
      alert('Error playing URL');
    }
  };

  const handleSetServerUrl = async () => {
    try {
      const response = await fetch('http://localhost:3000/api/config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ baseUrl: serverUrl }),
      });
      
      const data = await response.json();
      if (data.config) {
        alert(`Server URL updated to: ${data.config.baseUrl}`);
      } else {
        alert('Error updating server URL');
      }
    } catch (error) {
      console.error('Error updating server URL:', error);
      alert('Error updating server URL');
    }
  };

  return (
    <div className="App">
      <header>
        <h1>🎵 Advanced Music Bot</h1>
        <nav className="main-nav">
          <button 
            className={activeTab === 'library' ? 'active' : ''}
            onClick={() => setActiveTab('library')}
          >
            Library
          </button>
          <button 
            className={activeTab === 'playlists' ? 'active' : ''}
            onClick={() => setActiveTab('playlists')}
          >
            Playlists
          </button>
          <button 
            className={activeTab === 'queue' ? 'active' : ''}
            onClick={() => setActiveTab('queue')}
          >
            Queue
          </button>
          <button 
            className={activeTab === 'url' ? 'active' : ''}
            onClick={() => setActiveTab('url')}
          >
            Play URL
          </button>
        </nav>
      </header>
      
      <main>
        <PlayerControls 
          nowPlaying={nowPlaying}
          isPlaying={isPlaying}
          volume={volume}
          loopMode={loopMode}
          onControlAction={handleControlAction}
          onVolumeChange={(vol) => handleControlAction('volume', { volume: vol })}
          onLoopChange={(mode) => handleControlAction('loop', { mode })}
        />
        
        <div className="content-area">
          {activeTab === 'library' && (
            <LibraryBrowser 
              library={library}
              onPlayTrack={(track) => handleControlAction('play', { track_id: track.id })}
            />
          )}
          
          {activeTab === 'playlists' && (
            <PlaylistManager 
              playlists={playlists}
              onPlayPlaylist={(playlist) => console.log('Play playlist:', playlist)}
            />
          )}
          
          {activeTab === 'queue' && (
            <QueueManager 
              queue={queue}
              nowPlaying={nowPlaying}
              onSkip={() => handleControlAction('skip')}
              onClear={() => handleControlAction('clear')}
            />
          )}
          
          {activeTab === 'url' && (
            <div className="url-play-section">
              <h2>Play from URL</h2>
              <div className="url-input-container">
                <input
                  type="text"
                  placeholder="Enter audio URL (http:// or https://)"
                  value={directUrl}
                  onChange={(e) => setDirectUrl(e.target.value)}
                  className="url-input"
                />
                <button 
                  className="btn-primary"
                  onClick={handlePlayUrl}
                  disabled={!directUrl}
                >
                  ▶️ Play URL
                </button>
              </div>
              
              <h3>Server Configuration</h3>
              <div className="server-config">
                <input
                  type="text"
                  placeholder="Server URL"
                  value={serverUrl}
                  onChange={(e) => setServerUrl(e.target.value)}
                  className="url-input"
                />
                <button 
                  className="btn-primary"
                  onClick={handleSetServerUrl}
                >
                  Set Server URL
                </button>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;