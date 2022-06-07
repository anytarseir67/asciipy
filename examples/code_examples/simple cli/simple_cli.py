from asciipy import ImageConverter, BackgroundConfig
import sys

back = BackgroundConfig(enabled=True, alpha=True)
# create a background config that copys the sources alpha channel

img = ImageConverter(None, back)
# instantiate an image converter with the standard config, and the custom background config

img.convert(sys.argv[1], './ascii.png')
# convert an image from a path passed as an argument

print(f"{sys.argv[1]} converted and written to ./ascii.png")