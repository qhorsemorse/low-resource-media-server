"""
Helper script to create sample placeholder files in media directory.
"""

from pathlib import Path
from config import MEDIA_DIR

def create_placeholders():
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    readme_file = MEDIA_DIR / "README_PLACE_YOUR_720P_MP4_FILES_HERE.txt"
    with open(readme_file, "w", encoding="utf-8") as f:
        f.write("Place your 720p .mp4 video files (and .mp3 / .flac music files) in this folder!\n")
        f.write("Subfolders like media/Movies, media/TV_Shows, media/Downloads are automatically supported.\n")
    print(f"Created media folder guide at: {readme_file}")

if __name__ == "__main__":
    create_placeholders()
