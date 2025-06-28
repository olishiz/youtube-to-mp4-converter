# youtube-to-mp4-converter
Python application that lets you download videos from YouTube links and help to convert them to mp4 files locally.

# YouTube Playlist Downloader

A simple Python script to download all videos from a YouTube playlist (or single video) in the highest-quality MP4 format. Videos are saved to your Desktop/videos folder by default.

## Features
- Download entire YouTube playlists or single videos
- Saves videos in MP4 format to `Desktop/videos`
- Cleans up extra files, keeping only the final video files
- Command-line options for automation or interactive use

## Requirements
- Python 3.7+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)

## Installation
1. Clone this repository:
   ```sh
   git clone https://github.com/olishiz/youtube-to-mp4-converter.git
   cd youtube-to-mp4-converter
   ```
2. Install yt-dlp:
   ```sh
   pip install yt-dlp
   ```

## Usage
Run the script from the command line:

- **Download from a specific URL:**
  ```sh
  python youtube_playlist_downloader.py --url "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID"
  ```
  or
  ```sh
  python youtube_playlist_downloader.py --url "https://www.youtube.com/watch?v=VIDEO_ID"
  ```

## Output
- Videos are saved to a `videos` folder on your Desktop, organized by playlist or as single videos.

## Notes
- The script checks for `yt-dlp` and `ffmpeg` (optional, for best merging support).
- Only final video files are kept; extra files are cleaned up automatically.

## Troubleshooting
- If you see errors about `yt-dlp` not found, make sure you installed it with `pip install yt-dlp`.
- For best results, keep your `yt-dlp` up to date:
  ```sh
  pip install -U yt-dlp
  ```

## License
MIT
