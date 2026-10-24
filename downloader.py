#!/usr/bin/env python3
"""
================================================================================
  YouTube Video & Music Downloader (Python Edition)
  Features:
    - Auto-dependency verification & installation (yt-dlp, FFmpeg, Beets, Mutagen)
    - YouTube Video download with format inspection & FFmpeg audio/video merging
    - Music download (Single tracks & Playlists) in MP3 or Opus
    - Resume capability with archive.txt tracker
    - Beets (MusicBrainz) metadata enrichment with clean YouTube fallback
    - Automated online lyrics search and embedding (MusicBee compatible)
    - Zero file clutter: cover art, tags, and lyrics embedded directly into audio
================================================================================
"""

import os
import sys
import re
import json
import shutil
import urllib.parse
import urllib.request
import subprocess
from pathlib import Path

# Configure UTF-8 for console output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Terminal ANSI colors
class Colors:
    CYAN = "\033[0;36m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    RED = "\033[0;31m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

# Project directories
SCRIPT_DIR = Path(__file__).resolve().parent
BIN_DIR = SCRIPT_DIR / "bin"
DOWNLOADS_DIR = SCRIPT_DIR / "Downloads"
VIDEOS_DIR = DOWNLOADS_DIR / "Videos"
MUSIC_DIR = DOWNLOADS_DIR / "Music"

BEETS_CONFIG = BIN_DIR / "beets_config.yaml"
BEETS_DB = BIN_DIR / "beets.db"
COOKIES_FILE = BIN_DIR / "cookies.txt"

# Ensure directories exist
for folder in [BIN_DIR, DOWNLOADS_DIR, VIDEOS_DIR, MUSIC_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# Add bin/ to PATH
os.environ["PATH"] = f"{BIN_DIR}{os.pathsep}{os.environ.get('PATH', '')}"


# Dotted structure (Braille ASCII Art) of Frieren
BANNER_ART = r"""⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠴⠖⢲⡄⢠⠤⠄⠒⠒⠐⠦⣅⠀⠒⠒⠒⠦⢤⣄⣀⠀⠀⣀⡤⠶⢶⣄⠀⢘⡑⠇⠀⠀⣹⣤⠀⠀⠀⠀
⠀⠀⢀⣠⡶⠿⠾⠿⡀⢤⣴⡉⠋⠀⢀⣀⣀⠀⠀⣀⣠⠤⠤⠤⠤⣝⠀⠀⠀⠉⠉⠉⠉⠙⠐⠾⣄⠈⠉⠉⠱⠍⠁⠀⠀⠀⠀⢸⠀⠀⠀⠀
⣀⢰⣋⠵⠒⠛⠓⠂⢌⡄⠉⣀⣊⣉⡉⠁⢀⠴⠊⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠦⣄⠀⢳⠀⠀⠀⠀⠀⢈⠇⠀⠀⠀
⠁⡚⠁⠀⠀⣠⡴⣶⠞⠋⠈⠁⠀⠀⢀⠔⠁⠀⠀⠀⠀⠀⠀⠀⣀⣀⣀⠀⠀⠀⠀⠀⢀⣀⠀⠀⠀⠀⠀⠈⠣⡀⢧⠀⠀⠀⠀⠸⠦⡄⣀⣀
⠈⠀⠀⠀⣴⠋⣠⠋⠀⠙⠒⠶⠀⡰⠋⠀⠀⠀⠀⠀⠀⣠⠖⠋⢉⠀⠈⠀⠀⠀⠀⠀⠈⣉⠑⢦⡀⠀⠀⠀⠀⠙⣆⠢⠀⠀⠀⠀⠀⠛⠉⡌
⠀⠀⠀⣸⠃⢠⠇⠀⣆⠀⠀⢀⡜⠁⠀⠀⠀⠀⠀⢠⠞⢁⡤⠞⠉⠀⠀⠀⠀⠀⠀⠀⠀⠈⠳⢄⠻⣄⠀⠀⠀⠀⠘⣦⠀⠀⠀⠀⠀⠀⠀⣧
⠀⠀⢠⡏⠀⣾⠀⠀⠘⢦⠀⡞⠀⠀⠀⠀⠀⠀⡰⢃⡴⠋⠀⠀⠀⠀⠀⠀⠀⢀⡀⠀⠀⠀⠀⠀⠑⢽⣆⠀⠀⠀⠀⠈⣧⠀⠀⠀⠀⠀⠀⠋
⠀⠀⢸⠁⢀⣿⡀⢡⠀⠀⡿⠀⠀⠀⠀⠀⠀⢰⣱⠏⠀⠀⠀⠀⠀⠀⠀⡰⠃⡼⢧⠠⡄⠀⠀⠀⠀⠀⢻⣆⠀⠀⠀⠀⢸⡆⠀⠀⠀⠀⠀⠀
⠀⠀⣿⠀⠘⢿⣇⡀⠀⢸⠃⠀⠀⠀⠀⠀⢠⡿⠃⠀⠀⠀⠀⠀⠀⠀⡴⢁⠞⠁⠈⠳⡙⣄⠀⠀⠀⠀⠀⢹⡄⠀⠀⠀⡀⠁⡀⠀⠀⠀⠀⠀
⠀⠀⡏⠀⢸⠘⡘⡔⢀⡌⠀⠀⠀⠀⠀⠀⣾⠁⠀⠀⠀⠀⠀⠀⢠⠞⡵⠃⠀⠀⠀⠀⠙⢌⢦⡀⠀⠀⠀⠀⢳⠀⠀⠀⢻⠠⠀⠀⠀⠀⠀⠀
⠀⢠⡇⠀⢸⡄⠱⡘⢾⠃⠀⠀⠀⠀⠀⢸⠇⠀⠀⠀⢀⠀⢠⣴⡏⠁⠀⠀⠀⠀⠀⠀⠀⠀⡁⠽⢦⣄⣀⠀⠸⡄⠀⠀⠸⡄⠆⠀⣀⣀⣤⡴
⠀⠸⡷⠤⠴⠷⠖⠻⢾⠀⠀⠀⠀⠀⠀⢸⠀⠀⠀⢈⡷⠾⣋⣀⠤⠷⠀⠀⠀⠀⠀⠀⠀⠚⠧⠤⠤⠛⠻⠦⣤⡇⣀⠀⠀⡇⢸⣹⠋⡟⢀⡴
⣤⠤⣤⠤⠤⢤⣤⣀⢸⠀⠀⠀⠀⢠⠀⢈⣀⡴⠞⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⣨⠀⠀⡇⢸⠏⠀⣠⠞⠀
⠿⠀⢧⡀⠀⠀⠀⠈⠽⠀⣄⠀⠀⢸⡄⢸⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠇⡟⠀⠀⡇⣋⡠⠾⠏⠀⢀
⢤⣀⠀⠙⠓⣤⣀⠸⣄⡀⢹⠀⠀⢸⣇⠸⠰⠶⠶⠶⢶⠴⣶⠶⠶⠖⠀⠀⠀⠀⠀⠀⠐⠛⠛⠻⠛⠿⠛⠛⠛⢰⠃⠀⢠⠁⠃⢰⡀⠀⠀⠈
⠀⠈⠹⣦⣄⡀⠈⠙⠲⣇⠈⢇⠀⠈⣿⡄⠆⠀⠀⣀⡘⢠⣀⣤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⠤⠌⠤⠖⢀⣰⠏⠀⠀⡾⠈⠀⠀⣷⠀⠀⠀
⡆⠀⠀⢿⣨⠟⠃⢡⣐⢋⣄⠈⣄⠀⢻⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠞⠋⠀⣠⡞⢻⠀⠀⠀⠸⣤⣤⣤
⡇⠀⠀⢸⣿⠀⠀⠈⣿⣄⣹⣧⡘⠄⠈⢿⡈⠷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢁⠀⣠⣾⢻⠧⠼⠦⢤⣤⠀⢹⢿⣭
⡇⠀⠀⠀⢿⡄⠀⠀⣿⡆⠈⠛⠻⢷⣄⠨⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⡄⠀⠀⠀⠀⠀⣀⣀⠀⠀⠭⣞⠋⠀⠀⠀⠀⠀⠀⠈⣷⠲⠦⠨
⣷⠀⠀⠀⠘⣷⡀⠀⣿⣧⠀⠀⠀⠀⠀⢀⡈⠛⠦⢤⣀⣀⣀⣀⣀⣀⡀⠀⠩⠤⠙⠛⡛⠻⠻⠿⣿⡷⠀⠠⣿⠁⠀⠀⠀⠀⠀⠀⣿⠀⢐⠶
⢹⡀⠀⠀⠀⢹⣷⡀⠙⠋⠀⠀⠀⣶⣏⢁⣤⣴⠖⠛⠛⠉⠉⠉⠙⠛⣻⣿⣿⣿⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⠀⠀⠀⠀⠀⠀⢀⣇⡀⠀⠉
⠸⣧⠀⠀⠀⠀⡿⣷⡄⠀⠀⠀⢀⡇⠉⠈⠛⠻⠿⠿⠿⠿⠟⠛⠛⢛⡋⠉⠉⠀⢸⡦⠀⠀⠀⢠⡄⠀⠀⠀⢺⣧⠀⠀⠀⠆⠀⣹⠫⠉⠓⠶
⠀⢻⣆⠀⠀⠀⡇⢿⣷⠀⠀⠂⠸⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠀⠀⠀⠀⣠⣶⣦⡇⠄⠀⠀⠀⠀⠀⠀⠀⣿⣿⡆⠂⠀⠀⢀⡟⠐⢄⠈⠉
⡀⠀⠹⣄⠀⠐⡇⠈⠋⠀⠀⠀⠀⣿⠀⠀⠀⠀⠀⢀⠀⢤⣀⡐⠂⠀⠀⣼⠟⠁⣹⡇⠀⠀⠀⠀⠀⠀⠀⠀⠉⣻⠁⠐⠀⠀⢸⡓⢀⠐⠀⣐
⠹⡄⠀⠘⣆⠀⢷⠛⠀⠀⠀⠀⠀⢸⡇⠀⢀⢰⢾⡿⠷⠶⠾⠿⠿⠿⣶⣤⡀⠺⠛⠁⠖⠀⠀⢀⣴⢾⣬⡽⠿⠿⠾⠿⣾⣤⠌⠁⢙⠷⣤⣠
⠀⠹⣆⠀⠘⡆⠈⠻⣧⡀⠀⠀⢀⣼⢃⡴⣏⣻⠊⠀⠀⠀⠀⠀⠀⠀⠀⠁⢻⣦⡘⠒⠀⢀⣴⡟⠋⠈⠀⠀⠀⠀⠀⠀⠈⢻⣷⠚⢠⡀⢀⠚"""


def print_banner():
    """Display the dotted structure ASCII art and creator tag at startup."""
    indent = "             "
    print("\n")
    for line in BANNER_ART.strip("\n").splitlines():
        print(f"{Colors.CYAN}{indent}{line}{Colors.RESET}")
    print(f"{indent}             {Colors.BOLD}{Colors.YELLOW}✨ @pragyancreates ✨{Colors.RESET}\n")


# ==============================================================================
# Dependency Checking & Installation
# ==============================================================================
def check_and_install_dependencies():
    """Verify and auto-install Python packages and FFmpeg."""
    print(f"{Colors.CYAN}================================================================================{Colors.RESET}")
    print(f"{Colors.BOLD}                   YOUTUBE VIDEO & MUSIC DOWNLOADER SETUP{Colors.RESET}")
    print(f"{Colors.CYAN}================================================================================{Colors.RESET}")
    print("[*] Checking required components...\n")

    # 1. Check Python packages
    required_packages = ["yt_dlp", "beets", "mutagen", "requests", "bs4"]
    missing_packages = []
    for pkg in required_packages:
        try:
            __import__(pkg)
        except ImportError:
            missing_packages.append("beautifulsoup4" if pkg == "bs4" else pkg.replace("_", "-"))

    if missing_packages:
        print(f" {Colors.YELLOW}[!] Missing Python packages:{Colors.RESET} {', '.join(missing_packages)}")
        print(" [*] Installing required packages via pip (please wait)...")
        cmd = [sys.executable, "-m", "pip", "install", "--quiet"] + missing_packages
        try:
            subprocess.run(cmd, check=True)
            print(f" {Colors.GREEN}[+] Python packages installed successfully.{Colors.RESET}")
        except Exception as e:
            print(f" {Colors.RED}[ERROR] Failed to install packages: {e}{Colors.RESET}")
            sys.exit(1)
    else:
        print(f" {Colors.GREEN}[OK]{Colors.RESET} Python packages (yt-dlp, beets, mutagen, requests, bs4) are ready.")

    # 2. Check FFmpeg
    ffmpeg_bin = shutil.which("ffmpeg") or shutil.which("ffmpeg.exe", path=str(BIN_DIR))
    if not ffmpeg_bin:
        print(f" {Colors.YELLOW}[!] FFmpeg is NOT detected.{Colors.RESET}")
        if sys.platform == "win32":
            print(" [*] Downloading FFmpeg build for Windows (approx. 190 MB, please wait)...")
            zip_path = BIN_DIR / "ffmpeg.zip"
            url = "https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
            try:
                urllib.request.urlretrieve(url, zip_path)
                print(" [*] Extracting FFmpeg binaries...")
                import zipfile
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    for member in zip_ref.namelist():
                        if member.endswith(("ffmpeg.exe", "ffprobe.exe")):
                            filename = os.path.basename(member)
                            target = BIN_DIR / filename
                            with zip_ref.open(member) as source, open(target, "wb") as dest:
                                shutil.copyfileobj(source, dest)
                zip_path.unlink(missing_ok=True)
                print(f" {Colors.GREEN}[+] FFmpeg installed successfully into bin/{Colors.RESET}")
            except Exception as e:
                print(f" {Colors.RED}[ERROR] Failed to download/extract FFmpeg: {e}{Colors.RESET}")
                sys.exit(1)
        else:
            print(f" {Colors.RED}[!] Please install FFmpeg using your package manager (e.g. sudo apt install ffmpeg / brew install ffmpeg).{Colors.RESET}")
            sys.exit(1)
    else:
        print(f" {Colors.GREEN}[OK]{Colors.RESET} FFmpeg is ready.")

    # 3. Ensure Beets config exists
    if not BEETS_CONFIG.exists():
        beets_yaml = (
            "# Local Beets configuration for Music Downloader\n"
            "plugins:\n"
            "  - musicbrainz\n"
            "  - lyrics\n\n"
            "import:\n"
            "  write: yes\n"
            "  copy: no\n"
            "  move: no\n"
            "  resume: no\n"
            "  autotag: yes\n"
            "  timid: no\n"
            "  quiet_fallback: asis\n\n"
            "match:\n"
            "  strong_rec_thresh: 0.20\n"
            "  medium_rec_thresh: 0.50\n\n"
            "musicbrainz:\n"
            "  searchlimit: 10\n"
        )
        BEETS_CONFIG.write_text(beets_yaml, encoding="utf-8")

    print(f"\n[*] {Colors.GREEN}All components are ready!{Colors.RESET}\n")


# ==============================================================================
# Helper Functions
# ==============================================================================
def sanitize_filename(name: str) -> str:
    """Sanitize strings for Windows / Unix directory names."""
    clean = re.sub(r'[<>:"/\\|?*]', '_', name).strip()
    return clean if clean else "Playlist"


def open_folder(folder_path: Path):
    """Open folder in OS default file manager."""
    try:
        if sys.platform == "win32":
            os.startfile(str(folder_path))
        elif sys.platform == "darwin":
            subprocess.run(["open", str(folder_path)], check=False)
        else:
            subprocess.run(["xdg-open", str(folder_path)], check=False)
    except Exception as e:
        print(f"Folder location: {folder_path} (could not launch explorer: {e})")


def run_ytdlp(args: list) -> int:
    """Run yt-dlp with realtime console output, automatically applying cookies if available."""
    cmd = [sys.executable, "-m", "yt_dlp"]
    if COOKIES_FILE.exists() and COOKIES_FILE.stat().st_size > 0:
        if "--cookies" not in args:
            cmd.extend(["--cookies", str(COOKIES_FILE)])
    cmd.extend(args)
    try:
        proc = subprocess.run(cmd)
        return proc.returncode
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[!] Operation canceled by user.{Colors.RESET}")
        return 130


# ==============================================================================
# Beets & Lyrics Enrichment Engine
# ==============================================================================
def fetch_online_lyrics(artist: str, title: str) -> str:
    """Fetch lyrics from LRCLIB and lyrics.ovh APIs."""
    if not artist or not title:
        return ""

    headers = {"User-Agent": "MusicDownloader/2.0"}

    # 1. Try LRCLIB API
    try:
        query = urllib.parse.urlencode({"artist_name": artist.strip(), "track_name": title.strip()})
        url = f"https://lrclib.net/api/get?{query}"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=7) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                lyrics = data.get("syncedLyrics") or data.get("plainLyrics")
                if lyrics and lyrics.strip():
                    return lyrics.strip()
    except Exception:
        pass

    # 2. Try Lyrics.ovh API
    try:
        clean_artist = urllib.parse.quote(artist.split(",")[0].split("&")[0].strip())
        clean_title = urllib.parse.quote(title.split("(")[0].split("[")[0].strip())
        url = f"https://api.lyrics.ovh/v1/{clean_artist}/{clean_title}"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=7) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                lyrics = data.get("lyrics", "")
                if lyrics and lyrics.strip():
                    return lyrics.strip()
    except Exception:
        pass

    return ""


