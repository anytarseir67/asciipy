# asciipy
 python library and cli tool to convert images and videos to ascii

`pip install asciipy-any`

## Example output:
![image example](https://github.com/anytarseir67/asciipy/blob/main/examples/peepo-juicebox.png?raw=True) 
![gif example](https://github.com/anytarseir67/asciipy/blob/main/examples/bonk.gif?raw=True)

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
asciipy provides four classes `ImageConverter`, `GifConverter`, `VideoConverter`, and `BaseConverter`

* *note:* `input` fields can accept a url to convert, instead of local media or buffers.

### **BaseConverter**: all other converters inherit from this class. 
* takes five positional arguments, `width`, `palette`, `char_list`, `font`, and `transparent`.
* `int` **width**: desired width in ascii characters (height is implicit from the aspect ratio of the input) 
* `List[Tuple[int, int, int]]` **palette**: optional custom color palette, list of RGB tuples. currently four palettes are included in `asciipy.palettes`. `c64`, `nes`, `cmd`, and `grayscale`
* `str` **char_list**: optional custom character list from darkest to brightest
* `os.PathLike, IOBase, str` **font**: optional font used for characters in the output media. supports TrueType and OpenType fonts.
* `bool` **transparent**: when True, the alpha channel from the input is preserved and applied to the output. otherwise the alpha channel is discarded (defaults to `False`)
* `bool` **background**: an instance of `asciipy.BackgroundConfig` (defaults to `BackgroundConfig(False, None, True)`)

**Methods**:

`convert`: method called to start conversion.
* takes 2 arguments, `input`, and `output`, and returns `None`.
* `os.PathLike, IOBase, str` **input**: input media to convert. can be a file, iobuffer, or url.
* `os.PathLike, IOBase, str` **output**: destination of the converted media.

### **ImageConverter**: class used for image conversion.
* takes no extra arguments.

### **GifConverter**: class used for gif conversion.
* takes one extra argument:
* `bool` **gif**: if the converted output should be a gif, defaults to `True`. if `False`, the first frame of the gif will be output as a png.

### **VideoConverter**: class used for conversion of videos.
* takes one extra argument:
* `bool` **progress**: if a progress indicator should be printed during conversion.

### **BackgroundConfig**:
* takes 4 keyword arguments:
* `bool` **enabled**: if the background system should be on.
* `Optional[Union[Tuple[int, int, int], Tuple[int, int, int, int]]]` **color**: replaces the background color, with the provided color.
* `bool` **alpha**: if the alpha channel should be copied from the source.

## Palettes:
custom color palettes can be provided to the constructor of any converter. it should be a list of rgb tuples. the order of the tuples does not matter, however the order **inside** the tuple must be RGB, or you will get unintended colors.

example (black and white):
```py
palette = [
    (0, 0, 0),
    (255, 255, 255)
]
```



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
