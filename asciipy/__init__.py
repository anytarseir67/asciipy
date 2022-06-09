from PIL import Image, ImageDraw, ImageFont
import cv2
import glob
import os
from imageio import mimread
from math import sqrt
from random import randint
import colorsys
import multiprocessing
from itertools import islice
import sys

#typing imports
from io import IOBase
from typing import List, Tuple, Union, Any

# lib imports
from .url_ import urlcheck, download, requestsNotInstalled
from . import palettes

__version__ = "0.2.1"

_chars = "gS#%@"

def _remap(x, in_min, in_max, out_min, out_max):
    ind = round((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)
    if ind > out_max: ind = out_max
    return ind

class ConverterConfig:
    """class contaning configuration for BaseConverter, and its subclasses.

    Parameters
    ----------
    width: Optional[:class:`int`]
        width (in characters) of the output media. by default ``80``
    palette: Optional[List[Tuple[:class:`int`, :class:`int`, :class:`int`]]]
        custom color palette, list of RGB tuples. by default ``None``
    char_list: Optional[:class:`str`]
        custom character list (darkest -> brightest). by default ``gS#%@``
    font: Optional[:class:`os.PathLike` | :class:`io.IOBase` | :class:`str`]
        font used for characters in the output media. supports TrueType and OpenType fonts. by default ``None``
    font_size: Optional[:class:`int`]
        size of the font in points (font must support requested size). by default ``None``
    transparent: Optional[:class:`bool`]
        when true, the alpha channel from the input is preserved and applied to the output. otherwise the alpha channel is discarded. by default ``False``
    """
    def __init__(self, *, width: int=80, palette: List[Tuple[int, int, int]]=None, char_list: str=None, font: Union[os.PathLike, IOBase, str]=None, font_size: int=None, transparent: bool=False) -> None:
        self.width = width
        self.palette = palette
        self.char_list = char_list
        self.font = font
        self.font_size = font_size
        self.transparent = transparent

class BackgroundConfig:
    """class contanining configuration information for a converters background.

    Parameters
    ----------
    enabled: Optional[:class:`int`]
        enable the background system when true; note: when no config is passed to a converter, background is disabled. by default ``True``
    color: Optional[Tuple[:class:`int`, :class:`int`, :class:`int`]]
        color for the text background. by default ``None``
    alpha: Optional[:class:`bool`]
        when true, copy the alpha channel from the source media. by default ``True``
    palette:  Optional[List[Tuple[:class:`int`. :class:`int`, :class:`int`]]]
        optional color palette for the text background (R,G,B) 0-255 (overrides color). by default ``None``
    back_layer: Optional[Tuple[:class:`int`, :class:`int`, :class:`int`]]
        color of the "true" background (R,G,B) 0-255. by default ``None``
    back_threshold:  Optional[:class:`int`]
        any pixel with an alpha less than or equal to this threshold is condisdered part of the "true" background. by default ``0``
    darken: Optional[:class:`float`]
        all luma values are multiplied by this number. by default ``0.9``
    """
    def __init__(self, *, enabled: bool=True, color: Tuple[int, int, int]=None, alpha: bool=True, palette: List[Tuple[int, int, int]]=None, back_layer: Tuple[int, int, int]=None, back_threshold: int=0, darken: float=0.9):
        self.enabled = enabled
        self.color = color
        self.alpha = alpha
        self.palette = palette
        self.back_layer = back_layer
        self.back_threshold = back_threshold
        self.darken = darken

class BaseConverter:
    """base class for all converters.

    Parameters
    ----------
    config: Optional[:class:`ConverterConfig`]
        configuration for the converter. by default ``ConverterConfig()``
    background : Optional[:class:`BackgroundConfig`]
        configuration for the converters background. by default ``BackgroundConfig(enabled=False)``

    Attributes
    -----------
    width: :class:`int`
        width of the converters output in characters.
    palette: List[Tuple[:class:`int`, :class:`int`, :class:`int`]]
        the converters color palette.
    chars: Union[List[:class:`str`], :class:`str`]
        the converters character set (darkest -> lightest).
    font: Union[:class:`os.PathLike` | :class:`io.IOBase` | :class:`str`]
        the converters font.
    transparent: :class:`bool`
        if the converter copies the inputs alpha channel.
    """
    def __init__(self, config: ConverterConfig=None, background: BackgroundConfig=None) -> None:
        self.url = False
        if not isinstance(config, ConverterConfig):
            config = ConverterConfig()
        self.width: int = config.width
        self.palette: List[Tuple[int, int, int]] = config.palette
        if not isinstance(config.char_list, list) or not isinstance(config.char_list, str):
            config.char_list = _chars
        self.chars = config.char_list
        self.font = config.font
        self.font_size = config.font_size
        self.transparent = config.transparent
        if not isinstance(background, BackgroundConfig):
            background = BackgroundConfig(enabled=False)
        self._background = background
        self._mode = "RGBA" if self.transparent else "RGB"

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
            x = min(color_diffs)[1]
            if self.transparent:
                x = list(x)
                x.append(col[3])
                x = tuple(x)
            return x
        return col

    def _darken_rgb(self, r, g, b):
        h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
        l = max(min(l * self._background.darken, 1.0), 0.0)
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return int(r * 255), int(g * 255), int(b * 255)

    def _get_back_color(self, col: Tuple[int, int, int, int]) -> Tuple[int, int, int]:
        if self._background.palette == None:
            if self._background.alpha:
                if self._background.color == None :
                    _col2 = self._darken_rgb(col[0], col[1], col[2])
                    if self.transparent:
                        _col2 = list(_col2)
                        _col2.append(col[3])
                        _col2 = tuple(_col2)
                else:
                    if len(self._background.color) == 3:
                        _col2 = list(self._background.color)
                        _col2.append(col[3])
                        _col2 = tuple(_col2)
                    else:
                        _col2 = self._background.color
            else:
                _col2 = self._background.color or self._darken_rgb(col[0], col[1], col[2])
        else:
            color_diffs = []
            for color in self._background.palette:
                cr, cg, cb = color
                color_diff = sqrt((col[0] - cr)**2 + (col[1] - cg)**2 + (col[2] - cb)**2)
                color_diffs.append((color_diff, color))
            x = min(color_diffs)[1]
            if self._background.alpha:
                x = list(x)
                x.append(col[3])
                x = tuple(x)
            _col2 = x
        return _col2

    def _process_image(self, img: Image.Image) -> Image.Image:
        im = Image.new(mode=self._mode, size=(10000, 10000))
        d = ImageDraw.Draw(im)
        _x = 0
        _y = 0
        try:
            font = ImageFont.truetype(self.font, self.font_size)
        except AttributeError:
            font = None

        x_offset = d.textsize(self.chars[-1], font=font)[0]
        y_offset = d.textsize(self.chars[-1], font=font)[1]

        for x in range(img.height):
            for i in range(img.width):
                raw_color = img.getpixel((i, x))
                _col = self._get_color(raw_color)
                _bright = _col[0] + _col[1] + _col[2]
                char = self.chars[_remap(_bright, 0, 765, 0, len(self.chars)-1)]
                if self._background.enabled:
                    if self._background.back_layer != None:
                        d.rectangle((_x, _y, _x+x_offset, _y+y_offset), fill=(self._background.back_layer))
                    _col2 = self._get_back_color(raw_color)
                    if len(_col2) == 4:
                        if _col2[3] > self._background.back_threshold:
                            d.rectangle((_x, _y, (_x+x_offset)-1, (_y+y_offset)-1), fill=(_col2))
                    else:
                        d.rectangle((_x, _y, (_x+x_offset)-1, (_y+y_offset)-1), fill=(_col2))

                if len(_col) == 4:
                    if _col[3] > self._background.back_threshold:
                        d.text((_x, _y), char, fill=(_col), font=font)
                else:
                    d.text((_x, _y), char, fill=(_col), font=font)

                _x += x_offset
            _y += y_offset
            _x = 0
        width, height = (img.width * d.textsize(char, font=font)[0], img.height *  d.textsize(char, font=font)[1])
        im = im.crop((0, 0, width, height))
        return im

    def convert(self, _input: Union[os.PathLike, IOBase, str], output: Union[os.PathLike, IOBase, str]) -> None:
        """method to convert media, implemented by subclasses

        Parameters
        ----------
        input: Union[:class:`os.PathLike`, :class:`io.IOBase`, :class:`str`]
            input media to convert.
        output: Union[:class:`os.PathLike`, :class:`io.IOBase`, :class:`str`]
            destination fron the output media.

        Raises
        ------
        :class:`NotImplementedError`
            method is only implemented in subclasses.
        """
        self.input = self._process_input(_input)
        self.output = output
        if type(self) == BaseConverter:
            raise NotImplementedError("method only implemented in subclasses.")


class ImageConverter(BaseConverter):
    """converts images to ascii-images

    Parameters
    ----------
    config: Optional[:class:`ConverterConfig`]
        configuration for the converter. by default ``ConverterConfig()``
    background : Optional[:class:`BackgroundConfig`]
        configuration for the converters background. by default ``BackgroundConfig(enabled=False)``

    Attributes
    -----------
    width: :class:`int`
        width of the converters output in characters.
    palette: List[Tuple[:class:`int`, :class:`int`, :class:`int`]]
        the converters color palette.
    chars: Union[List[:class:`str`], :class:`str`]
        the converters character set (darkest -> lightest).
    font: Union[:class:`os.PathLike` | :class:`io.IOBase` | :class:`str`]
        the converters font.
    transparent: :class:`bool`
        if the converter copies the inputs alpha channel.
    """

    def __init__(self, config: ConverterConfig=None, background: BackgroundConfig=None) -> None:
        super().__init__(config, background)

    def convert(self, _input: Union[os.PathLike, IOBase, str], output: Union[os.PathLike, IOBase, str]) -> None:
        """method to convert images to ascii-images

        Parameters
        ----------
        input: Union[:class:`os.PathLike`, :class:`io.IOBase`, :class:`str`]
            input image to convert.
        output: Union[:class:`os.PathLike`, :class:`io.IOBase`, :class:`str`]
            destination fron the output image.
            
        Returns
        -------
        None
        """
        super().convert(_input, output)
        img = Image.open(self.input).convert(self._mode)
        aspect_ratio = img.width / img.height
        height = int(self.width / (2 * aspect_ratio))
        img = img.resize((self.width, height))
        final = self._process_image(img)
        final.save(self.output)


class GifConverter(BaseConverter):
    """converts gifs to ascii-gifs (or images)

    Parameters
    ----------
    config: Optional[:class:`ConverterConfig`]
        configuration for the converter. by default ``ConverterConfig()``
    background : Optional[:class:`BackgroundConfig`]
        configuration for the converters background. by default ``BackgroundConfig(enabled=False)``
    gif: Optional[:class:`bool`]
        when true, output all frames converted to ascii, otherwise output only the first frame. by default ``True``

    Attributes
    -----------
    width: :class:`int`
        width of the converters output in characters.
    palette: List[Tuple[:class:`int`, :class:`int`, :class:`int`]]
        the converters color palette.
    chars: Union[List[:class:`str`], :class:`str`]
        the converters character set (darkest -> lightest).
    font: Union[:class:`os.PathLike` | :class:`io.IOBase` | :class:`str`]
        the converters font.
    transparent: :class:`bool`
        if the converter copies the inputs alpha channel.
    """
    def __init__(self, config: ConverterConfig=None, background: BackgroundConfig=None, *, gif: bool=True) -> None:
        super().__init__(config, background)
        self._gif = gif

    def convert(self, _input: Union[os.PathLike, IOBase, str], output: Union[os.PathLike, IOBase, str]) -> None:
        """method to convert gifs to ascii-gifs (or images)

        Parameters
        ----------
        input: Union[:class:`os.PathLike`, :class:`io.IOBase`, :class:`str`]
            input gif to convert.
        output: Union[:class:`os.PathLike`, :class:`io.IOBase`, :class:`str`]
            destination fron the output gif (or image).

        Returns
        -------
        None
        """
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
            frame = Image.fromarray(frame).convert(self._mode).resize((self.width, height))
            converted_frames.append(self._process_image(frame))

        loop = img.info.get('loop') or 0
        if self._gif:
            converted_frames.pop(0).save(self.output, save_all=True, append_images=converted_frames, loop=loop, duration=img.info['duration'])
        else:
            converted_frames[0].save(self.output)


class VideoConverter(BaseConverter):
    """converts videos to ascii-videos

    Parameters
    ----------
    config: Optional[:class:`ConverterConfig`]
        configuration for the converter. by default ``ConverterConfig()``
    background: Optional[:class:`BackgroundConfig`]
        configuration for the converters background. by default ``BackgroundConfig(enabled=False)``
    progress: Optional[:class:`bool`]
        when true, print the percentage completion after each frame (disabled when ``converters > 1``). by default ``True``
    converters: Optional[:class:`int`]
        number of converter processes to spawn. by default ``1``

    Attributes
    -----------
    width: :class:`int`
        width of the converters output in characters.
    palette: List[Tuple[:class:`int`, :class:`int`, :class:`int`]]
        the converters color palette.
    chars: Union[List[:class:`str`], :class:`str`]
        the converters character set (darkest -> lightest).
    font: Union[:class:`os.PathLike` | :class:`io.IOBase` | :class:`str`]
        the converters font.
    transparent: :class:`bool`
        if the converter copies the inputs alpha channel.
    converters: :class:`int`
        number of converter processes what will be spawned when :meth:`~asciipy.VideoConverter.convert` is called.
    """
    def __init__(self, config: ConverterConfig=None, background: BackgroundConfig=None, *, progress: bool=True, converters: int=1) -> None:
        super().__init__(config, background)
        self.progress: bool = progress
        self.height: int = None
        self.fps: int = None
        self._id: int = randint(0, 999999)
        self.converters = converters
        # used in the frames path so more than one converter can run in the same wd

    def _render_process(self, frames: List[Image.Image], num: int) -> None:
        try:
            for frame in frames:
                _ascii = self._process_image(frame)
                _ascii.save(f'./frames_{self._id}/img{num}.png')
                num += 1
            return 
        except KeyboardInterrupt:
            sys.exit()

    @staticmethod
    def _chunk(it: list, size: int) -> ...:
        it = iter(it)
        return iter(lambda: tuple(islice(it, size)), ())

    def convert(self, _input: Union[os.PathLike, IOBase, str], output: Union[os.PathLike, IOBase, str]) -> None:
        """method to convert videos to ascii-videos

        Parameters
        ----------
        input: Union[:class:`os.PathLike`, :class:`io.IOBase`, :class:`str`]
            input video to convert.
        output: Union[:class:`os.PathLike`, :class:`io.IOBase`, :class:`str`]
            destination fron the output video.

        Returns
        -------
        None
        """
        super().convert(_input, output)
        try:
            os.mkdir(f'./frames_{self._id}')
            vid = cv2.VideoCapture(self.input)
            self.fps = vid.get(cv2.CAP_PROP_FPS)
            total_frames = vid.get(cv2.CAP_PROP_FRAME_COUNT)
            i = 0
            frames = []
            while(vid.isOpened()):  
                img = vid.read()[1]
                if img is None: break
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(img)
                img = img.convert(self._mode)
                if i == 0:
                    aspect_ratio = img.width / img.height
                    self.height = int(self.width / (2 * aspect_ratio))
                img = img.resize((self.width, self.height))
                if self.converters == 1:
                    frame = self._process_image(img)
                    frame.save(f'./frames_{self._id}/img{i}.png')
                    if self.progress:
                        print(f"\r{round((i/total_frames)*100)}% complete", end='')
                else:
                    frames.append(img)
                i+=1

            if self.converters > 1:
                chunk_len = round(len(frames)/self.converters)
                chunks = list(self._chunk(frames, chunk_len))
                cur = 0
                processes = []
                for chunk in chunks:
                    p = multiprocessing.Process(target=self._render_process, args=(chunk, cur,))
                    p.start()
                    processes.append(p)
                    cur += chunk_len

                while not all([p.is_alive() for p in processes]):
                    pass

                for p in processes:
                    p.join()

            self._combine()
        except KeyboardInterrupt:
            print('conversion interupted.')
        finally:
            print('clearing temp files...')
            self._clear()

    def _combine(self) -> None:
        os.system(f'ffmpeg -r {self.fps} -i ./frames_{self._id}/img%01d.png -y temp.mp4')
        os.system(f'ffmpeg -i temp.mp4 -i "{self.input}" -map 0:v -map 1:a? -y {self.output}')

    def _clear(self) -> None:
        try:
            os.remove('./temp.mp4')
        except FileNotFoundError:
            pass
        for f in glob.glob(f'./frames_{self._id}/*'):
            os.remove(f)
        os.rmdir(f'./frames_{self._id}')