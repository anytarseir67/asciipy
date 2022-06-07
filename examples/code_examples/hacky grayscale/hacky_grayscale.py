from asciipy import BaseConverter, ImageConverter, VideoConverter, ConverterConfig
from typing import Tuple
import sys

conf = ConverterConfig(transparent=True)

def _get_color(self, col: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
    gray = 0
    for i in col:
        gray += i
    gray = round(gray / 3)
    return (gray, gray, gray, col[3])

BaseConverter._get_color = _get_color
# doing it this way allows us to change behavior for all converters 
# without having to inherit from them, or modify each separately.


im = ImageConverter(conf)

im.convert(sys.argv[1], './gray.png')

vid = VideoConverter(conf)

vid.convert(sys.argv[2], './gray.mp4')