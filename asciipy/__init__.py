from PIL import Image, ImageDraw, ImageFont
import cv2
import glob
import os
from imageio import mimread
from math import sqrt
from random import randint
from .url_ import urlcheck, download, requestsNotInstalled
from . import palettes

#typing imports
from io import IOBase
from typing import List, Tuple, Union, Any

__version__ = "0.0.1"

_chars = "gS#%@"

def _remap(x, in_min, in_max, out_min, out_max):
    return round((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)   

class BaseConverter:
    def __init__(self, width: int=80, palette: List[Tuple[int, int, int]]=None, char_list: str=None, font: Any=None, transparent: bool=False) -> None:
        self.url = False
        self.width: int = width
        self.palette: List[Tuple[int, int, int]] = palette
        self.chars = char_list or _chars
        self.font = font
        self.transparent = transparent
        self.mode = "RGBA" if self.transparent else "RGB"

    def _process_input(self, _input: Any) -> Any:
        if isinstance(_input, str):
            check = urlcheck(_input)
            if check:
                self.url = True
                return f"./downloaded/{download(_input)}"
            elif check == None:
                raise requestsNotInstalled("requests is required to convert from urls, install it directly, or install asciipy-any[url]")
        return _input
        
    def _get_color(self, col: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
        if self.palette != None:
            color_diffs = []
            for color in self.palette:
                cr, cg, cb = color
                color_diff = sqrt((col[0] - cr)**2 + (col[1] - cg)**2 + (col[2] - cb)**2)
                color_diffs.append((color_diff, color))

            # i fucking hate this, but it works so....
            x = min(color_diffs)[1]
            if self.transparent:
                x = list(x)
                x.append(col[3])
                x = tuple(x)
            return x
        return col

    def _process_text(self, img: Image.Image) -> Image.Image:
        lines = []
        _colors: List[List[Tuple[int, int, int]]] = []
        for x in range(img.height):
            line = []
            colors = []
            for i in range(img.width):
                _col = self._get_color(img.getpixel((i, x)))
                _bright = _col[0] + _col[1] + _col[2]
                char = self.chars[_remap(_bright, 0, 765, 0, len(self.chars)-1)]
                line.append(char)
                colors.append(_col)
            lines.append(line)
            _colors.append(colors)
        return self._draw_text(img, lines, _colors)

    def _draw_text(self, src: Image.Image, text: List[List[str]], colors: List[List[Tuple[int, int, int]]]) -> Image.Image:
        im = Image.new(mode=self.mode, size=(10000, 10000))
        d = ImageDraw.Draw(im)
        _x = 0
        _y = 0
        try:
            font = ImageFont.truetype(self.font, 128)
        except AttributeError:
            font = None
        for i, line in enumerate(text):
            for x, char in enumerate(line):
                d.text((_x, _y), char, fill=(colors[i][x]), font=font)
                _x += d.textsize(char, font=font)[0]
            _y += d.textsize(char, font=font)[1]
            _x = 0
        width, height = (src.width * d.textsize(char, font=font)[0], src.height *  d.textsize(char, font=font)[1])
        im = im.crop((0, 0, width, height))
        return im

    def convert(self, _input: Union[os.PathLike, IOBase, str], output: Union[os.PathLike, IOBase, str]) -> None:
        self.input = self._process_input(_input)
        self.output = output


class ImageConverter(BaseConverter):
    def __init__(self, width: int=80, palette: List[Tuple[int, int, int]]=None, char_list: str=_chars, font: Any=None, transparent: bool=False) -> None:
        super().__init__(width, palette, char_list, font, transparent)

    def convert(self, _input: Union[os.PathLike, IOBase, str], output: Union[os.PathLike, IOBase, str]) -> None:
        super().convert(_input, output)
        img = Image.open(self.input).convert(self.mode)
        aspect_ratio = img.width / img.height
        height = int(self.width / (2 * aspect_ratio))
        img = img.resize((self.width, height))
        final = self._process_text(img)
        final.save(self.output)


class GifConverter(BaseConverter):
    def __init__(self, width: int = 80, palette: List[Tuple[int, int, int]]=None, char_list: str=_chars, font: Any=None, transparent: bool=False, *, gif: bool=True) -> None:
        super().__init__(width, palette, char_list, font, transparent)
        self._gif = gif

    def convert(self, _input: Union[os.PathLike, IOBase, str], output: Union[os.PathLike, IOBase, str]) -> None:
        super().convert(_input, output)
        img = Image.open(self.input)
        img.load()
        aspect_ratio = img.width / img.height
        height = int(self.width / (2 * aspect_ratio))
        converted_frames: List[Image.Image] = []
        frames = mimread(self.input)
        # print is here so it doesn't falsely warn when using the default CLI
        print('WARNING: gif conversion is not yet fully functional, please report any bugs at: https://github.com/anytarseir67/asciipy/issues/new')
        for frame in frames:
            frame = Image.fromarray(frame).convert(self.mode).resize((self.width, height))
            converted_frames.append(self._process_text(frame))

        if self._gif:
            converted_frames.pop(0).save(self.output, save_all=True, append_images=converted_frames, loop=img.info['loop'], duration=img.info['duration'])
        else:
            converted_frames[0].save(self.output)


class VideoConverter(BaseConverter):
    def __init__(self, width: int=80, palette: List[Tuple[int, int, int]]=None, char_list: str=_chars, font: Any=None, transparent: bool=False, *, progress: bool=True) -> None:
        super().__init__(width, palette, char_list, font, transparent)
        self.progress: bool = progress
        self.height: int = None
        self.fps: int = None
        self._id: int = randint(0, 999999) 
        # used in the frames path so more than one converter can run in the same wd

    def convert(self, _input: Union[os.PathLike, IOBase, str], output: Union[os.PathLike, IOBase, str]) -> None:
        super().convert(_input, output)
        try:
            os.mkdir(f'./frames_{self._id}')
            vid = cv2.VideoCapture(self.input)
            self.fps = vid.get(cv2.CAP_PROP_FPS)
            total_frames = vid.get(cv2.CAP_PROP_FRAME_COUNT)
            i = 0
            while(vid.isOpened()):  
                img = vid.read()[1]
                if img is None: break
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(img)
                img = img.convert(self.mode)
                aspect_ratio = img.width / img.height
                self.height = int(self.width / (2 * aspect_ratio))
                img = img.resize((self.width, self.height))
                frame = self._process_text(img)
                frame.save(f'./frames_{self._id}/img{i}.png')
                if self.progress:
                    print(f"\r{round((i/total_frames)*100)}% complete", end='')
                i+=1
            self._combine()
        except KeyboardInterrupt:
            print('conversion interupted.')
        finally:
            print('clearing temp files...')
            self._clear()

    def _combine(self) -> None:
        os.system(f'ffmpeg -r {self.fps} -i ./frames_{self._id}/img%01d.png -y temp.mp4')
        os.system(f'ffmpeg -i temp.mp4 -i "{self.input}" -map 0:v -map 1:a -y {self.output}')

    def _clear(self) -> None:
        os.remove('./temp.mp4')
        for f in glob.glob(f'./frames_{self._id}/*'):
            os.remove(f)
        os.rmdir(f'./frames_{self._id}')
