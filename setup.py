import lib.local_debug as local_debug
from setuptools import setup

installs = [
    'pytest',
    'Adafruit_WS2801',
    'rpi-ws281x-python'
    'requests'
]

if not local_debug.is_debug():
    installs.append('RPi.GPIO')

setup(
    name='cateorical-sectional',
    version='2.0',
    python_requires='>=3.5',
    description='VFR weathermap supporting Adafruit WS2801 and ws281x lights.',
    url='https://github.com/Lexdysic/categorical-sectional',
    author='lexdysic',
    license='GPL V3',
    install_requires=installs)
