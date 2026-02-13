#!/usr/bin/env python3
"""
Extract audio tracks from video files using FFmpeg.

Usage:
    python utils/extract_audio.py [input_folder] [output_folder]

Examples:
    python utils/extract_audio.py
    python utils/extract_audio.py video_files audio_files
    python utils/extract_audio.py "ChatExport_2024/video_files" "ChatExport_2024/audio_files"
"""

import subprocess
import sys
from pathlib import Path

# Supported video extensions
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mkv', '.mov', '.webm', '.flv', '.wmv', '.m4v'}

# Output audio format
AUDIO_FORMAT = 'mp3'
AUDIO_BITRATE = '192k'


def check_ffmpeg():
    """Check if FFmpeg is installed and accessible."""
    try:
        subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def extract_audio(video_path: Path, audio_path: Path) -> bool:
    """
    Extract audio from a video file.

    Args:
        video_path: Path to input video file
        audio_path: Path to output audio file

    Returns:
        True if successful, False otherwise
    """
    try:
        result = subprocess.run(
            [
                'ffmpeg',
                '-i', str(video_path),
                '-vn',                    # No video
                '-acodec', 'libmp3lame',  # MP3 codec
                '-ab', AUDIO_BITRATE,     # Bitrate
                '-y',                     # Overwrite output
                str(audio_path)
            ],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"  Error: {e}")
        return False


def process_folder(input_folder: Path, output_folder: Path, skip_existing: bool = True):
    """
    Process all video files in a folder.

    Args:
        input_folder: Folder containing video files
        output_folder: Folder for output audio files
        skip_existing: Skip files that already have extracted audio
    """
    # Find all video files
    video_files = [
        f for f in input_folder.iterdir()
        if f.is_file() and f.suffix.lower() in VIDEO_EXTENSIONS
    ]

    if not video_files:
        print(f"No video files found in {input_folder}")
        return

    print(f"Found {len(video_files)} video file(s)")

    # Create output folder
    output_folder.mkdir(parents=True, exist_ok=True)

    # Process each video
    success_count = 0
    skip_count = 0

    for i, video_path in enumerate(video_files, 1):
        audio_path = output_folder / f"{video_path.stem}.{AUDIO_FORMAT}"

        # Skip if already exists
        if skip_existing and audio_path.exists():
            print(f"[{i}/{len(video_files)}] Skipping (exists): {video_path.name}")
            skip_count += 1
            continue

        print(f"[{i}/{len(video_files)}] Processing: {video_path.name}")

        if extract_audio(video_path, audio_path):
            print(f"  -> {audio_path.name}")
            success_count += 1
        else:
            print(f"  Failed to extract audio")

    # Summary
    print(f"\nDone! Extracted: {success_count}, Skipped: {skip_count}, Failed: {len(video_files) - success_count - skip_count}")


def main():
    # Check FFmpeg
    if not check_ffmpeg():
        print("Error: FFmpeg not found!")
        print("Install it:")
        print("  winget install FFmpeg")
        print("  or download from https://ffmpeg.org/download.html")
        sys.exit(1)

    # Parse arguments
    input_folder = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("video_files")
    output_folder = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("audio_files")

    # Validate input folder
    if not input_folder.exists():
        print(f"Error: Input folder not found: {input_folder}")
        sys.exit(1)

    if not input_folder.is_dir():
        print(f"Error: Not a directory: {input_folder}")
        sys.exit(1)

    print(f"Input:  {input_folder.absolute()}")
    print(f"Output: {output_folder.absolute()}")
    print()

    process_folder(input_folder, output_folder)


if __name__ == "__main__":
    main()
