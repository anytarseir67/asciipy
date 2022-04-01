from setuptools import setup
import pathlib
HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text().replace('`pip install asciipy-any`', '')

with open('requirements.txt') as f:
  requirements = f.read().splitlines()

setup(name='asciipy-any',
    version='0.1.1a1',
    description='python library and cli tool to convert images and videos to ascii.',
    long_description=README,
    long_description_content_type="text/markdown",
    author='anytarseir67',
    url='https://github.com/anytarseir67/asciipy',
    license="GPLv3",
    packages=['asciipy'],
    install_requires=requirements,
    package_data={'': ['./colors.pkl', './LUT.npy']},
    include_package_data=True,
    entry_points = {
        'console_scripts': ['asciipy=asciipy.cli:main'],
    }
    )