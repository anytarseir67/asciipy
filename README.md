# asciipy
 python library and cli tool to convert images and videos to ascii

`pip install asciipy-any`

## Command line usage:
`asciipy [input_file] [output_file] [width] (optional, default=80)`

**Command line examples**: 

* image with default size: `asciipy test.png ascii.png`

* video with default size: `asciipy test.mp4 ascii.mp4`

* image with custom size: `asciipy test.png ascii.png 160`

* video with custom size: `asciipy test.mp4 ascii.mp4 160`

## Python usage:
asciipy provides three classes `VideoConverter`, `ImageConverter`, and `BaseConverter`


* **BaseConverter**: provided for subclassing, and internal use


* **VideoConverter**: takes three positional arguments, `input`, `output`, `width`, and 1 keyword argument, `progress`

* * (os.PathLike, IOBase, str) **input**: input video to convert

* * (os.PathLike, IOBase, str) **output**: destination of the converted video

* * (int) **width**: desired width in ascii characters (height is implicit from the aspect ratio of the input) 

* * (bool) **progress**: if a progress indicator should be printed during conversion


* **ImageConverter**: takes three positional arguments, `input`, `output`, and `width`

* * (os.PathLike, IOBase, str) **input**: input image to convert

* * (os.PathLike, IOBase, str) **output**: destination of the converted image

* * (int) **width**: desired width in ascii characters (height is implicit from the aspect ratio of the input) 

both converter classes implement a `.convert()` method, which takes no arguments, to start the conversion

**Python examples**:

image to ascii cli
```py
from asciipy import ImageConverter
import sys

img = ImageConverter(sys.argv[1], './ascii.png')
img.convert()
print(f"{sys.argv[1]} converted and written to ./ascii.png")
```

## Planned features:
* proper gif support (partialy done, but still to buggy to be considered implemented)
* using the alpha channel of png's to preserve transparency, instead of filling blank spaces with `0, 0, 0`
* ability to pass url's to the input arguments
* ability to write output as html
* ability to convert vectors (not sure how i could even go about this)

## need help?
* [join my discord server!](https://discord.gg/fDQPCBybVJ)

* [or my guilded server](https://www.guilded.gg/i/kJO6g5op) (i'm often not online here)
