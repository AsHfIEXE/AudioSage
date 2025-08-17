import sys
import os
import asyncio
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import discord
from discord.ext import commands
from dotenv import load_dotenv
from bot.audio.url_player import URLMusicPlayer
from bot.audio.library import MusicLibrary
from bot.audio.playlist_manager import PlaylistManager
from flask import Flask, jsonify, request
from threading import Thread

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize components
MUSIC_SERVER_URL = os.getenv('MUSIC_SERVER_URL', 'http://localhost:3000')
music_library = MusicLibrary(MUSIC_SERVER_URL)
playlist_manager = PlaylistManager()
music_players = {}  # Guild-specific players

def get_player(guild_id):
    if guild_id not in music_players:
        music_players[guild_id] = URLMusicPlayer(MUSIC_SERVER_URL)
    return music_players[guild_id]

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await bot.tree.sync()

# Voice commands
@bot.tree.command(name="join", description="Join your voice channel")
async def join(interaction: discord.Interaction):
    if not interaction.user.voice:
        await interaction.response.send_message("You need to be in a voice channel!", ephemeral=True)
        return
    
    channel = interaction.user.voice.channel
    await channel.connect()
    await interaction.response.send_message(f"Joined {channel.name}")

@bot.tree.command(name="leave", description="Leave voice channel")
async def leave(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        if interaction.guild.id in music_players:
            del music_players[interaction.guild.id]
        await interaction.response.send_message("Left voice channel")
    else:
        await interaction.response.send_message("Not in a voice channel", ephemeral=True)

# Playback commands
@bot.tree.command(name="play", description="Play a track by name")
async def play(interaction: discord.Interaction, query: str):
    if not interaction.user.voice:
        await interaction.response.send_message("You need to be in a voice channel!", ephemeral=True)
        return
    
    if not interaction.guild.voice_client:
        await interaction.user.voice.channel.connect()
    
    results = music_library.search(query)
    if not results:
        await interaction.response.send_message(f"No results found for: {query}", ephemeral=True)
        return
    
    player = get_player(interaction.guild.id)
    track = results[0]
    await player.add_to_queue(interaction, track)

@bot.tree.command(name="playnext", description="Play track next in queue")
async def playnext(interaction: discord.Interaction, query: str):
    if not interaction.user.voice:
        await interaction.response.send_message("You need to be in a voice channel!", ephemeral=True)
        return
    
    if not interaction.guild.voice_client:
        await interaction.user.voice.channel.connect()
    
    results = music_library.search(query)
    if not results:
        await interaction.response.send_message(f"No results found for: {query}", ephemeral=True)
        return
    
    player = get_player(interaction.guild.id)
    track = results[0]
    await player.add_to_queue(interaction, track, play_next=True)

@bot.tree.command(name="playurl", description="Play audio directly from a URL")
async def playurl(interaction: discord.Interaction, url: str):
    """Play audio directly from a URL"""
    # Validate URL format (basic check)
    if not url.startswith(('http://', 'https://')):
        await interaction.response.send_message("Please provide a valid HTTP/HTTPS URL", ephemeral=True)
        return
    
    if not interaction.user.voice:
        await interaction.response.send_message("You need to be in a voice channel!", ephemeral=True)
        return
    
    if not interaction.guild.voice_client:
        await interaction.user.voice.channel.connect()
    
    # Create a temporary track object
    track = {
        'id': f"url_{hash(url) % 1000000}",
        'title': url.split('/')[-1] or "Unknown URL Track",
        'artist': "URL Source",
        'album': "Direct URL",
        'url': url,
        'duration': "Unknown"
    }
    
    player = get_player(interaction.guild.id)
    await player.add_to_queue(interaction, track)

@bot.tree.command(name="skip", description="Skip current track")
async def skip(interaction: discord.Interaction):
    player = get_player(interaction.guild.id)
    await player.skip(interaction)

@bot.tree.command(name="stop", description="Stop playback and clear queue")
async def stop(interaction: discord.Interaction):
    player = get_player(interaction.guild.id)
    await player.stop(interaction)

# Queue management
@bot.tree.command(name="queue", description="Show current queue")
async def queue(interaction: discord.Interaction):
    player = get_player(interaction.guild.id)
    await player.show_queue(interaction)

@bot.tree.command(name="clear", description="Clear the queue")
async def clear(interaction: discord.Interaction):
    player = get_player(interaction.guild.id)
    await player.clear_queue(interaction)

@bot.tree.command(name="shuffle", description="Shuffle the queue")
async def shuffle(interaction: discord.Interaction):
    player = get_player(interaction.guild.id)
    await player.shuffle_queue(interaction)

@bot.tree.command(name="remove", description="Remove track from queue")
async def remove(interaction: discord.Interaction, position: int):
    player = get_player(interaction.guild.id)
    await player.remove_from_queue(interaction, position)

# Playback controls
@bot.tree.command(name="volume", description="Set playback volume (0-200)")
async def volume(interaction: discord.Interaction, volume: int):
    player = get_player(interaction.guild.id)
    await player.set_volume(interaction, volume/100.0)

@bot.tree.command(name="loop", description="Set loop mode (0=off, 1=track, 2=queue)")
async def loop(interaction: discord.Interaction, mode: int):
    player = get_player(interaction.guild.id)
    await player.set_loop(interaction, mode)

# Information commands
@bot.tree.command(name="nowplaying", description="Show current playing track")
async def nowplaying(interaction: discord.Interaction):
    player = get_player(interaction.guild.id)
    if player.current_track:
        track = player.current_track
        embed = discord.Embed(
            title="Now Playing",
            description=f"**{track.get('title', 'Unknown')}**",
            color=0x4ecdc4
        )
        embed.add_field(name="Artist", value=track.get('artist', 'Unknown'), inline=True)
        embed.add_field(name="Album", value=track.get('album', 'Unknown'), inline=True)
        if track.get('duration'):
            duration = int(track.get('duration'))
            embed.add_field(name="Duration", value=f"{duration//60}:{duration%60:02d}", inline=True)
        embed.add_field(name="Volume", value=f"{int(player.volume*100)}%", inline=True)
        modes = ["Off", "Track", "Queue"]
        embed.add_field(name="Loop Mode", value=modes[player.loop_mode], inline=True)
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("Nothing is currently playing", ephemeral=True)

# Library commands
@bot.tree.command(name="search", description="Search for music")
async def search(interaction: discord.Interaction, query: str):
    results = music_library.search(query)
    if not results:
        await interaction.response.send_message(f"No results found for: {query}", ephemeral=True)
        return
    
    embed = discord.Embed(
        title=f"Search Results for '{query}'",
        color=0xff6b6b
    )
    
    description = ""
    for i, track in enumerate(results[:10], 1):
        description += f"{i}. **{track.get('title', 'Unknown')}** - {track.get('artist', 'Unknown')}\n"
    
    embed.description = description
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="list", description="List all available tracks")
async def list_tracks(interaction: discord.Interaction):
    tracks = music_library.get_all_tracks()
    if not tracks:
        await interaction.response.send_message("No tracks available", ephemeral=True)
        return
    
    embed = discord.Embed(
        title=f"Music Library ({len(tracks)} tracks)",
        color=0x4ecdc4
    )
    
    description = ""
    for i, track in enumerate(tracks[:20], 1):
        description += f"{i}. **{track.get('title', 'Unknown')}** - {track.get('artist', 'Unknown')}\n"
    
    if len(tracks) > 20:
        description += f"\n... and {len(tracks) - 20} more tracks"
    
    embed.description = description
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="refresh", description="Refresh music library from server")
async def refresh(interaction: discord.Interaction):
    success = music_library.refresh_library()
    if success:
        await interaction.response.send_message(f"✅ Library refreshed! {len(music_library.get_all_tracks())} tracks available")
    else:
        await interaction.response.send_message("❌ Failed to refresh library", ephemeral=True)