def embed_lyrics_to_file(file_path: Path, lyrics: str) -> bool:
    """Embed lyrics directly into audio tags using Mutagen."""
    try:
        ext = file_path.suffix.lower()
        if ext == ".opus":
            from mutagen.oggopus import OggOpus
            audio = OggOpus(file_path)
            audio["lyrics"] = lyrics
            audio.save()
            return True
        elif ext == ".mp3":
            from mutagen.id3 import ID3, USLT, ID3NoHeaderError
            try:
                tags = ID3(file_path)
            except ID3NoHeaderError:
                tags = ID3()
            tags.delall("USLT")
            tags.add(USLT(encoding=3, lang="eng", desc="", text=lyrics))
            tags.save(file_path)
            return True
    except Exception as e:
        print(f"      {Colors.YELLOW}[!] Could not write lyrics tag: {e}{Colors.RESET}")
    return False


def get_tags(file_path: Path):
    """Retrieve artist and title from audio file tags."""
    artist, title = "", ""
    try:
        ext = file_path.suffix.lower()
        if ext == ".opus":
            from mutagen.oggopus import OggOpus
            audio = OggOpus(file_path)
            title = audio.get("title", [""])[0]
            artist = audio.get("artist", [""])[0]
        elif ext == ".mp3":
            from mutagen.id3 import ID3
            tags = ID3(file_path)
            title = str(tags.get("TIT2", ""))
            artist = str(tags.get("TPE1", ""))
    except Exception:
        pass
    return artist.strip(), (title.strip() if title else file_path.stem)


