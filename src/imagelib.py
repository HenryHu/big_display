"""Image processing utilities"""

from PIL import Image

import align

def scale_size(w, h, tw, th):
    wr = w / tw
    hr = h / th
    return (tw, int(h / wr)) if wr > hr else (int(w / hr), th)

def create(w, h):
    return Image.new('RGBA', (w, h))

def scale(img, outw, outh, halign=align.HAlign.MIDDLE, valign=align.VAlign.MIDDLE):
    (w, h) = scale_size(img.width, img.height, outw, outh)
    img = img.resize((w, h))

    canvas = Image.new('RGBA', (outw, outh))
    if valign == align.VAlign.LEFT:
        x = 0
    elif valign == align.VAlign.MIDDLE:
        x = (outw - w) // 2
    else:
        x = outw - w

    if halign == align.HAlign.TOP:
        y = 0
    elif halign == align.HAlign.MIDDLE:
        y = (outh - h) // 2
    else:
        y = outh - h

    canvas.paste(img, (x, y))
    return canvas

def to_565(img):
    data = list(img.getdata())
    buf = bytearray(img.width * img.height * 2)
    pos = 0
    for y in range(img.height):
        for x in range(img.width):
            point = data[y * img.width + x]

            buf[pos] = point[0] & 0xf8 | ((point[1] & 0xe0) >> 5)
            buf[pos + 1] = ((point[1] & 0x1c) << 3) | ((point[2] & 0xf8) >> 3)
            pos += 2

    return buf
