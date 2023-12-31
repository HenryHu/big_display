#!/usr/bin/env python3
"""Convert an image to RGB565 binary data"""

import sys

from PIL import Image

import imagelib
import local_config

TARGET_HEIGHT = local_config.HEIGHT
TARGET_WIDTH = local_config.WIDTH

img = Image.open(sys.argv[1])
print(img.getbbox())
img = img.crop(img.getbbox())

buf = imagelib.img_to_565(img, TARGET_WIDTH, TARGET_HEIGHT)

filename = 'out.bmp' if len(sys.argv) < 3 else sys.argv[2]

with open(filename, 'wb') as outf:
    outf.write(buf)