# Server configuration commands
@bot.tree.command(name="setserver", description="Set the default music server URL")
async def setserver(interaction: discord.Interaction, url: str):
    """Set the default music server URL"""
    if not url.startswith(('http://', 'https://')):
        await interaction.response.send_message("Please provide a valid HTTP/HTTPS URL", ephemeral=True)
        return
    
    # Remove trailing slash
    url = url.rstrip('/')
    
    # Update the global music server URL
    global MUSIC_SERVER_URL
    MUSIC_SERVER_URL = url
    
    # Update all existing players
    for player in music_players.values():
        player.server_url = url
    
    await interaction.response.send_message(f"🎵 Music server URL updated to: {url}")

@bot.tree.command(name="serverinfo", description="Show current music server URL")
async def serverinfo(interaction: discord.Interaction):
    """Show current music server URL"""
    await interaction.response.send_message(f"🎵 Current music server: {MUSIC_SERVER_URL}")

# Playlist commands
@bot.tree.command(name="playlist_create", description="Create a new playlist")
async def playlist_create(interaction: discord.Interaction, name: str):
    user_id = str(interaction.user.id)
    playlist_manager.create_playlist(user_id, name)
    await interaction.response.send_message(f"Created playlist: {name}")

@bot.tree.command(name="playlist_add", description="Add track to playlist")
async def playlist_add(interaction: discord.Interaction, playlist_name: str, query: str):
    user_id = str(interaction.user.id)
    results = music_library.search(query)
    if not results:
        await interaction.response.send_message(f"No results found for: {query}", ephemeral=True)
        return
    
    track = results[0]
    if playlist_manager.add_track(user_id, playlist_name, track):
        await interaction.response.send_message(f"Added {track.get('title')} to {playlist_name}")
    else:
        await interaction.response.send_message(f"Playlist {playlist_name} not found", ephemeral=True)

