import discord
import asyncio
from collections import deque
import random

class URLMusicPlayer:
    def __init__(self, server_url):
        self.server_url = server_url.rstrip('/')
        self.queue = deque()
        self.current_track = None
        self.is_playing = False
        self.volume = 1.0  # 0.0 to 2.0
        self.loop_mode = 0  # 0=off, 1=track, 2=queue
        self.voice_client = None
        
    async def add_to_queue(self, interaction, track, play_next=False, silent=False):
        if play_next and self.queue:
            # Insert after current track
            temp_queue = list(self.queue)
            temp_queue.insert(0, track)
            self.queue = deque(temp_queue)
        else:
            self.queue.append(track)
            
        if not silent:
            await interaction.response.send_message(f"Added to queue: {track.get('title', 'Unknown')}")
        
        if not self.is_playing:
            await self.play_next(interaction)
    
    async def play_next(self, interaction):
        # Handle loop modes
        if self.loop_mode == 1 and self.current_track and not len(self.queue):
            # Loop current track
            self.queue.appendleft(self.current_track)
        elif self.loop_mode == 2 and self.current_track:
            # Loop entire queue
            self.queue.append(self.current_track)
            
        if not self.queue:
            self.is_playing = False
            self.current_track = None
            return
            
        self.current_track = self.queue.popleft()
        self.is_playing = True
        
        # Get voice client
        voice_client = interaction.guild.voice_client
        if not voice_client:
            return
        
        try:
            # Get the audio URL
            audio_url = self.current_track.get('url')
            if not audio_url:
                # Construct URL from server base if needed
                file_path = self.current_track.get('file_path', '')
                audio_url = f"{self.server_url}/{file_path.lstrip('/')}"
            
            # Play the audio file directly from URL with volume
            def after_playing(error):
                if error:
                    print(f"Error playing track: {error}")
                # Schedule next track
                asyncio.run_coroutine_threadsafe(
                    self.play_next(interaction), 
                    interaction.client.loop
                )
            
            # Play with volume control
            source = discord.FFmpegPCMAudio(
                audio_url,
                options=f'-af "volume={self.volume}"'
            )
            
            voice_client.play(source, after=after_playing)
            
        except Exception as e:
            print(f"Error playing track: {e}")
            # Continue to next track
            await self.play_next(interaction)
    
    async def skip(self, interaction):
        voice_client = interaction.guild.voice_client
        
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            await interaction.response.send_message("⏭️ Skipped current track")
        else:
            await interaction.response.send_message("Nothing is playing", ephemeral=True)
    
    async def stop(self, interaction):
        voice_client = interaction.guild.voice_client
        if voice_client:
            voice_client.stop()
            self.queue.clear()
            self.current_track = None
            self.is_playing = False
            await interaction.response.send_message("⏹️ Stopped playback and cleared queue")
        else:
            await interaction.response.send_message("Not in a voice channel", ephemeral=True)
    
    async def show_queue(self, interaction):
        if not self.queue and not self.current_track:
            await interaction.response.send_message("Queue is empty")
            return
            
        embed = discord.Embed(
            title="Current Queue",
            color=0xff6b6b
        )
        
        description = ""
        if self.current_track:
            description += f"**Now Playing:** {self.current_track.get('title', 'Unknown')} "
            description += f"[{self.current_track.get('artist', 'Unknown')}]\n\n"
        
        for i, track in enumerate(self.queue, 1):
            description += f"{i}. {track.get('title', 'Unknown')} "
            description += f"[{track.get('artist', 'Unknown')}]\n"
            
            # Limit message length
            if len(description) > 3500 and i < len(self.queue):
                description += f"\n... and {len(self.queue) - i} more tracks"
                break
        
        embed.description = description
        await interaction.response.send_message(embed=embed)
    
    async def clear_queue(self, interaction):
        self.queue.clear()
        await interaction.response.send_message("🗑️ Queue cleared")
    
    async def shuffle_queue(self, interaction):
        if self.queue:
            queue_list = list(self.queue)
            random.shuffle(queue_list)
            self.queue = deque(queue_list)
            await interaction.response.send_message("🔀 Queue shuffled")
        else:
            await interaction.response.send_message("Queue is empty", ephemeral=True)
    
    async def remove_from_queue(self, interaction, position: int):
        if position <= 0 or position > len(self.queue):
            await interaction.response.send_message(f"Invalid position. Queue has {len(self.queue)} items", ephemeral=True)
            return
            
        queue_list = list(self.queue)
        removed_track = queue_list.pop(position - 1)
        self.queue = deque(queue_list)
        
        await interaction.response.send_message(f"Removed from queue: {removed_track.get('title', 'Unknown')}")
    
    async def set_volume(self, interaction, volume: float):
        """Set volume (0.0 to 2.0)"""
        if 0.0 <= volume <= 2.0:
            self.volume = volume
            await interaction.response.send_message(f"🔊 Volume set to {volume*100:.0f}%")
        else:
            await interaction.response.send_message("Volume must be between 0.0 and 2.0", ephemeral=True)
    
    async def set_loop(self, interaction, mode: int):
        """Set loop mode: 0=off, 1=track, 2=queue"""
        if mode in [0, 1, 2]:
            self.loop_mode = mode
            modes = ["off", "track", "queue"]
            await interaction.response.send_message(f"🔁 Loop mode set to {modes[mode]}")
        else:
            await interaction.response.send_message("Invalid loop mode. Use 0=off, 1=track, 2=queue", ephemeral=True)
    
    def get_player_state(self):
        """Get current player state for web UI"""
        return {
            'current_track': self.current_track,
            'queue': list(self.queue),
            'is_playing': self.is_playing,
            'volume': self.volume,
            'loop_mode': self.loop_mode
        }