def has_embedded_lyrics(file_path: Path) -> bool:
    """Check if file already contains a lyrics tag."""
    try:
        ext = file_path.suffix.lower()
        if ext == ".opus":
            from mutagen.oggopus import OggOpus
            audio = OggOpus(file_path)
            return bool(audio.get("lyrics"))
        elif ext == ".mp3":
            from mutagen.id3 import ID3
            tags = ID3(file_path)
            return bool(tags.getall("USLT"))
    except Exception:
        pass
    return False


def clean_audio_tags(file_path: Path):
    """Pre-clean YouTube video title junk to ensure high-accuracy MusicBrainz matching."""
    try:
        import mutagen
        m = mutagen.File(str(file_path))
        if not m:
            return

        raw_title = ""
        raw_artist = ""
        if isinstance(m, mutagen.oggopus.OggOpus):
            raw_title = (m.get("title") or [""])[0]
            raw_artist = (m.get("artist") or [""])[0]
        elif isinstance(m, mutagen.mp3.MP3):
            if m.tags:
                raw_title = str(m.tags.get("TIT2", ""))
                raw_artist = str(m.tags.get("TPE1", ""))

        title = raw_title
        artist = raw_artist

        # If title is in "Artist - Title" format
        if " - " in title and (not artist or artist.lower() in title.lower()):
            parts = title.split(" - ", 1)
            artist = parts[0].strip()
            title = parts[1].strip()

        # Strip common YouTube noise patterns
        noise_patterns = [
            r"\(audio\)", r"\(official audio\)", r"\(official music video\)",
            r"\(official video\)", r"\(lyric video\)", r"\(lyrics\)",
            r"\(visualizer\)", r"\[official video\]", r"\[official audio\]",
            r"\[4k\]", r"\[hd\]", r"\(live\)", r"\(official visualizer\)"
        ]
        for pat in noise_patterns:
            title = re.sub(pat, "", title, flags=re.IGNORECASE).strip()

        # Strip featured artist from title for clean searching
        feat_pattern = r"[\(\[\s]+(?:ft|feat|featuring)\.?\s+([^\)\]]+)[\)\]]?"
        title = re.sub(feat_pattern, "", title, flags=re.IGNORECASE).strip()
        title = re.sub(r"[\s\-_]+$", "", title).strip()

        # Take primary artist if comma-separated
        if "," in artist:
            primary = artist.split(",")[0].strip()
            if primary:
                artist = primary

        # Save cleaned base tags
        if isinstance(m, mutagen.oggopus.OggOpus):
            if title:
                m["title"] = [title]
            if artist:
                m["artist"] = [artist]
            m.save()
        elif isinstance(m, mutagen.mp3.MP3):
            from mutagen.id3 import TIT2, TPE1
            if not m.tags:
                m.add_tags()
            if title:
                m.tags.add(TIT2(encoding=3, text=[title]))
            if artist:
                m.tags.add(TPE1(encoding=3, text=[artist]))
            m.save()
    except Exception:
        pass


