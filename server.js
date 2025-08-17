const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 3000;

// Serve static files from the 'music' directory if it exists
if (fs.existsSync(path.join(__dirname, 'music'))) {
    app.use('/music', express.static(path.join(__dirname, 'music')));
    console.log('🎵 Serving music files from /music directory');
} else {
    console.log('⚠️  Music directory not found. Create a "music" folder with your audio files.');
}

// API endpoint for music library
app.get('/api/music', (req, res) => {
    // Check if library.json exists for fallback
    const libraryPath = path.join(__dirname, 'library.json');
    if (fs.existsSync(libraryPath)) {
        try {
            const library = JSON.parse(fs.readFileSync(libraryPath, 'utf8'));
            res.json(library);
            return;
        } catch (e) {
            console.error('Error reading library.json:', e);
        }
    }
    
    // Default mock library if nothing else exists
    const mockLibrary = [
        {
            id: 'track_001',
            title: 'Example Song',
            artist: 'Example Artist',
            album: 'Example Album',
            duration: '180',
            url: 'http://localhost:3000/music/example.mp3',
            file_path: '/music/example.mp3',
            genre: 'Example',
            year: '2023'
        }
    ];
    
    res.json(mockLibrary);
});

app.listen(PORT, () => {
    console.log(`🎵 Music server running at http://localhost:${PORT}`);
    console.log(`📚 API endpoint: http://localhost:${PORT}/api/music`);
});