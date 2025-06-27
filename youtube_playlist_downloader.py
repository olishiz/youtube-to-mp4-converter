#!/usr/bin/env python3
"""
YouTube Playlist Downloader

This script downloads all videos from a YouTube playlist using yt-dlp.
Videos are saved in highest-quality MP4 format to Desktop/videos folder.

Requirements:
- yt-dlp (install with: pip install yt-dlp)

Usage:
    python youtube_playlist_downloader.py [options]
    
Options:
    --url, -u URL          Specify playlist URL directly
    --use-default, -d      Use hardcoded default URL for testing
    
Examples:
    python youtube_playlist_downloader.py --use-default
    python youtube_playlist_downloader.py --url "https://www.youtube.com/playlist?list=YOUR_ID"
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def check_ytdlp_installed():
    """Check if yt-dlp is installed and accessible."""
    try:
        result = subprocess.run(['python', '-m', 'yt_dlp', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✓ yt-dlp version: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Error: yt-dlp is not installed or not accessible.")
        print("Please install it using: pip install yt-dlp")
        return False

def create_download_directory():
    """Create the videos directory on Desktop if it doesn't exist."""
    desktop_path = Path.home() / "Desktop"
    videos_path = desktop_path / "videos"
    
    try:
        videos_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Download directory ready: {videos_path}")
        return str(videos_path)
    except Exception as e:
        print(f"❌ Error creating directory {videos_path}: {e}")
        return None

def get_video_url(args=None):
    """Get video/playlist URL from command line argument, hardcoded value, or user input."""
    # Default hardcoded URLs for testing
    default_playlist_url = "https://www.youtube.com/playlist?list=PLO_7Kx05VzchqbmSOPNqZJ1s1h7uzR4Ha"
    default_video_url = "https://www.youtube.com/watch?v=ELgJ7SUqhP0"
    
    # Check if URL provided as command line argument
    if args and args.url:
        url_type = "single video" if "watch?v=" in args.url else "playlist"
        print(f"Using {url_type} URL from command line: {args.url}")
        return args.url
    
    # Check if we should use the hardcoded single video URL
    if args and args.single_video:
        print(f"Using hardcoded single video URL: {default_video_url}")
        return default_video_url
    
    # Check if we should use the hardcoded playlist URL (for automated testing)
    if args and args.use_default:
        print(f"Using hardcoded playlist URL: {default_playlist_url}")
        return default_playlist_url
    
    # Interactive mode - ask user for input
    print(f"\n💡 Tip: You can use --url <URL>, --use-default (playlist), or --single-video to skip this prompt")
    print(f"Default playlist URL: {default_playlist_url}")
    print(f"Default single video URL: {default_video_url}")
    
    while True:
        user_input = input("\nEnter YouTube URL (playlist or single video, or press Enter for default playlist): ").strip()
        
        # If user pressed Enter without input, use default playlist
        if not user_input:
            print(f"Using default playlist URL: {default_playlist_url}")
            return default_playlist_url
            
        # Accept any YouTube URL (playlist or single video)
        if "youtube.com" in user_input or "youtu.be" in user_input:
            return user_input
        else:
            print("⚠️  Warning: This doesn't appear to be a YouTube URL.")
            confirm = input("Continue anyway? (y/n): ").strip().lower()
            if confirm in ['y', 'yes']:
                return user_input
            else:
                continue

def cleanup_temp_files(directory):
    """Remove all extra files, keeping only final MP4 videos."""
    import glob
    
    # Patterns for files that should be removed (everything except .mp4, .mkv, .webm)
    unwanted_patterns = [
        '*.f*.mp4',         # Separate video files (e.g., f135.mp4)
        '*.f*.m4a',         # Separate audio files (e.g., f140.m4a)
        '*.f*.webm',        # Separate webm files
        '*.f*.mkv',         # Separate mkv files
        '*.info.json',      # Info JSON files
        '*.description',    # Description files
        '*.jpg',            # Thumbnail images
        '*.jpeg',           # Thumbnail images
        '*.png',            # Thumbnail images
        '*.webp',           # Thumbnail images
        '*.m4a',            # Audio-only files
        '*.srt',            # Subtitle files
        '*.vtt'             # Subtitle files
    ]
    
    cleaned_count = 0
    total_cleaned = 0
    
    # First, remove temporary format files only if merged version exists
    temp_patterns = ['*.f*.mp4', '*.f*.m4a', '*.f*.webm', '*.f*.mkv']
    for pattern in temp_patterns:
        temp_files = glob.glob(os.path.join(directory, pattern))
        for temp_file in temp_files:
            # Check if there's a corresponding merged file
            base_name = os.path.basename(temp_file)
            # Remove the format code (e.g., .f135.mp4 -> .mp4)
            merged_name = base_name.split('.f')[0] + '.mp4'
            merged_path = os.path.join(directory, merged_name)
            
            # Only remove temp file if merged version exists
            if os.path.exists(merged_path):
                try:
                    os.remove(temp_file)
                    cleaned_count += 1
                except OSError:
                    pass  # Ignore if we can't remove the file
    
    # Then remove all other unwanted files
    other_patterns = ['*.info.json', '*.description', '*.jpg', '*.jpeg', 
                     '*.png', '*.webp', '*.m4a', '*.srt', '*.vtt']
    for pattern in other_patterns:
        unwanted_files = glob.glob(os.path.join(directory, pattern))
        for unwanted_file in unwanted_files:
            try:
                os.remove(unwanted_file)
                total_cleaned += 1
            except OSError:
                pass  # Ignore if we can't remove the file
    
    if cleaned_count > 0 or total_cleaned > 0:
        print(f"🧹 Cleaned up {cleaned_count + total_cleaned} extra files (keeping only MP4 videos)")