def fetch_musicbrainz_metadata(artist: str, title: str):
    """Direct MusicBrainz search fallback for songs with minor duration discrepancies."""
    try:
        clean_a = artist.split(",")[0].strip() if artist else ""
        clean_t = re.sub(r"\(.*?\)|\[.*?\]", "", title).strip()
        query = f'recording:"{clean_t}" AND artist:"{clean_a}"' if clean_a else f'recording:"{clean_t}"'
        url = "https://musicbrainz.org/ws/2/recording?query=" + urllib.parse.quote(query) + "&fmt=json&limit=5"
        headers = {"User-Agent": "YouTubeMusicDownloader/2.1 ( contact@pragyancreates.io )"}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            recs = data.get("recordings", [])
            if recs:
                top = recs[0]
                rec_title = top.get("title") or title
                artist_credit = "".join([c.get("name", "") + c.get("joinphrase", "") for c in top.get("artist-credit", [])]) or artist
                releases = top.get("releases", [])
                album = releases[0].get("title") if releases else None
                date = releases[0].get("date") if releases else top.get("first-release-date")
                track_num = None
                if releases:
                    medium_list = releases[0].get("media", [])
                    if medium_list and medium_list[0].get("track"):
                        track_num = str(medium_list[0]["track"][0].get("number", "1"))
                return {
                    "title": rec_title,
                    "artist": artist_credit,
                    "album": album,
                    "date": date,
                    "tracknumber": track_num
                }
    except Exception:
        pass
    return None