@bot.tree.command(name="playlist_play", description="Play a playlist")
async def playlist_play(interaction: discord.Interaction, playlist_name: str):
    if not interaction.user.voice:
        await interaction.response.send_message("You need to be in a voice channel!", ephemeral=True)
        return
    
    if not interaction.guild.voice_client:
        await interaction.user.voice.channel.connect()
    
    user_id = str(interaction.user.id)
    playlist = playlist_manager.get_playlist(user_id, playlist_name)
    if not playlist:
        await interaction.response.send_message(f"Playlist {playlist_name} not found", ephemeral=True)
        return
    
    player = get_player(interaction.guild.id)
    for track in playlist['tracks']:
        await player.add_to_queue(interaction, track, silent=True)
    
    await interaction.response.send_message(f"Playing playlist: {playlist_name}")

@bot.tree.command(name="playlist_list", description="List your playlists")
async def playlist_list(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    playlists = playlist_manager.get_user_playlists(user_id)
    
    if not playlists:
        await interaction.response.send_message("You have no playlists", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="Your Playlists",
        color=0xff6b6b
    )
    
    description = ""
    for name, playlist in playlists.items():
        description += f"**{name}** ({len(playlist['tracks'])} tracks)\n"
    
    embed.description = description
    await interaction.response.send_message(embed=embed)

# Web API endpoints
def run_web_api():
    app = Flask(__name__)
    
    @app.route('/api/player/<int:guild_id>')
    def get_player_state(guild_id):
        if guild_id in music_players:
            return jsonify(music_players[guild_id].get_player_state())
        return jsonify({'error': 'Player not found'}), 404
    
    @app.route('/api/library')
    def get_library():
        return jsonify(music_library.get_all_tracks())
    
    @app.route('/api/search')
    def search_library():
        query = request.args.get('q', '')
        results = music_library.search(query)
        return jsonify(results)
    
    @app.route('/api/playurl/<int:guild_id>', methods=['POST'])
    def play_url(guild_id):
        """Play audio directly from a URL"""
        data = request.json
        url = data.get('url')
        
        if not url or not url.startswith(('http://', 'https://')):
            return jsonify({'error': 'Invalid URL'}), 400
        
        # Create temporary track
        track = {
            'id': f"url_{hash(url) % 1000000}",
            'title': url.split('/')[-1] or "Unknown URL Track",
            'artist': "URL Source",
            'album': "Direct URL",
            'url': url,
            'duration': "Unknown"
        }
        
        # Get player and add to queue
        player = get_player(guild_id)
        # In a real implementation, you'd trigger playback here
        # This is a simplified version
        
        return jsonify({'status': 'ok', 'track': track})
    
    @app.route('/api/server', methods=['GET'])
    def get_server_url():
        """Get current server URL"""
        return jsonify({'server_url': MUSIC_SERVER_URL})
    
    @app.route('/api/server', methods=['POST'])
    def set_server_url():
        """Set server URL"""
        global MUSIC_SERVER_URL
        data = request.json
        url = data.get('url', '').rstrip('/')
        
        if not url.startswith(('http://', 'https://')):
            return jsonify({'error': 'Invalid URL'}), 400
        
        MUSIC_SERVER_URL = url
        
        # Update all players
        for player in music_players.values():
            player.server_url = url
        
        return jsonify({'server_url': MUSIC_SERVER_URL})
    
    @app.route('/api/play/<int:guild_id>', methods=['POST'])
    def play_track(guild_id):
        data = request.json
        track_id = data.get('track_id')
        
        track = music_library.get_track_by_id(track_id)
        if not track:
            return jsonify({'error': 'Track not found'}), 404
        
        player = get_player(guild_id)
        # In a real implementation, you'd trigger playback through Discord
        return jsonify({'status': 'ok'})
    
    @app.route('/api/control/<int:guild_id>/<action>', methods=['POST'])
    def control_player(guild_id, action):
        player = get_player(guild_id)
        if not player:
            return jsonify({'error': 'Player not found'}), 404
        
        if action == 'play':
            # Implementation would trigger play
            pass
        elif action == 'pause':
            # Implementation would trigger pause
            pass
        elif action == 'skip':
            # Implementation would trigger skip
            pass
        elif action == 'stop':
            # Implementation would trigger stop
            pass
        elif action == 'volume':
            volume = request.json.get('volume', 100)
            player.volume = volume / 100.0
        elif action == 'loop':
            mode = request.json.get('mode', 0)
            player.loop_mode = mode
        
        return jsonify(player.get_player_state())
    
    app.run(host='0.0.0.0', port=5000)

# Start web API in background thread
web_api_thread = Thread(target=run_web_api)
web_api_thread.start()

bot.run(os.getenv('DISCORD_TOKEN'))
