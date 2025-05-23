#!/usr/bin/env python3
"""
Spotify Liked Songs to MP3 Downloader

This script downloads your Spotify liked songs by:
1. Fetching liked songs from Spotify API
2. Searching for each song on YouTube
3. Downloading and converting to MP3

Requirements:
- pip install spotipy yt-dlp requests
- Spotify Developer App credentials
- FFmpeg installed on your system
- Also add it to the path (/bin folder)
"""

import os
import re
import time
import json
from pathlib import Path
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import yt_dlp
from concurrent.futures import ThreadPoolExecutor, as_completed

class SpotifyDownloader:
    def __init__(self, client_id, client_secret, redirect_uri="http://127.0.0.1:3000/callback"):
        """Initialize the Spotify downloader with API credentials."""
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.sp = None
        self.download_folder = Path("Downloaded_Music")
        self.download_folder.mkdir(exist_ok=True)
        
        # Configure yt-dlp options
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'outtmpl': str(self.download_folder / '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
        }
    
    def authenticate_spotify(self):
        """Authenticate with Spotify API."""
        scope = "user-library-read"
        
        auth_manager = SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=scope
        )
        
        self.sp = spotipy.Spotify(auth_manager=auth_manager)
        print("✓ Successfully authenticated with Spotify")
    
    def get_liked_songs(self):
        """Fetch all liked songs from Spotify."""
        if not self.sp:
            raise Exception("Not authenticated with Spotify")
        
        print("Fetching liked songs from Spotify...")
        liked_songs = []
        offset = 0
        limit = 50
        
        while True:
            results = self.sp.current_user_saved_tracks(limit=limit, offset=offset)
            
            if not results['items']:
                break
            
            for item in results['items']:
                track = item['track']
                song_info = {
                    'name': track['name'],
                    'artist': ', '.join([artist['name'] for artist in track['artists']]),
                    'album': track['album']['name'],
                    'duration_ms': track['duration_ms'],
                    'popularity': track['popularity']
                }
                liked_songs.append(song_info)
            
            offset += limit
            print(f"Fetched {len(liked_songs)} songs so far...")
        
        print(f"✓ Found {len(liked_songs)} liked songs")
        return liked_songs
    
    def sanitize_filename(self, filename):
        """Remove invalid characters from filename."""
        return re.sub(r'[<>:"/\\|?*]', '', filename)
    
    def search_and_download_song(self, song_info):
        """Search for a song on YouTube and download it."""
        query = f"{song_info['artist']} - {song_info['name']}"
        safe_filename = self.sanitize_filename(f"{song_info['artist']} - {song_info['name']}")
        
        # Check if file already exists
        potential_files = list(self.download_folder.glob(f"{safe_filename}*"))
        if potential_files:
            return f"⏭️  Skipped (already exists): {query}"
        
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                # Search for the song on YouTube
                search_query = f"ytsearch1:{query}"
                
                # Extract info without downloading first
                info = ydl.extract_info(search_query, download=False)
                
                if 'entries' in info and len(info['entries']) > 0:
                    video_info = info['entries'][0]
                    
                    # Update output template for this specific download
                    custom_opts = self.ydl_opts.copy()
                    custom_opts['outtmpl'] = str(self.download_folder / f"{safe_filename}.%(ext)s")
                    
                    # Download the video
                    with yt_dlp.YoutubeDL(custom_opts) as ydl_download:
                        ydl_download.download([video_info['webpage_url']])
                    
                    return f"✓ Downloaded: {query}"
                else:
                    return f"❌ Not found: {query}"
                    
        except Exception as e:
            return f"❌ Error downloading {query}: {str(e)}"
    
    def download_all_songs(self, songs, max_workers=3):
        """Download all songs using multiple threads."""
        print(f"\nStarting download of {len(songs)} songs...")
        print(f"Download folder: {self.download_folder.absolute()}")
        print("-" * 50)
        
        successful_downloads = 0
        failed_downloads = 0
        skipped_downloads = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all download tasks
            future_to_song = {
                executor.submit(self.search_and_download_song, song): song 
                for song in songs
            }
            
            # Process completed downloads
            for future in as_completed(future_to_song):
                result = future.result()
                print(result)
                
                if "Downloaded" in result:
                    successful_downloads += 1
                elif "Skipped" in result:
                    skipped_downloads += 1
                else:
                    failed_downloads += 1
                
                # Small delay to avoid rate limiting
                time.sleep(0.5)
        
        print("-" * 50)
        print(f"Download Summary:")
        print(f"✓ Successfully downloaded: {successful_downloads}")
        print(f"⏭️  Skipped (already existed): {skipped_downloads}")
        print(f"❌ Failed: {failed_downloads}")
        print(f"📁 Files saved to: {self.download_folder.absolute()}")
    
    def save_playlist_info(self, songs):
        """Save playlist information to a JSON file."""
        playlist_file = self.download_folder / "playlist_info.json"
        with open(playlist_file, 'w', encoding='utf-8') as f:
            json.dump(songs, f, indent=2, ensure_ascii=False)
        print(f"✓ Playlist info saved to: {playlist_file}")

def main():
    """Main function to run the Spotify downloader."""
    print("Spotify Liked Songs Downloader")
    print("=" * 40)
    
    # Spotify API credentials - Replace with your own!
    CLIENT_ID = "your_spotify_client_id_here"
    CLIENT_SECRET = "your_spotify_client_secret_here"
    
    if CLIENT_ID == "your_spotify_client_id_here":
        print("❌ Please set up your Spotify API credentials first!")
        print("\nTo get your credentials:")
        print("1. Go to https://developer.spotify.com/dashboard")
        print("2. Create a new app")
        print("3. Copy your Client ID and Client Secret")
        print("4. Add 'http://localhost:8888/callback' as a redirect URI")
        print("5. Replace the credentials in this script")
        return
    
    try:
        # Initialize downloader
        downloader = SpotifyDownloader(CLIENT_ID, CLIENT_SECRET)
        
        # Authenticate with Spotify
        downloader.authenticate_spotify()
        
        # Get liked songs
        liked_songs = downloader.get_liked_songs()
        
        if not liked_songs:
            print("No liked songs found!")
            return
        
        # Save playlist info
        downloader.save_playlist_info(liked_songs)
        
        # Ask user if they want to proceed with download
        response = input(f"\nFound {len(liked_songs)} songs. Download all? (y/n): ").lower()
        if response != 'y':
            print("Download cancelled.")
            return
        
        # Download all songs
        downloader.download_all_songs(liked_songs)
        
    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    main()