def apply_metadata_to_file(file_path: Path, meta: dict):
    """Write verified MusicBrainz metadata into Opus or MP3."""
    try:
        import mutagen
        m = mutagen.File(str(file_path))
        if not m:
            return
        if isinstance(m, mutagen.oggopus.OggOpus):
            if meta.get("title"):
                m["title"] = [meta["title"]]
            if meta.get("artist"):
                m["artist"] = [meta["artist"]]
            if meta.get("album"):
                m["album"] = [meta["album"]]
            if meta.get("date"):
                m["date"] = [meta["date"]]
            if meta.get("tracknumber"):
                m["tracknumber"] = [meta["tracknumber"]]
            m.save()
        elif isinstance(m, mutagen.mp3.MP3):
            from mutagen.id3 import TIT2, TPE1, TALB, TDRC, TRCK
            if not m.tags:
                m.add_tags()
            if meta.get("title"):
                m.tags.add(TIT2(encoding=3, text=[meta["title"]]))
            if meta.get("artist"):
                m.tags.add(TPE1(encoding=3, text=[meta["artist"]]))
            if meta.get("album"):
                m.tags.add(TALB(encoding=3, text=[meta["album"]]))
            if meta.get("date"):
                m.tags.add(TDRC(encoding=3, text=[meta["date"]]))
            if meta.get("tracknumber"):
                m.tags.add(TRCK(encoding=3, text=[meta["tracknumber"]]))
            m.save()
    except Exception:
        pass


def enrich_audio_files(target_dir: Path):
    """Run Beets (MusicBrainz) autotagger and lyrics engine on downloaded tracks."""
    audio_files = []
    for ext in ["*.opus", "*.mp3"]:
        audio_files.extend(target_dir.glob(ext))

    if not audio_files:
        return

    print(f"\n{Colors.CYAN}================================================================================{Colors.RESET}")
    print(f"{Colors.BOLD}       METADATA & LYRICS ENRICHMENT (BEETS + MUSICBRAINZ + LRCLIB){Colors.RESET}")
    print(f"{Colors.CYAN}================================================================================{Colors.RESET}")
    print(f"[*] Found {len(audio_files)} track(s) to process.\n")

    for audio_file in audio_files:
        old_artist, old_title = get_tags(audio_file)
        display_name = f"{old_artist} - {old_title}" if old_artist else old_title
        print(f"[*] Processing: {Colors.BOLD}{audio_file.name}{Colors.RESET}")
        print(f"    Current info : {display_name}")

        # Pre-clean video title junk (e.g. "(Audio)", "(Official Music Video)")
        clean_audio_tags(audio_file)

        # 1. Beets MusicBrainz matching
        print("    [Beets] Querying MusicBrainz for official studio release metadata...")
        temp_db = BIN_DIR / f"temp_beets_{os.getpid()}.db"
        beet_cmd = [
            sys.executable, "-m", "beets",
            "-c", str(BEETS_CONFIG),
            "-l", str(temp_db),
            "import", "-s", "-q", "-C", str(audio_file)
        ]
        try:
            subprocess.run(beet_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=45)
        except Exception:
            pass
        finally:
            if temp_db.exists():
                try:
                    temp_db.unlink()
                except Exception:
                    pass

        new_artist, new_title = get_tags(audio_file)
        enriched = False
        if (new_artist and new_artist != old_artist) or (new_title and new_title != old_title):
            enriched = True
            print(f"    {Colors.GREEN}[+] Matched & enriched via Beets: {new_artist} - {new_title}{Colors.RESET}")

        # If Beets quiet threshold did not trigger, try Direct MusicBrainz search
        if not enriched:
            mb_meta = fetch_musicbrainz_metadata(new_artist or old_artist, new_title or old_title)
            if mb_meta and mb_meta.get("album"):
                apply_metadata_to_file(audio_file, mb_meta)
                new_artist = mb_meta.get("artist") or new_artist
                new_title = mb_meta.get("title") or new_title
                enriched = True
                print(f"    {Colors.GREEN}[+] Matched & enriched via MusicBrainz: {new_artist} - {new_title} [Album: {mb_meta.get('album')}]{Colors.RESET}")
            else:
                print("    [i] No official MusicBrainz match found -> Preserved YouTube metadata fallback")

        # 2. Lyrics search & embedding
        if has_embedded_lyrics(audio_file):
            print(f"    {Colors.GREEN}[+] Lyrics are already embedded.{Colors.RESET}")
        else:
            search_artist = new_artist or old_artist
            search_title = new_title or old_title
            print(f"    [*] Searching lyrics online for: '{search_title}' by '{search_artist}'...")
            lyrics = fetch_online_lyrics(search_artist, search_title)
            if lyrics:
                if embed_lyrics_to_file(audio_file, lyrics):
                    print(f"    {Colors.GREEN}[+] Lyrics successfully embedded into audio file!{Colors.RESET}")
            else:
                print("    [i] No lyrics available online (skipped).")

    # Clean up any leftover beets database backup files in bin/
    for backup in BIN_DIR.glob("*.bak"):
        try:
            backup.unlink()
        except Exception:
            pass

    print(f"\n{Colors.GREEN}[+] Enrichment complete! All metadata & lyrics are embedded directly in files.{Colors.RESET}")


