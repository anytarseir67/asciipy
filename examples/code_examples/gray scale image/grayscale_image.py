from asciipy import ImageConverter, ConverterConfig, BackgroundConfig
from typing import Tuple
import sys

conf = ConverterConfig(transparent=True)
back = BackgroundConfig(enabled=True, alpha=True, darken=1)
# create our custom configs


# create a custom converter class that creates grayscale images
class GrayScaleImage(ImageConverter):
    def _get_back_color(self, col: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
        gray = 0
        for i in col:
            gray += i
        gray = round(gray / 3)
        dark = self._darken_rgb(gray, gray, gray)
        return *dark, col[3]

    def _get_color(self, col: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
        gray = 0
        for i in col:
            gray += i
        gray = round(gray / 3)
        return (gray, gray, gray, col[3])

img = GrayScaleImage(conf, back) # instantiate our custom converter

img.convert(sys.argv[1], 'gray.png') # convert an image from a path passed as an argument

print(f"{sys.argv[1]} converted and written to ./gray.png")