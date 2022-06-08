[![Documentation Status](https://readthedocs.org/projects/asciipy-any/badge/?version=latest)](https://asciipy-any.readthedocs.io/?badge=latest)
[![pypi version](https://img.shields.io/pypi/v/asciipy-any?color=0F8&label=PyPi&logo=PyPi&logoColor=0F8&style=plastic)](https://pypi.org/project/asciipy-any/)
[![Discord](https://img.shields.io/discord/735647676086878238?color=697Ec4&label=discord&logo=discord&logoColor=697Ec4)](https://discord.gg/fDQPCBybVJ)

# asciipy
 python library and cli tool to convert images and videos to ascii

`pip install asciipy-any`

## Example output:
![image example](https://github.com/anytarseir67/asciipy/blob/master/examples/peepo-juicebox.png?raw=True) 
![gif example](https://github.com/anytarseir67/asciipy/blob/master/examples/bonk.gif?raw=True)

additional examples can be found in `/examples/`

## Command line usage:
`asciipy [input_file] [output_file] [width] (optional, default=80)`

**Command line examples**: 

* image with default size: `asciipy test.png ascii.png`

* video with default size: `asciipy test.mp4 ascii.mp4`

* image with custom size: `asciipy test.png ascii.png 160`

* video with custom size: `asciipy test.mp4 ascii.mp4 160`

## Optional dependencies (URL and Youtube support):
* *note: these libraries can be manually installed instead. `youtube_dl` can be used instead of `yt-dlp`*
* `asciipy-any[full]` will install `requests` and `yt-dlp` to enable downloading from urls and youtube videos.
* `asciipy-any[url]` will install `requests` to enable downloading from urls.
* `asciipy-any[youtube]` will install `yt-dlp` to enable downloading youtube videos.

## Python usage:

* you can find our documentation here: https://asciipy-any.readthedocs.io/

## Python examples:

**image to ascii cli**
```py
from asciipy import ImageConverter
import sys

img = ImageConverter()
img.convert(sys.argv[1], './ascii.png')
print(f"{sys.argv[1]} converted and written to ./ascii.png")
```

## Planned features:
* ~~proper gif support~~ (mostly done, but still to buggy to be considered finished)
* ability to write output as html
* ability to convert vectors (not sure how i could even go about this)

## need help?
* [join my discord server!](https://discord.gg/fDQPCBybVJ)

* [or my guilded server](https://www.guilded.gg/i/kJO6g5op) (i'm often not online here)