# ==============================================================================
# Function 1: Video Downloader
# ==============================================================================
def download_video():
    """Download YouTube video with quality inspection and format merge."""
    print(f"\n{Colors.CYAN}================================================================================{Colors.RESET}")
    print(f"{Colors.BOLD}                          DOWNLOAD YOUTUBE VIDEO{Colors.RESET}")
    print(f"{Colors.CYAN}================================================================================{Colors.RESET}\n")

    url = input("Enter YouTube Video URL (or 'back' to return): ").strip().strip('"').strip("'")
    if not url or url.lower() == "back":
        return

    print(f"\n[*] {Colors.CYAN}Fetching available formats from YouTube... Please wait...{Colors.RESET}\n")
    if run_ytdlp(["-F", url]) != 0:
        print(f"\n{Colors.RED}[ERROR] Could not retrieve formats for this URL. Please verify the link.{Colors.RESET}")
        input("Press Enter to continue...")
        return

    print(f"\n{Colors.CYAN}--------------------------------------------------------------------------------{Colors.RESET}")
    print(f"{Colors.BOLD}FORMAT SELECTION GUIDE:{Colors.RESET}")
    print("  - Type 'best' for maximum resolution video + best audio stream merged automatically.")
    print("  - Or enter a specific Format ID from the table above (e.g. 137 for 1080p, 399).")
    print("    (Audio will be automatically downloaded and merged with it!)")
    print("  - Or enter a combined code like '137+140'.")
    print(f"{Colors.CYAN}--------------------------------------------------------------------------------{Colors.RESET}")
    format_id = input("Enter Format ID [Default: best]: ").strip() or "best"

    print("\nSelect Output Container:")
    print("  [1] MP4 (Recommended - universal compatibility)")
    print("  [2] MKV (Matroska - supports all codecs and soft subtitles)")
    container_choice = input("Choice (1 or 2) [Default: 1]: ").strip()
    container = "mkv" if container_choice == "2" else "mp4"

    # Build format argument
    if format_id.lower() == "best":
        f_param = "bestvideo+bestaudio/best"
    elif "+" in format_id:
        f_param = format_id
    else:
        f_param = f"{format_id}+bestaudio/best"

    print(f"\n{Colors.CYAN}================================================================================{Colors.RESET}")
    print(f"[*] Starting download and merge...")
    print(f"    Format      : {Colors.BOLD}{f_param}{Colors.RESET}")
    print(f"    Container   : {Colors.BOLD}{container}{Colors.RESET}")
    print(f"    Destination : {Colors.BOLD}{VIDEOS_DIR}{Colors.RESET}")
    print(f"{Colors.CYAN}================================================================================{Colors.RESET}\n")

    args = [
        "-f", f_param,
        "--merge-output-format", container,
        "--embed-metadata",
        "--embed-chapters",
        "--embed-thumbnail",
        "--no-mtime",
        "-o", str(VIDEOS_DIR / "%(title)s [%(id)s].%(ext)s"),
        url
    ]

    ret = run_ytdlp(args)
    if ret == 0:
        print(f"\n{Colors.GREEN}================================================================================{Colors.RESET}")
        print(f"{Colors.GREEN}[+] SUCCESS: Video downloaded and merged successfully!{Colors.RESET}")
        print(f"    Saved in: {Colors.BOLD}{VIDEOS_DIR}{Colors.RESET}")
        print(f"{Colors.GREEN}================================================================================{Colors.RESET}")
    else:
        print(f"\n{Colors.RED}[!] Download finished with notices or errors.{Colors.RESET}")

    input("\nPress Enter to return to main menu...")


