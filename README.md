# Playlist Download

Simple Python script I wrote which downloads all videos from a Youtube playlist as mp3s.

## Features

-   Downloads all Youtube videos as the highest quality mp3
-   Saves the title and description for each video in a HTML file for usage in a DAW (e.g. FL Studio)
-   Logs errors of videos that weren't able to be downloaded

## Installation

1. Ensure FFMPEG is installed and note .exe path
2. cd into repo
3. `pip install -r requirements.txt`

## Running

1. Edit config.py with your preferred file paths and number of videos to download
2. `python main.py`
