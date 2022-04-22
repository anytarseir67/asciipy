import re
from io import BytesIO
from urllib import parse
import os
import shutil

from typing import Union

try:
    import requests
    req = True
except ImportError:
    req = False

try:
    try:
        import yt_dlp as youtube
    except ImportError:
        import youtube_dl as youtube
    yt_regex = re.compile(r'^((?:https?:)?\/\/)?((?:www|m|music)\.)?((?:youtube(-nocookie)?\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$')
    yt = True
except ImportError:
    yt = False

url = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)


_ext: str = None

class ytdlNotInstalled(Exception):
    pass

class requestsNotInstalled(Exception):
    pass

class VideoProcessor(youtube.postprocessor.PostProcessor):
    def run(self, info):
        global _ext
        _ext = info['filepath']
        shutil.move(_ext, f'./downloaded/{_ext}')
        return [], info


def urlcheck(text: str) -> Union[bool, None]:
    if req:
        return re.match(url, text) is not None
    return None


def download(url: str) -> str:
    try:
        os.mkdir('./downloaded')
    except FileExistsError:
        pass

    if re.match(yt_regex, url) is not None:
        if yt == False:
            raise ytdlNotInstalled("youtube-dl or yt-dlp are required to convert youtube videos. install one directly, or install asciipy-any[youtube]")
        with youtube.YoutubeDL(params={'format': 'mp4', 'noplaylist': True}) as downloader:
            downloader.add_post_processor(VideoProcessor())
            downloader.download(url)
        ext = _ext
    else:
        data = BytesIO()
        data.seek(0)
        with requests.get(url, stream=True) as r:
            for chunk in r.iter_content():
                data.write(chunk)
        data.seek(0)
        path = parse.urlparse(url).path
        ext = os.path.os.path.split(path)[1]
        with open(f'./downloaded/{ext}', 'wb') as f:
            f.write(data.read())

    return ext