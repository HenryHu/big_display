#!/usr/bin/env python3

from PIL import Image
import subprocess
import sys

import local_config

TARGET_HEIGHT = 32
TARGET_WIDTH = 64

img = Image.open(sys.argv[1])
print(img.getbbox())
img = img.crop(img.getbbox())

def scale_size(w, h, tw, th):
    wr = w / tw
    hr = h / th
    if wr > hr:
        return (tw, int(h / wr))
    else:
        return (int(w / hr), th)

(w, h) = scale_size(img.width, img.height, TARGET_WIDTH, TARGET_HEIGHT)
img = img.resize((w, h))
print("output image:", w, " x ", h)

data = list(img.getdata())

if len(sys.argv) < 3:
    filename = 'out.bmp'
else:
    filename = sys.argv[2]

outf = open(filename, 'wb')

for x in range(img.width):
    for y in range(img.height):
        point = data[x * img.height + y]

        if type(point) == int:
            outf.write(bytes([point * 255]))
            outf.write(bytes([point * 255]))
        else:
            outf.write(bytes([point[0] & 0xf8 | ((point[1] & 0xe0) >> 5)]))
            outf.write(bytes([((point[1] & 0x1c) << 3) | ((point[2] & 0xf8) >> 3)]))

outf.close()

subprocess.check_call(["curl", "http://%s/bitmap/0/0/%d/%d" % (local_config.LOCAL_IP, w, h), "--data-binary", "@%s" % filename])
