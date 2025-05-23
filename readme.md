# Spotify Downloader

A simple Python tool to download liked songs from Spotify To Mp3.

## Features

- Download liked songs from Spotify.
- Saves audio files in high quality.
- Fetches metadata (artist, album, cover art).
## How It Works

This tool downloads your Spotify liked songs by:
1. Fetching your liked songs using the Spotify API.
2. Searching for each song on YouTube.
3. Downloading and converting the audio to MP3 format.

## Spotify API Setup

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).
2. Click the **Create app** button.
3. Fill out the form:
    - **App name:** Any name (e.g., "My Music Downloader")
    - **App description:** Brief description (e.g., "Personal music downloader")
    - **Website:** Any URL or leave blank
    - **Redirect URI:** Add `http://127.0.0.1:3000/callback`
    - **APIs/SDKs:** Check "Web API"
4. Agree to the terms of service and click **Save**.

Make sure to copy your `Client ID` and `Client Secret` and add em into the donwloader.py(there is a place in main).

## Additional Notes
- Download the windows build from here `https://ffmpeg.org/download.html#build-windows`
- Ensure FFmpeg is installed and added to your system's PATH (the `/bin` folder).
- This script is for personal use only.
- Requires Spotify Developer App credentials.
## Requirements

- Python 3.7+
- `spotipy`
- `yt-dlp` (or `youtube-dl`)
- `ffmpeg`

Install dependencies:
```bash
pip install spotipy yt-dlp requests
```

## Notes

- Downloads use YouTube as the audio source.
- For personal use only. Respect Spotify's terms of service.
