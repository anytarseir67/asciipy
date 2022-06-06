from asciipy import VideoConverter, ImageConverter, GifConverter, ConverterConfig, __version__ as version
import sys
from PIL import UnidentifiedImageError

_help = f"""
asciipy {version}

Usage:
asciipy [input_file] [output_file] [width] (optional, default=80)
"""

def main():
    try:
        _input = sys.argv[1]
        output = sys.argv[2]
    except IndexError:
        print(_help)
        return

    width = 80
    if len(sys.argv) == 4:
        width = int(sys.argv[3])
    conf = ConverterConfig(width=width)
    try:
        GifConverter(conf).convert(_input, output)
    except (UnidentifiedImageError, ValueError):
        try:
            ImageConverter(conf).convert(_input, output)
        except UnidentifiedImageError:
            VideoConverter(conf).convert(_input, output)
    print('Done!')

if __name__ == "__main__":
    main()