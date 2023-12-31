#!/usr/bin/env python3

from PIL import Image
import subprocess
import sys

import imagelib
import local_config

TARGET_HEIGHT = local_config.HEIGHT
TARGET_WIDTH = local_config.WIDTH

img = Image.open(sys.argv[1])
print(img.getbbox())
img = img.crop(img.getbbox())

buf = imagelib.img_to_565(img, TARGET_WIDTH, TARGET_HEIGHT)

if len(sys.argv) < 3:
    filename = 'out.bmp'
else:
    filename = sys.argv[2]

outf = open(filename, 'wb')
outf.write(buf)
outf.close()
