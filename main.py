from pytube import Playlist, YouTube
import json
import os
import sys
import requests
import re
import subprocess
import math
from datetime import datetime
import json
from config import *

p = Playlist(PLAYLIST_URL)

def download_hq_mp3(yt: YouTube, dirName: str, title: str) -> bool:
    """
    Download mp3 of Youtube video 
    """
    try:
        # download as mp4
        video = yt.streams.get_audio_only()
        output = video.download(output_path=dirName,  filename=f'{title}.mp4')
        # print(output)
        base, ext = os.path.splitext(output)
        print(base)
        # use ffmpeg to convert to mp3
        cmd = [FFMPEG_PATH, '-i', output, f'{base}.mp3']
        subprocess.run(cmd, shell=True)
        os.remove(output)
        return True
    except Exception as e:
        print(f"DOWNLOAD ERROR")
        print(e)
        with open(ERROR_PATH, 'a') as f:
            f.write(str(datetime.now()) + '\t')
            f.write(title + '\n')
        return False
        
def get_desc(url) -> str:
    """
    Get description of Youtube video and clean up
    """
    full_html = requests.get(url).text
    y = re.search(r'shortDescription":"', full_html)
    desc = ""
    bpm = ""
    count = y.start() + 19  # adding the length of the 'shortDescription":"
    while True:
        # get the letter at current index in text
        letter = full_html[count]
        if letter == "\"":
            if full_html[count - 1] == "\\":
                # this is case where the letter before is a backslash, meaning it is not real end of description
                desc += letter
                count += 1
            else:
                break
        else:
            desc += letter
            count += 1
    desc = desc.lower()
    desc = desc.replace('\\n', ' ')
    desc = desc.replace('\\r', ' ')
    return desc


def sanitize(title: str) -> str:
    """
    Sanitze Youtube title to avoid file read errors
    """
    title = re.sub(r'[^\x00-\x7f]',r'', title)
    title = title.lower()
    title = title.strip()
    title = title.replace(' ','_')
    toReplace = '[](){}"“.,@#*&<>:;/\\|?!' + "'"
    for char in toReplace:
        title = title.replace(char, '')
    return title

def get_chunks(text: str, size: int = 100, maxNumOfChunks: int = 10) -> list[list]:
    """
    Split text into chunks for easier reading (avoid long, singular line of text)
    """
    numOfChunks = min(math.ceil(len(text) / size), maxNumOfChunks)
    return [text[i*size : i*size + size] for i in range(numOfChunks) ]

# Main script start

HTML_BEGIN = f"""
<html>
<body>
<h2>Beats {str(datetime.now())}</h2>
<p>ENTRY</p>
"""

TEMPLATE = """
<h2>{vidNum}</h2>
<p>{title}</p>
<p>{author} | {url}</p>
<p>{desc}</p>
"""

HTML_END = """
</body>
</html>
"""

errors = []
count = 0
with open(RECORD_TEXT_PATH, 'w', encoding="utf-8") as f, open(RECORD_HTML_PATH, "w", encoding="utf-8") as f2:
    f2.write(HTML_BEGIN)
    for n in range(NUMBER_OF_DOWNLOADS):
        try:
            
            # get video data and sanitize

            url = p.video_urls[n]
            yt = YouTube(url)
            title = sanitize(yt.title)
            vidNum = p.length - n
            title = str(vidNum) + title
            desc = get_desc(url)
            print(yt.author)
            desc = desc.replace('bpm', '<b>bpm</b>')
            desc = desc.replace('key', '<b>key</b>')

            # write video data html file
            
            f2.write(TEMPLATE.format(vidNum=vidNum, title=title, author=yt.author, url=url, desc=desc))


            # uncomment for text file write

            # f.write(title)
            # f.write('\n')
            # f.write(yt.author)
            # f.write('\n')
            # for chunk in get_chunks(desc):
            #     f.write(chunk)
            #     f.write('\n')
            # f.write('\n')
            # f.write('=====================')
            # f.write('\n')
            # f.write('\n')

            # date = yt.publish_date
            # month_day = date.strftime("%Y-%m")
            # print(month_day)

            # create download directory if not exist

            os.makedirs(DL_OUTPUT_PATH, exist_ok=True)
            dirName = DL_OUTPUT_PATH + rf'\{yt.author}'
            os.makedirs(dirName, exist_ok=True)
 
            if not download_hq_mp3(yt, dirName, title):
                raise Exception
            else:
                count += 1
        except Exception as e:
            print(e)
            errors.append((vidNum, url, yt.author, title, n))
            continue
        # print(yt.vid_info)
    f2.write(HTML_END)


print(f"{count} / {NUMBER_OF_DOWNLOADS}")
for r in errors:
    print(r)

