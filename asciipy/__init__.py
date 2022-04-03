from PIL import Image, ImageDraw
import pickle
import numpy as np
import cv2
import glob
import os
from imageio import mimread

#typing imports
from io import IOBase
from typing import List, Tuple, Union

charSet = "(SSS#g@@g#SSS("

_path = os.path.dirname(os.path.abspath(__file__))
lerped = pickle.load(open(f"{_path}/colors.pkl", "rb"))
LUT = np.load(f"{_path}/LUT.npy")

class BaseConverter:
    def __init__(self, _input: Union[os.PathLike, IOBase, str], output: Union[os.PathLike, IOBase, str], width: int=80) -> None:
        self.input = _input
        self.output = output
        self.width: int = width

    def _render(self, img: Image.Image) -> Image.Image:
        lines = []
        _colors: List[List[Tuple[int, int, int]]] = []
        for x in range(img.height):
            line = []
            colors = []
            for i in range(img.width):
                r, g, b, a = img.getpixel((i, x))
                idx = LUT[b, g, r]
                lerp = lerped[idx][2]
                line.append(charSet[lerp])
                colors.append((r, g, b, a))
            lines.append(line)
            _colors.append(colors)
        return self._draw_text(img, lines, _colors)

    def _draw_text(self, src: Image.Image, text: List[List[str]], colors: List[List[Tuple[int, int, int]]]) -> Image.Image:
        im = Image.new(mode="RGBA", size=(10000, 10000))
        d = ImageDraw.Draw(im)
        _x = 0
        _y = 0
        for i, line in enumerate(text):
            for x, char in enumerate(line):
                d.text((_x, _y), char, fill=(colors[i][x]))
                _x += d.textsize(char)[0]
            _y += d.textsize(char)[1]
            _x = 0
        width, height = (src.width * d.textsize(char)[0], src.height *  d.textsize(char)[1])
        im = im.crop((0, 0, width, height))
        return im


class ImageConverter(BaseConverter):
    def __init__(self, _input: Union[os.PathLike, IOBase, str], output: str, width: int=80) -> None:
        super().__init__(_input, output, width)

    def convert(self):
        img = Image.open(self.input).convert('RGBA')
        aspect_ratio = img.width / img.height
        height = int(self.width / (2 * aspect_ratio))
        img = img.resize((self.width, height))
        final = self._render(img)
        final.save(self.output)


class GifConverter(BaseConverter):
    def __init__(self, _input: Union[os.PathLike, IOBase, str], output: str, width: int = 80, *, gif: bool=True) -> None:
        super().__init__(_input, output, width)
        self._gif = gif

    def convert(self):
        img = Image.open(self.input)
        img.load()
        aspect_ratio = img.width / img.height
        height = int(self.width / (2 * aspect_ratio))
        converted_frames: List[Image.Image] = []
        frames = mimread(self.input)
        for frame in frames:
            frame = Image.fromarray(frame).convert('RGBA').resize((self.width, height))
            converted_frames.append(self._render(frame))

        if self._gif:
            converted_frames.pop(0).save(self.output, save_all=True, append_images=converted_frames, loop=img.info['loop'], duration=img.info['duration'])
        else:
            converted_frames[0].save(self.output)


class VideoConverter(BaseConverter):
    def __init__(self, _input: Union[os.PathLike, IOBase, str], output: str, width: int=80, *, progress: bool=True) -> None:
        super().__init__(_input, output, width)
        self.progress: bool = progress
        self.height: int = None
        self.fps: int = None

    def convert(self):
        try:
            os.mkdir('./frames')
        except FileExistsError:
            pass
        vid = cv2.VideoCapture(self.input)
        self.fps = vid.get(cv2.CAP_PROP_FPS)
        total_frames = vid.get(cv2.CAP_PROP_FRAME_COUNT)
        i = 0
        while(vid.isOpened()):  
            img = vid.read()[1]
            if img is None: break
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            img = img.convert('RGBA')
            aspect_ratio = img.width / img.height
            self.height = int(self.width / (2 * aspect_ratio))
            img = img.resize((self.width, self.height))
            frame = self._render(img)
            frame.save(f'./frames/img{i}.png')
            if self.progress:
                print(f"\r{round((i/total_frames)*100)}% complete", end='')
            i+=1
        self._combine()
        self._clear()
        
    def _draw_text(self, src: Image.Image, text: List[List[str]], colors: List[List[Tuple[int, int, int]]]) -> Image.Image:
        return super()._draw_text(src, text, colors)

    def _combine(self) -> None:
        os.system(f'ffmpeg -r {self.fps} -i ./frames/img%01d.png -y temp.mp4')
        os.system(f'ffmpeg -i temp.mp4 -i {self.input} -map 0:v -map 1:a -y {self.output}')

    @staticmethod
    def _clear():
        os.remove('./temp.mp4')
        for f in glob.glob('./frames/*'):
            os.remove(f)
        os.remove('./frames')