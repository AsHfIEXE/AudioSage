import json
import requests
import os
from typing import List, Dict, Optional

class MusicLibrary:
    def __init__(self, server_url):
        self.server_url = server_url.rstrip('/')  # Remove trailing slash
        self.library = []
        self.load_library()
    
    def load_library(self):
        """Load library from server API or JSON file"""
        try:
            # Option 1: Fetch from server API endpoint
            api_url = f"{self.server_url}/api/music"
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                self.library = response.json()
                return
            
            # Option 2: Load from local JSON file (fallback)
            if os.path.exists('library.json'):
                with open('library.json', 'r') as f:
                    self.library = json.load(f)
            else:
                # Create empty library
                self.library = []
                self.save_library()
                
        except Exception as e:
            print(f"Error loading library: {e}")
            self.library = []
    
    def save_library(self):
        """Save library to local file"""
        with open('library.json', 'w') as f:
            json.dump(self.library, f, indent=2)
    
    def refresh_library(self):
        """Refresh library from server"""
        try:
            api_url = f"{self.server_url}/api/music"
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                self.library = response.json()
                self.save_library()
                return True
        except Exception as e:
            print(f"Error refreshing library: {e}")
        return False
    
    def search(self, query: str) -> List[Dict]:
        """Search through library with improved matching"""
        results = []
        query = query.lower().strip()
        
        if not query:
            return self.library[:20]  # Return first 20 if no query
            
        for track in self.library:
            # Check multiple fields for matches
            searchable_text = f"{track.get('title', '')} {track.get('artist', '')} {track.get('album', '')}".lower()
            if query in searchable_text:
                results.append(track)
                
        # Sort by relevance (simplified)
        results.sort(key=lambda x: self._calculate_relevance(x, query), reverse=True)
        return results[:15]  # Return top 15 matches
    
    def _calculate_relevance(self, track: Dict, query: str) -> int:
        """Calculate how relevant a track is to the query"""
        score = 0
        searchable_text = f"{track.get('title', '')} {track.get('artist', '')} {track.get('album', '')}".lower()
        
        if query in track.get('title', '').lower():
            score += 10
        if query in track.get('artist', '').lower():
            score += 8
        if query in track.get('album', '').lower():
            score += 5
            
        return score
    
    def get_track_by_id(self, track_id: str) -> Optional[Dict]:
        """Get track by its ID"""
        for track in self.library:
            if track.get('id') == track_id:
                return track
        return None
    
    def get_all_tracks(self) -> List[Dict]:
        """Get all tracks"""
        return self.library