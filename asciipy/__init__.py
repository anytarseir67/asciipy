from typing import List, Tuple
from PIL import Image, ImageDraw
import pickle
import numpy as np
import cv2
import glob
import os

charSet = "(SSS#g@@g#SSS("

_path = os.path.dirname(os.path.abspath(__file__))
lerped = pickle.load(open(f"{_path}/colors.pkl", "rb"))
LUT = np.load(f"{_path}/LUT.npy")

class BaseConverter:
    def __init__(self) -> None:
        pass

    def _render(self, img, index: int):
        lines = []
        _colors: List[Tuple[int, int, int]] = []
        for x in range(img.height):
            line = []
            colors = []
            for i in range(img.width):
                r, g, b = img.getpixel((i, x))
                idx = LUT[b, g, r]
                lerp = lerped[idx][2]
                line.append(charSet[lerp])
                colors.append((r, g, b))
            lines.append(line)
            _colors.append(colors)
        return self._draw_text(img, lines, _colors, index)

    def _draw_text(self, src, text: List[str], colors: List[Tuple[int, int, int]], _i: int) -> None:
        im = Image.new(mode="RGB", size=(10000, 10000))
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
    def __init__(self, _input: str, output: str, width: int=80) -> None:
        super().__init__()
        self.input: str = _input
        self.output: str = output
        self.width: int = width

    def convert(self):
        img = Image.open(self.input).convert('RGB')
        aspect_ratio = img.width / img.height
        height = int(self.width / (2 * aspect_ratio))
        img = img.resize((self.width, height))
        final = self._render(img, 0)
        final.save(self.output)


class VideoConverter(BaseConverter):
    def __init__(self, _input: str, output: str, width: int=80, progress: bool=True) -> None:
        super().__init__()
        self.input: str = _input
        self.output: str = output
        self.progress: bool = progress
        self.width: int = width
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
            aspect_ratio = img.width / img.height
            self.height = int(self.width / (2 * aspect_ratio))
            img = img.resize((self.width, self.height))
            self._render(img, i)
            if self.progress:
                print(f"\r{round((i/total_frames)*100)}% complete", end='')
            i+=1
        self._combine()
        self._clear()
        
    def _draw_text(self, src, text: List[str], colors: List[Tuple[int, int, int]], _i: int) -> None:
        tmp = super()._draw_text(src, text, colors, _i)
        tmp.save(f'./frames/img{_i}.png')

    def _combine(self) -> None:
        os.system(f'ffmpeg -r {self.fps} -i ./frames/img%01d.png -y temp.mp4')
        os.system(f'ffmpeg -i temp.mp4 -i {self.input} -map 0:v -map 1:a -y {self.output}')

    @staticmethod
    def _clear():
        for f in glob.glob('./frames/*'):
            os.remove(f)
        os.remove('./frames')
        os.remove('./temp.mp4')