# ==============================================================================
# Function 2: Music Downloader
# ==============================================================================
def download_music():
    """Download single music tracks or playlists with Beets & lyrics enrichment."""
    print(f"\n{Colors.CYAN}================================================================================{Colors.RESET}")
    print(f"{Colors.BOLD}                   DOWNLOAD MUSIC (SINGLE TRACK OR PLAYLIST){Colors.RESET}")
    print(f"{Colors.CYAN}================================================================================{Colors.RESET}\n")

    url = input("Enter YouTube Music link, song link, or playlist link: ").strip().strip('"').strip("'")
    if not url or url.lower() == "back":
        return

    print(f"\n{Colors.CYAN}--------------------------------------------------------------------------------{Colors.RESET}")
    print(f"{Colors.BOLD}Select Audio Format:{Colors.RESET}")
    print("  [1] MP3  (High Quality 320 kbps / universal compatibility for all players)")
    print("  [2] OPUS (Best native YouTube audio quality, ~160 kbps, modern)")
    print(f"{Colors.CYAN}--------------------------------------------------------------------------------{Colors.RESET}")
    audio_choice = input("Choice (1 or 2) [Default: 1]: ").strip()
    audio_format = "opus" if audio_choice == "2" else "mp3"

    is_playlist = False
    extra_flags = []
    if "list=" in url.lower():
        print(f"\n{Colors.YELLOW}[!] This URL contains a playlist identifier.{Colors.RESET}")
        print("  [1] Download the ENTIRE playlist")
        print("  [2] Download ONLY this single track")
        pl_choice = input("Choice (1 or 2) [Default: 1]: ").strip()
        if pl_choice == "2":
            extra_flags = ["--no-playlist"]
            is_playlist = False
        else:
            is_playlist = True

    print(f"\n[*] {Colors.CYAN}Analyzing link and retrieving metadata...{Colors.RESET}")
    try:
        query_cmd = [sys.executable, "-m", "yt_dlp", "--flat-playlist", "--playlist-items", "1", "--print", "%(playlist_title)s"] + extra_flags + [url]
        res = subprocess.run(query_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=15)
        raw_title = res.stdout.strip()
    except Exception:
        raw_title = "NA"

    if is_playlist and raw_title and raw_title != "NA":
        target_folder_name = sanitize_filename(raw_title)
    else:
        target_folder_name = "Single Tracks"

    target_dir = MUSIC_DIR / target_folder_name
    target_dir.mkdir(parents=True, exist_ok=True)
    archive_file = target_dir / "archive.txt"

    print(f"\n{Colors.CYAN}================================================================================{Colors.RESET}")
    print(f"  {Colors.BOLD}Music Download Configuration:{Colors.RESET}")
    print(f"   * Destination Folder : {Colors.BOLD}{target_dir}{Colors.RESET}")
    print(f"   * Playlist / Album   : {Colors.BOLD}{target_folder_name}{Colors.RESET}")
    print(f"   * Format             : {Colors.BOLD}{audio_format.upper()} (High Quality){Colors.RESET}")
    print(f"   * Resume Archive     : {Colors.BOLD}{archive_file}{Colors.RESET}")
    print(f"   * Embedding Mode     : {Colors.BOLD}100% Inside Audio (Cover, Title, Artist, Album, Track #){Colors.RESET}")
    print(f"{Colors.CYAN}================================================================================{Colors.RESET}\n")
    print(f"[*] {Colors.GREEN}Starting download... Interrupted downloads resume from where they left off.{Colors.RESET}\n")

    # yt-dlp arguments (clean embedded tags, NO loose sidecar files)
    dl_args = [
        "--ignore-errors",
        "--no-abort-on-error",
        "--download-archive", str(archive_file),
        "-x",
        "--audio-format", audio_format,
        "--audio-quality", "0",
        "--embed-metadata",
        "--embed-thumbnail",
        "--parse-metadata", "title:%(artist)s - %(title)s"
    ]

    if is_playlist:
        dl_args.extend([
            "--parse-metadata", "%(playlist_index)s:%(track_number)s",
            "--parse-metadata", "%(playlist_title,playlist)s:%(album)s"
        ])
    else:
        dl_args.extend(extra_flags)

    dl_args.extend([
        "--no-mtime",
        "-o", str(target_dir / "%(title)s.%(ext)s"),
        url
    ])

    ret = run_ytdlp(dl_args)

    # Run Beets & Lyrics enrichment directly on the downloaded tracks
    enrich_audio_files(target_dir)

    print(f"\n{Colors.GREEN}================================================================================{Colors.RESET}")
    print(f"{Colors.GREEN}[+] All files are saved in: {Colors.BOLD}{target_dir}{Colors.RESET}")
    print(f"    Resume tracker        : {Colors.BOLD}{archive_file}{Colors.RESET}")
    print(f"{Colors.GREEN}================================================================================{Colors.RESET}\n")

    open_choice = input("Open destination folder in File Explorer? (Y/N) [Default: Y]: ").strip().upper()
    if open_choice in ["", "Y", "YES"]:
        open_folder(target_dir)

    input("\nPress Enter to return to main menu...")


