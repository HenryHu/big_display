"""Image processing utilities"""

from PIL import Image

def scale_size(w, h, tw, th):
    wr = w / tw
    hr = h / th
    return (tw, int(h / wr)) if wr > hr else (int(w / hr), th)

def img_to_565(img, outw, outh):
    data = img
    (w, h) = scale_size(img.width, img.height, outw, outh)
    img = img.resize((w, h))

    canvas = Image.new('RGB', (outw, outh))
    canvas.paste(img, ((outw - w) // 2, (outh - h) // 2))

    data = list(canvas.getdata())
    buf = bytearray(outw * outh * 2)
    pos = 0
    for y in range(outh):
        for x in range(outw):
            point = data[y * canvas.width + x]

            buf[pos] = point[0] & 0xf8 | ((point[1] & 0xe0) >> 5)
            buf[pos + 1] = ((point[1] & 0x1c) << 3) | ((point[2] & 0xf8) >> 3)
            pos += 2

    return buf
