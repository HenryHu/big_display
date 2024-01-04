"""Widgets to be used with the display"""
# pylint: disable=too-few-public-methods,broad-except,too-many-arguments

import time
import logging

from PIL import Image, ImageDraw, ImageFont

import align
import local_config
import imagelib
import display

WHITE_COLOR = (255, 255, 255)

class Widget:
    parent = None
    children = []
    state = None

    def add_child(self, child):
        self.children.append(child)
        child.set_parent(self)

    def set_parent(self, parent):
        self.parent = parent

    def render(self, canvas):
        pass

class DotWidget(Widget):
    x = 0
    y = 0
    state = None

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.state = None

    def update(self, r=255, g=255, b=255):
        display.dot(self.x, self.y, r, g, b)
        self.state = (r, g, b)

    def repaint(self):
        if self.state is None:
            return
        display.dot(self.x, self.y, self.state[0], self.state[1], self.state[2])

class ImageWidget(Widget):
    x = 0
    y = 0
    w = 0
    h = 0
    halign = align.HAlign.MIDDLE
    valign = align.VAlign.MIDDLE

    def __init__(self, x, y, w=local_config.WIDTH, h=local_config.HEIGHT,
                 halign=align.HAlign.MIDDLE, valign=align.VAlign.MIDDLE
                 ):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.halign = halign
        self.valign = valign

    def update(self, img: Image):
        scaled = imagelib.scale(img, self.w, self.h, self.halign, self.valign)
        self.state = scaled
        for child in self.children:
            child.render(scaled)

        if self.parent is None:
            while not display.bitmap(self.x, self.y, self.w, self.h, imagelib.to_565(scaled)):
                logging.warning("retrying bitmap draw")
                time.sleep(0.1)

    def repaint(self):
        if self.state is None:
            return
        if self.parent is None:
            display.bitmap(self.x, self.y, self.w, self.h, imagelib.to_565(self.state))

class TextWidget(Widget):
    x = 0
    y = 0
    text = ''
    font = None

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.text = ''
        self.font = ImageFont.load(local_config.FONT_PATH)
        self.state = None

    def update(self, text: str, r: int=255, g: int=255, b: int=255, force: bool=False):
        if text != self.text or force:
            if self.text and len(text) != len(self.text):
                display.text(self.x, self.y, ' ' * len(self.text), 0, 0, 0)

            self.state = (text, r, g, b)
            if self.parent is None:
                if display.text(self.x, self.y, text, r, g, b):
                    self.text = text

    def render(self, canvas):
        if self.state is None:
            return
        (text, r, g, b) = self.state

        draw = ImageDraw.Draw(canvas)
        draw.text((self.x, self.y), text, fill=(r, g, b), font=self.font, align='left')
        self.text = self.state[0]

    def repaint(self):
        if self.state is None:
            return
        if self.parent is None:
            (text, r, g, b) = self.state
            display.text(self.x, self.y, text, r, g, b)

class ColorPicker:
    def pick(self, _value):
        return WHITE_COLOR

class RangedColorPicker(ColorPicker):
    color_map = None
    def __init__(self, color_map):
        self.color_map = color_map

    def pick(self, value):
        for entry in sorted(self.color_map):
            if value < entry:
                return self.color_map[entry]
        return None

class ColoredTextWidget(Widget):
    text_widget = None
    picker = None
    def __init__(self, x: int, y: int, picker: ColorPicker):
        self.text_widget = TextWidget(x, y)
        self.picker = picker

    def update(self, text: str, value: float, force: bool=False):
        color = self.picker.pick(value)
        if color is not None:
            self.text_widget.update(text, *color, force=force)
        else:
            self.text_widget.update(text, force=force)

    def set_parent(self, parent):
        self.text_widget.set_parent(parent)

    def render(self, canvas):
        self.text_widget.render(canvas)

    def repaint(self):
        self.text_widget.repaint()

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

    def repaint(self):
        self.first_part.repaint()
        self.dot_widget.repaint()
        self.second_part.repaint()
