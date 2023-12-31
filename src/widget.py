"""Widgets to be used with the display"""
# pylint: disable=too-few-public-methods,broad-except,too-many-arguments

import logging

import requests
import local_config
import imagelib

WHITE_COLOR = (255, 255, 255)

class DotWidget:
    x = 0
    y = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def update(self, r=255, g=255, b=255):
        try:
            r = requests.post(
                f"{local_config.DISPLAY_URL}/dot?x={self.x}&y={self.y}&r={r}&g={g}&b={b}",
                timeout=local_config.DISPLAY_TIMEOUT)
            r.close()
        except Exception:
            logging.exception("error drawing dot")

class ImageWidget:
    x = 0
    y = 0
    w = 0
    h = 0
    filename = None

    def __init__(self, x, y, w=local_config.WIDTH, h=local_config.HEIGHT):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def image(self, data):
        try:
            r = requests.post(
                f"{local_config.DISPLAY_URL}/bitmap?x={self.x}&y={self.y}&w={self.w}&h={self.h}",
                data=data, timeout=local_config.DISPLAY_TIMEOUT)
            if r.content != b'ok':
                logging.error("fail to set image: %r", r.content)
            r.close()
        except Exception:
            logging.exception("error drawing image")

    def update(self, img):
        data = imagelib.img_to_565(img, self.w, self.h)
        self.image(data)

class TextWidget:
    x = 0
    y = 0
    text = ''

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def text_out(self, x, y, text, r=255, g=255, b=255):
        try:
            r = requests.get(
                f"{local_config.DISPLAY_URL}/text?x={x}&y={y}&text={text}&r={r}&g={g}&b={b}",
                timeout=1)
            r.close()
        except Exception:
            logging.exception("error drawing text")

    def update(self, text, r=255, g=255, b=255):
        if text != self.text:
            if self.text and len(text) != len(self.text):
                self.text_out(self.x, self.y, ' ' * len(self.text))
            self.text_out(self.x, self.y, text, r, g, b)
            self.text = text

class ColorPicker:
    def pick(self, _value):
        return WHITE_COLOR

    def current_color(self):
        return WHITE_COLOR

class RangedColorPicker(ColorPicker):
    color_map = None
    current_color = None
    def __init__(self, color_map):
        self.color_map = color_map
        self.current_color = (255, 255, 255)

    def pick(self, value):
        for entry in sorted(self.color_map):
            if value < entry:
                color = self.color_map[entry]
                self.current_color = color
                return color
        return None

class ColoredTextWidget:
    text_widget = None
    picker = None
    def __init__(self, x, y, picker):
        self.text_widget = TextWidget(x, y)
        self.picker = picker

    def update(self, text, value):
        color = self.picker.pick(value)
        if color is not None:
            self.text_widget.update(text, *color)
        else:
            self.text_widget.update(text)

class TextWithDotWidget:
    first_part = None
    second_part = None
    dot_widget = None
    picker = None
    x = 0
    y = 0
    def __init__(self, x, y, picker):
        self.picker = picker
        self.x = x
        self.y = y

        self.first_part = TextWidget(x, y)
        self.dot_widget = DotWidget(x + 12, y + 6)
        self.second_part = TextWidget(x + 14, y)

    def update(self, text, value):
        color = self.picker.pick(value)
        if color is None:
            color = WHITE_COLOR

        if '.' in text:
            (first, second) = text.split('.', 1)
            self.first_part.update(first, *color)
            self.dot_widget.update(*color)
            self.second_part.update(second, *color)
        else:
            self.second_part.update('')
            self.first_part.update(text, *color)
