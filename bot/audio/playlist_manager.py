import json
import os
from typing import Dict, List, Optional

class PlaylistManager:
    def __init__(self, playlists_file: str = "playlists.json"):
        self.playlists_file = playlists_file
        self.playlists = self.load_playlists()
    
    def load_playlists(self) -> Dict:
        """Load playlists from file"""
        if os.path.exists(self.playlists_file):
            try:
                with open(self.playlists_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_playlists(self):
        """Save playlists to file"""
        with open(self.playlists_file, 'w') as f:
            json.dump(self.playlists, f, indent=2)
    
    def create_playlist(self, user_id: str, name: str) -> bool:
        """Create a new playlist for a user"""
        if user_id not in self.playlists:
            self.playlists[user_id] = {}
        
        if name in self.playlists[user_id]:
            return False  # Playlist already exists
        
        self.playlists[user_id][name] = {
            'name': name,
            'tracks': [],
            'created_at': self._get_timestamp()
        }
        
        self.save_playlists()
        return True
    
    def add_track(self, user_id: str, playlist_name: str, track: Dict) -> bool:
        """Add a track to a playlist"""
        if user_id not in self.playlists:
            return False
        
        if playlist_name not in self.playlists[user_id]:
            return False
        
        # Check if track already exists in playlist
        for existing_track in self.playlists[user_id][playlist_name]['tracks']:
            if existing_track.get('id') == track.get('id'):
                return True  # Track already in playlist
        
        self.playlists[user_id][playlist_name]['tracks'].append(track)
        self.save_playlists()
        return True
    
    def remove_track(self, user_id: str, playlist_name: str, track_id: str) -> bool:
        """Remove a track from a playlist"""
        if user_id not in self.playlists:
            return False
        
        if playlist_name not in self.playlists[user_id]:
            return False
        
        playlist = self.playlists[user_id][playlist_name]
        playlist['tracks'] = [
            track for track in playlist['tracks'] 
            if track.get('id') != track_id
        ]
        
        self.save_playlists()
        return True
    
    def get_playlist(self, user_id: str, name: str) -> Optional[Dict]:
        """Get a specific playlist"""
        if user_id in self.playlists and name in self.playlists[user_id]:
            return self.playlists[user_id][name]
        return None
    
    def get_user_playlists(self, user_id: str) -> Dict:
        """Get all playlists for a user"""
        return self.playlists.get(user_id, {})
    
    def delete_playlist(self, user_id: str, name: str) -> bool:
        """Delete a playlist"""
        if user_id in self.playlists and name in self.playlists[user_id]:
            del self.playlists[user_id][name]
            self.save_playlists()
            return True
        return False
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()