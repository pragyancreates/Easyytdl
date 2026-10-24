# YouTube Video & Music Downloader (Python Edition)

Created by **@pragyancreates**

A unified, cross-platform CLI tool built in **Python** powered by **yt-dlp**, **FFmpeg**, and **Beets** (MusicBrainz), featuring a custom high-definition Braille/dotted structure startup banner in the terminal.

It downloads videos with format inspection and audio/video merging, downloads music (single songs and playlists) in **MP3** or **Opus**, maintains an `archive.txt` resume tracker, enriches metadata using **Beets (MusicBrainz)** with clean **YouTube fallback**, and automatically searches and embeds **online lyrics** (compatible with MusicBee, Foobar2000, VLC).

All metadata, artwork, and lyrics are embedded **100% inside the audio file itself** with zero folder clutter.

---

## ⚡ Quick Start (Works on ANY PC)

Simply double-click **`run.bat`** in Windows File Explorer:
- **No Python installed?** `run.bat` automatically downloads and installs Python silently for you without requiring admin privileges.
- **Missing packages or FFmpeg?** The script automatically installs `yt-dlp`, `beets`, `mutagen`, `requests`, `beautifulsoup4`, and FFmpeg.
- **Already have Python?** You can also run:
```bash
python downloader.py
```

---

## 🚀 Key Features

### 1. Automatic Zero-Configuration Setup (Works Out-of-the-Box)
- **Automatic Python Setup**: If Python is not found, `run.bat` automatically fetches and installs Python 3.12 for Windows.
- **Python Packages**: Automatically installs `yt-dlp`, `beets`, `mutagen`, `requests`, and `beautifulsoup4` via pip.
- **FFmpeg**: Automatically detected on system `PATH` or auto-downloaded into `bin/`.

### 2. YouTube Cookies Manager (Drag & Drop cookies.txt)
- **Bypass Bot & Sign-in Gates**: Option `[3]` lets you drag and drop your exported `cookies.txt` file directly into the terminal window.
- **Zero Configuration**: Automatically saves to `bin/cookies.txt` and seamlessly feeds `--cookies` to `yt-dlp` for all video and audio downloads.
- Resolves YouTube's *"Sign in to confirm you're not a bot"*, age-restricted video locks, and private playlist permissions.
- Easily replace or type `remove` to clear saved cookies at any time.

### 3. YouTube Video Downloader
- Prompts for a video URL and displays the complete table of available resolutions, framerates, codecs, and bitrates (`yt-dlp -F`).
- **Format Selection**:
  - Type `best` for the maximum video resolution merged with the best audio stream.
  - Or enter any specific format ID (e.g. `137` for 1080p, `399`, `22`). Video-only streams are automatically merged with the best audio stream.
  - Or specify custom combinations (e.g. `137+140`).
- **Containers**: Choose between **MP4** or **MKV**.
- Saved in: `Downloads/Videos/`.

### 3. Music Downloader with Beets & Lyrics Enrichment
- **Single Tracks & Playlists**: Accepts any song link or playlist URL (`list=...`).
- **Audio Formats**:
  - **MP3** (High Quality 320 kbps / universal compatibility)
  - **OPUS** (Best native YouTube stream, ~160 kbps, pristine quality)
- **Midway Resume (`archive.txt`)**:
  - Maintains `Downloads/Music/<Playlist Name>/archive.txt`.
  - If a download stops or is closed midway, running again with the same link **skips completed tracks instantly** and resumes.
- **Beets (MusicBrainz) Metadata Enrichment**:
  - Automatically queries the official **MusicBrainz** database via Beets for studio release information (official album, release date, track numbers, artist credits, genre).
  - **Clean Fallback**: If a song is not found on MusicBrainz (e.g. indie tracks, unreleased demos), the baseline YouTube metadata is kept intact.
- **Automated Lyrics Search & Embedding**:
  - Automatically searches online lyrics providers (LRCLIB & Lyrics.ovh).
  - Embeds lyrics directly into the audio file (`LYRICS` tag for Opus, `USLT` tag for MP3) so **MusicBee** immediately displays synchronized or static lyrics.
- **Zero File Clutter**:
  - Cover art, tags, and lyrics are all embedded directly inside each audio file.
  - No loose `.jpg`, `.info.json`, `.description`, or `.txt` files polluting your folder!

---

## 📂 Project Structure

```
Music and Youtube Video Downloader/
│
├── downloader.py               # Main Python application
├── run.bat                     # Quick launcher to double-click on Windows
│
├── bin/                        # Local database & config
│   ├── beets_config.yaml
│   └── beets.db
│
├── Downloads/
│   ├── Videos/                 # Downloaded video files (.mp4 / .mkv)
│   └── Music/
│       ├── <Playlist Name>/    # Dedicated folder per playlist
│       │   ├── archive.txt     # Resume tracker
│       │   ├── Song 1.opus     # Contains embedded cover art, tags & lyrics
│       │   ├── Song 2.opus
│       │   └── ...
│       │
│       └── Single Tracks/      # Non-playlist individual songs
│           ├── archive.txt
│           └── SingleSong.opus
└── README.md
```
