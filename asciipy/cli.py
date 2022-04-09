from asciipy import VideoConverter, ImageConverter, GifConverter
import sys
from PIL import UnidentifiedImageError

def main():
    try:
        _input = sys.argv[1]
        output = sys.argv[2]
    except IndexError:
        print('Usage:\nasciipy [input_file] [output_file] [width] (optional, default=80)')
        return

    width = 80
    if len(sys.argv) == 4:
        width = int(sys.argv[3])
    try:
        GifConverter(_input, output, width).convert()
    except (UnidentifiedImageError, ValueError):
        try:
            ImageConverter(_input, output, width).convert()
        except UnidentifiedImageError:
            VideoConverter(_input, output, width).convert()
    print('Done!')

if __name__ == "__main__":
    main()