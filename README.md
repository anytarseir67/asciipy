# asciipy
 python library and cli tool to convert images and videos to ascii

`pip install asciipy-any`

## Example output:
![image example](https://github.com/anytarseir67/asciipy/blob/main/examples/peepo-juicebox.png?raw=True) 
![gif example](https://github.com/anytarseir67/asciipy/blob/main/examples/bonk.gif?raw=True)

## Command line usage:
`asciipy [input_file] [output_file] [width] (optional, default=80)`

**Command line examples**: 

* image with default size: `asciipy test.png ascii.png`

* video with default size: `asciipy test.mp4 ascii.mp4`

* image with custom size: `asciipy test.png ascii.png 160`

* video with custom size: `asciipy test.mp4 ascii.mp4 160`

## Python usage:
asciipy provides three classes `VideoConverter`, `ImageConverter`, and `BaseConverter`

* *note:* `input` fields can accept a url to convert, instead of local media or buffers.

### **BaseConverter**: takes four positional arguments, `input`, `output`, `width`, and `palette`.
`os.PathLike, IOBase, str` **input**: input media to convert

`os.PathLike, IOBase, str` **output**: destination of the converted image

`int` **width**: desired width in ascii characters (height is implicit from the aspect ratio of the input) 

`List[Tuple[int, int, int]]` **palette**: optional custom color palette, list of RGB tuples currently 3 palettes are included in `asciipy.palettes`. `c64`, `nes`, and `cmd`


### **ImageConverter**: no additional arguments.

### **GifConverter**: takes 1 keyword argument, `gif`.
`bool` **gif**: if the converted output should be a gif, defaults to True. if False, the first frame of the gif will be output as a png

### **VideoConverter**: takes 1 keyword argument, `progress`.
`bool` **progress**: if a progress indicator should be printed during conversion

all converter classes implement a `.convert()` method, which takes no arguments, to start the conversion

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
* ~~proper gif support~~ (mostly done, but still to buggy to be considered finished)
* ability to write output as html
* ability to convert vectors (not sure how i could even go about this)

## need help?
* [join my discord server!](https://discord.gg/fDQPCBybVJ)

* [or my guilded server](https://www.guilded.gg/i/kJO6g5op) (i'm often not online here)
