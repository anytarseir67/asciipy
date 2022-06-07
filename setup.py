from setuptools import setup
import pathlib
import re

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text().replace("`pip install asciipy-any`", "")

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

version = ''
with open('asciipy/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

setup(
    name="asciipy-any",
    version=version,
    description="python library and cli tool to convert images and videos to ascii.",
    long_description=README,
    long_description_content_type="text/markdown",
    author="anytarseir67",
    url="https://github.com/anytarseir67/asciipy",
    license="GPLv3",
    packages=["asciipy"],
    install_requires=requirements,
    include_package_data=True,
    entry_points={
        "console_scripts": ["asciipy=asciipy.cli:main"],
    },
    extras_require={
        "full": ["yt-dlp", "requests"],
        "youtube": ["yt-dlp"],
        "url": ["requests"],
        'docs': [
            'sphinx',
            'sphinxcontrib_trio',
            'sphinxcontrib-websupport',
            'typing-extensions',
            'myst_parser'
        ],
    },
)
