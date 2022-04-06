import re
import requests
from io import BytesIO
from urllib import parse
import os

url = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

def urlcheck(text: str) -> bool:
    return re.match(url, text) is not None

def download(url: str) -> str:
    data = BytesIO()
    data.seek(0)
    with requests.get(url, stream=True) as r:
        for chunk in r.iter_content():
            data.write(chunk)
    data.seek(0)
    path = parse.urlparse(url).path
    ext = os.path.os.path.split(path)[1]
    try:
        os.mkdir('./downloaded')
    except FileExistsError:
        pass
    with open(f'./downloaded/{ext}', 'wb') as f:
        f.write(data.read())
    return ext