def check_ffmpeg():
    """Check if ffmpeg is available."""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, check=True)
        print(f"✓ ffmpeg is available")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  ffmpeg not found. Using single-file format selection...")
        return False

def download_video_or_playlist(url, output_dir):
    """Download video(s) using yt-dlp with specified options."""
    # Determine if it's a single video or playlist
    is_single_video = "watch?v=" in url and "list=" not in url
    content_type = "single video" if is_single_video else "playlist"
    
    print(f"\n🚀 Starting download...")
    print(f"📂 Saving to: {output_dir}")
    print(f"🔗 {content_type.title()}: {url}")
    print("-" * 60)
    
    # Check for ffmpeg
    has_ffmpeg = check_ffmpeg()
    
    # Use best single file format to avoid ffmpeg requirement
    # Adjust output path based on content type
    if is_single_video:
        output_template = f'{output_dir}/Single Videos/%(title)s.%(ext)s'
    else:
        output_template = f'{output_dir}/%(playlist_title)s/%(title)s.%(ext)s'
    
    cmd = [
        'python', '-m', 'yt_dlp',
        '--format', 'best[ext=mp4]/best',  # Single file format
        '--output', output_template,
        '--ignore-errors',  # Skip unavailable videos
        '--continue',
        '--no-overwrites',
        '--skip-unavailable-fragments',  # Skip broken fragments
        '--abort-on-unavailable-fragment',
        '--no-abort-on-error',  # Don't stop on individual video errors
        '--ignore-config',  # Ignore any config files that might interfere
        url
    ]
    
    # Add playlist-specific options only for playlists
    if not is_single_video:
        cmd.insert(-1, '--yes-playlist')
    
    try:
        # Run yt-dlp with real-time output
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                                 stderr=subprocess.STDOUT, 
                                 universal_newlines=True, bufsize=1)
        
        print("📥 Download progress:")
        skipped_count = 0
        error_count = 0
        
        for line in process.stdout:
            # Print progress lines that contain useful information
            line = line.strip()
            if line:
                # Count skipped/error videos
                if any(skip_phrase in line.lower() for skip_phrase in 
                      ['video unavailable', 'private video', 'blocked', 'terminated', 'copyright']):
                    skipped_count += 1
                    print(f"   ⏭️  Skipped: {line}")
                elif 'error:' in line.lower():
                    error_count += 1
                    print(f"   ⚠️  {line}")
                elif any(keyword in line.lower() for keyword in 
                        ['downloading', 'finished', 'extracting', '%', 'playlist']):
                    print(f"   {line}")
        
        if skipped_count > 0:
            print(f"\n📊 Skipped {skipped_count} unavailable/private videos")
        
        process.wait()
        
        # Check if any files were actually downloaded and clean up
        playlist_dirs = [d for d in os.listdir(output_dir) if os.path.isdir(os.path.join(output_dir, d))]
        
        if playlist_dirs:
            playlist_dir = os.path.join(output_dir, playlist_dirs[0])
            
            # Clean up temporary files before counting
            cleanup_temp_files(playlist_dir)
            
            downloaded_files = [f for f in os.listdir(playlist_dir) 
                              if f.endswith(('.mp4', '.mkv', '.webm'))]
            
            if downloaded_files:
                print(f"\n✅ Download completed! Found {len(downloaded_files)} video files")
                print(f"📁 Files saved in: {playlist_dir}")
                return True
        
        if process.returncode == 0:
            print("\n✅ Download process completed successfully!")
            print(f"📁 Check files in: {output_dir}")
            return True
        else:
            print(f"\n⚠️  Download process finished with exit code: {process.returncode}")
            print("💡 Some videos may have downloaded successfully despite errors")
            print(f"📁 Check files in: {output_dir}")
            return True  # Don't fail completely if some files downloaded
            
    except KeyboardInterrupt:
        print("\n⏹️  Download interrupted by user.")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error during download: {e}")
        return False

def main():
    """Main function to orchestrate the download process."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Download YouTube videos and playlists using yt-dlp",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python youtube_playlist_downloader.py --use-default  # Download default playlist
  python youtube_playlist_downloader.py --single-video  # Download default single video
  python youtube_playlist_downloader.py --url "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID"
  python youtube_playlist_downloader.py --url "https://www.youtube.com/watch?v=VIDEO_ID"
  python youtube_playlist_downloader.py  # Interactive mode"""
    )
    parser.add_argument('--url', '-u', 
                       help='YouTube URL to download (playlist or single video)')
    parser.add_argument('--use-default', '-d', action='store_true',
                       help='Use the hardcoded default playlist URL for testing')
    parser.add_argument('--single-video', '-s', action='store_true',
                       help='Use the hardcoded default single video URL for testing')
    
    args = parser.parse_args()
    
    print("🎬 YouTube Video/Playlist Downloader")
    print("=" * 40)
    
    # Check if yt-dlp is installed
    if not check_ytdlp_installed():
        return 1
    
    # Create download directory
    output_dir = create_download_directory()
    if not output_dir:
        return 1
    
    # Get video/playlist URL from command line, default, or user input
    try:
        video_url = get_video_url(args)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        return 0
    
    # Download the video(s)
    success = download_video_or_playlist(video_url, output_dir)
    
    if success:
        print("\n🎉 All done! Enjoy your videos!")
        return 0
    else:
        print("\n💡 Tip: Check your internet connection and playlist URL.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)

