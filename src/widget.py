"""Widgets to be used with the display"""
# pylint: disable=too-few-public-methods,broad-except,too-many-arguments,too-many-instance-attributes

import time
import logging

from PIL import Image, ImageDraw, ImageFont

import align
import local_config
import imagelib
import display

WHITE_COLOR = (255, 255, 255)

def show_bitmap(x, y, img):
    return display.bitmap(x, y, img.width, img.height, imagelib.to_565(img))

class Widget:
    def __init__(self, x, y):
        self.children = []
        self.parent = None
        self.state = None
        self.background = None
        self.x = x
        self.y = y

    def add_child(self, child):
        self.children.append(child)
        child.set_parent(self)

    def set_parent(self, parent):
        self.parent = parent

    def render(self, canvas):
        pass

    def set_background(self, background):
        self.background = background

class DotWidget(Widget):
    def __init__(self, x, y):
        Widget.__init__(self, x, y)
        self.state = None

    def update(self, r=255, g=255, b=255):
        display.dot(self.x, self.y, r, g, b)
        self.state = (r, g, b)

    def repaint(self):
        if self.state is None:
            return
        if self.parent is None:
            display.dot(self.x, self.y, self.state[0], self.state[1], self.state[2])

class ImageWidget(Widget):
    def __init__(self, x, y, w=local_config.WIDTH, h=local_config.HEIGHT,
                 halign=align.HAlign.MIDDLE, valign=align.VAlign.MIDDLE
                 ):
        Widget.__init__(self, x, y)
        self.w = w
        self.h = h
        self.halign = halign
        self.valign = valign

    def paint(self, x, y, w, h):
        canvas = self.paint_full()
        if canvas is None:
            return None
        dx = x - self.x
        dy = y - self.y
        return canvas.crop((dx, dy, dx + w, dy + h))

    def update(self, img: Image):
        self.state = img.copy()
        self.repaint()
        return True

    def paint_full(self):
        if self.state is None:
            return None

        canvas = imagelib.create(self.w, self.h)

        if self.background is not None:
            background = self.background.paint(self.x, self.y, self.w, self.h)
            if background is not None:
                canvas = background

        scaled = imagelib.scale(self.state, self.w, self.h, self.halign, self.valign)
        canvas.alpha_composite(scaled)
        for child in self.children:
            child.render(canvas)

        return canvas

    def repaint(self):
        if self.parent is None:
            canvas = self.paint_full()
            if canvas is None:
                return
            while not show_bitmap(self.x, self.y, canvas):
                logging.warning("retrying bitmap draw")
                time.sleep(1)

class TransparentTextWidget(Widget):
    CHAR_HEIGHT = 8
    CHAR_WIDTH = 6
    CROP_HEAD = 2
    SHADOW_COLOR = (0, 0, 0)

    def __init__(self, x:int, y:int):
        Widget.__init__(self, x, y)
        self.text = ''
        self.color = WHITE_COLOR
        self.font = ImageFont.load(local_config.FONT_PATH)
        self.background = None
        self.w = 0
        self.h = self.CHAR_HEIGHT + 1

    def update(self, text:str, r:int=255, g:int=255, b:int=255):
        if text != self.text or (r, g, b) != self.color:
            self.text = text
            self.color = (r, g, b)
            self.repaint()

    def paint_full(self):
        self.w = len(self.text) * self.CHAR_WIDTH
        canvas_h = self.h + self.CROP_HEAD
        canvas = imagelib.create(self.w, canvas_h)

        if self.background is not None:
            background = self.background.paint(self.x, self.y, self.w, self.h)
            if background is not None:
                canvas.paste(background, (0, self.CROP_HEAD))

        draw = ImageDraw.Draw(canvas)
        draw.text((1, 1), self.text, fill=self.SHADOW_COLOR, font=self.font, align='left')
        draw.text((0, 1), self.text, fill=self.SHADOW_COLOR, font=self.font, align='left')
        draw.text((1, 0), self.text, fill=self.SHADOW_COLOR, font=self.font, align='left')
        draw.text((0, 0), self.text, fill=self.color, font=self.font, align='left')

        return canvas.crop((0, self.CROP_HEAD, self.w, canvas_h))

    def repaint(self):
        if self.parent is not None:
            return

        if self.text == '':
            return

        canvas = self.paint_full()
        if canvas is None:
            return

        while not show_bitmap(self.x, self.y, canvas):
            logging.warning("retrying bitmap draw for text")
            time.sleep(1)

    def char_width(self):
        return self.CHAR_WIDTH

    def char_height(self):
        return self.CHAR_HEIGHT

class TextWidget(Widget):
    def __init__(self, x: int, y: int):
        Widget.__init__(self, x, y)
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

    def char_width(self):
        return 6

    def char_height(self):
        return 7

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
        Widget.__init__(self, x, y)
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
    def __init__(self, x, y, picker, text_class):
        self.picker = picker
        self.x = x
        self.y = y

        self.first_part = text_class(x, y)
        char_width = self.first_part.char_width()
        char_height = self.first_part.char_height()

        self.dot_widget = DotWidget(x + 2 * char_width, y + char_height - 1)
        self.second_part = text_class(x + 2 * char_width + 2, y)

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

    def set_background(self, background):
        self.first_part.set_background(background)
        self.second_part.set_background(background)