# ==============================================================================
# Function 3: YouTube Cookies Manager (Drag & Drop cookies.txt)
# ==============================================================================
def manage_cookies():
    """Import and manage cookies.txt via drag & drop for yt-dlp authentication."""
    print(f"\n{Colors.CYAN}================================================================================{Colors.RESET}")
    print(f"{Colors.BOLD}               YOUTUBE COOKIES MANAGER (DRAG & DROP COOKIES.TXT){Colors.RESET}")
    print(f"{Colors.CYAN}================================================================================{Colors.RESET}\n")

    if COOKIES_FILE.exists() and COOKIES_FILE.stat().st_size > 0:
        size_kb = COOKIES_FILE.stat().st_size / 1024
        print(f"  {Colors.GREEN}[✓] Current Status:{Colors.RESET} Active cookies loaded ({size_kb:.1f} KB)")
        print(f"      File path     : {COOKIES_FILE}\n")
        print("  Options:")
        print("    - Drag and drop a new cookies.txt file to replace the current one.")
        print("    - Type 'remove' to delete the saved cookies.")
        print("    - Type 'back' to return to the main menu.\n")
    else:
        print(f"  {Colors.YELLOW}[!] Current Status:{Colors.RESET} No cookies installed.")
        print("      Adding cookies enables downloading age-gated videos, private playlists,")
        print("      and resolves 'Sign in to confirm you're not a bot' or HTTP 429 errors.\n")
        print("  How to add:")
        print("    1. Export cookies from your browser (e.g. using 'Get cookies.txt LOCALLY' extension).")
        print("    2. Drag and drop the exported file directly into this terminal window and press Enter.")
        print("    (Or type 'back' to return)\n")

    raw_path = input("Drag & drop cookies.txt file here (or 'back'): ").strip()
    if not raw_path or raw_path.lower() == "back":
        return

    if raw_path.lower() in ["remove", "clear", "delete"]:
        if COOKIES_FILE.exists():
            try:
                COOKIES_FILE.unlink()
                print(f"\n{Colors.GREEN}[+] Cookies file removed successfully.{Colors.RESET}")
            except Exception as e:
                print(f"\n{Colors.RED}[ERROR] Could not delete cookies file: {e}{Colors.RESET}")
        else:
            print("\n[i] No cookies file to remove.")
        input("\nPress Enter to continue...")
        return

    # Clean path from terminal drag-and-drop (handles quotes and powershell '&' prefix)
    clean_path = raw_path.strip().strip("'").strip('"').strip()
    if clean_path.startswith("& "):
        clean_path = clean_path[2:].strip().strip("'").strip('"').strip()

    src_file = Path(clean_path)
    if not src_file.exists() or not src_file.is_file():
        print(f"\n{Colors.RED}[ERROR] File not found: '{clean_path}'{Colors.RESET}")
        print("Please ensure you dragged and dropped an existing file from File Explorer.")
        input("\nPress Enter to continue...")
        return

    try:
        content = src_file.read_text(encoding="utf-8", errors="ignore")
        if not content.strip():
            print(f"\n{Colors.RED}[ERROR] The dropped file is empty.{Colors.RESET}")
            input("\nPress Enter to continue...")
            return

        shutil.copy2(src_file, COOKIES_FILE)
        size_kb = COOKIES_FILE.stat().st_size / 1024
        print(f"\n{Colors.GREEN}[+] Cookies successfully imported! ({size_kb:.1f} KB){Colors.RESET}")
        print(f"    Saved to: {Colors.BOLD}{COOKIES_FILE}{Colors.RESET}")
        if "youtube" in content.lower():
            print(f"    {Colors.GREEN}[✓] YouTube authentication tokens detected.{Colors.RESET}")
        print(f"    yt-dlp will now automatically use this cookie session for all downloads.")
    except Exception as e:
        print(f"\n{Colors.RED}[ERROR] Could not import cookies file: {e}{Colors.RESET}")

    input("\nPress Enter to return to main menu...")


# ==============================================================================
# Main Menu
# ==============================================================================
def main():
    print_banner()
    check_and_install_dependencies()

    while True:
        try:
            import yt_dlp
            ytdlp_ver = getattr(yt_dlp.version, "__version__", "Installed")
        except Exception:
            ytdlp_ver = "Ready"

        cookie_status = f"{Colors.GREEN}Active (cookies.txt){Colors.RESET}" if COOKIES_FILE.exists() and COOKIES_FILE.stat().st_size > 0 else f"{Colors.YELLOW}None (Optional){Colors.RESET}"

        print(f"{Colors.CYAN}================================================================================{Colors.RESET}")
        print(f"{Colors.BOLD}            YOUTUBE VIDEO & MUSIC DOWNLOADER  •  @pragyancreates{Colors.RESET}")
        print(f"{Colors.CYAN}================================================================================{Colors.RESET}")
        print(f"  Components  : yt-dlp [{Colors.GREEN}{ytdlp_ver}{Colors.RESET}] | FFmpeg [{Colors.GREEN}Ready{Colors.RESET}] | Beets [{Colors.GREEN}Ready{Colors.RESET}]")
        print(f"  Cookies     : [{cookie_status}]")
        print(f"  Destination : {Colors.BOLD}{DOWNLOADS_DIR}{Colors.RESET}")
        print(f"{Colors.CYAN}================================================================================{Colors.RESET}\n")
        print("  Choose an option:\n")
        print(f"    {Colors.BOLD}[1]{Colors.RESET} Download YouTube Video (Select quality/format, auto-merge video+audio)")
        print(f"    {Colors.BOLD}[2]{Colors.RESET} Download Music / Songs (Single track or Playlist, Beets & Lyrics enrichment)")
        print(f"    {Colors.BOLD}[3]{Colors.RESET} Set YouTube Cookies (Drag & Drop cookies.txt to bypass bot/sign-in checks)")
        print(f"    {Colors.BOLD}[4]{Colors.RESET} Update yt-dlp & Beets to latest versions")
        print(f"    {Colors.BOLD}[5]{Colors.RESET} Open Downloads folder in File Explorer")
        print(f"    {Colors.BOLD}[6]{Colors.RESET} Exit\n")
        print(f"{Colors.CYAN}================================================================================{Colors.RESET}")

        choice = input("Enter choice (1-6): ").strip()

        if choice == "1":
            download_video()
        elif choice == "2":
            download_music()
        elif choice == "3":
            manage_cookies()
        elif choice == "4":
            print(f"\n[*] Updating yt-dlp and Beets via pip...")
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp", "beets", "mutagen"])
            input("\nUpdate finished. Press Enter to continue...")
        elif choice == "5":
            open_folder(DOWNLOADS_DIR)
        elif choice == "6":
            print(f"\n{Colors.GREEN}Thank you for using YouTube Video & Music Downloader!{Colors.RESET}")
            print(f"Files are saved in: {Colors.BOLD}{DOWNLOADS_DIR}{Colors.RESET}\n")
            sys.exit(0)
        else:
            print(f"\n{Colors.RED}[!] Invalid selection. Please enter a number from 1 to 6.{Colors.RESET}")


if __name__ == "__main__":
    main()
