.. highlight:: python

quickstart
===========

Basic setup
------------
    :note: this lib is developed on python 3.8, and is not guaranteed to work on other versions.

    **installing:**
        to install or update from PyPi, run ``pip install -U asciipy-any``
        to install with optional dependencies for youtube and urls, run ``pip install -U asciipy-any[full]`` for all optional dependencies, or ``pip install -U asciipy-any[youtube]``/``pip install -U asciipy-any[url]``

    **video support:**
        to properly support video conversion, you will need to install `ffmpeg <https://ffmpeg.org/download.html>`_ manually.

Examples
---------

**Simple CLI**
~~~~~~~~~~~~~~~

    .. code-block:: python
        :linenos:

        from asciipy import ImageConverter, BackgroundConfig
        import sys

        back = BackgroundConfig(enabled=True, alpha=True)
        # create a background config that copys the sources alpha channel

        img = ImageConverter(None, back)
        # instantiate an image converter with the standard config, and the custom background config

        img.convert(sys.argv[1], './ascii.png')
        # convert an image from a path passed as an argument

        print(f"{sys.argv[1]} converted and written to ./ascii.png")

**Gray-Scale-image-converter**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. code-block:: python
        :linenos:

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

**Hacky Gray-Scale converters**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. code-block:: python
        :linenos:

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