"""Display-related methods"""
# pylint: disable=broad-except,too-many-arguments

import logging

import requests

import local_config

def dot(x, y, r, g, b):
    logging.info("draw dot at (%d, %d) color (%d, %d, %d)", x, y, r, g, b)
    try:
        r = requests.post(
            f"{local_config.DISPLAY_URL}/dot?x={x}&y={y}&r={r}&g={g}&b={b}",
            timeout=local_config.DISPLAY_TIMEOUT)
        r.close()
        return True
    except Exception:
        logging.exception("error drawing dot")
        return False

def text(x, y, t, r, g, b):
    logging.info("draw text at (%d, %d) text %s color (%d, %d, %d)", x, y, text, r, g, b)
    try:
        r = requests.get(
            f"{local_config.DISPLAY_URL}/text?x={x}&y={y}&text={t}&r={r}&g={g}&b={b}",
            timeout=local_config.DISPLAY_TIMEOUT_LONG)
        r.close()
        return True
    except Exception:
        logging.exception("error drawing text")
        return False

def bitmap(x, y, w, h, data):
    logging.info("draw bitmap at (%d, %d) size (%d, %d)", x, y, w ,h)
    try:
        r = requests.post(
            f"{local_config.DISPLAY_URL}/bitmap?x={x}&y={y}&w={w}&h={h}",
            data=data, timeout=local_config.DISPLAY_TIMEOUT_LONG)
        if r.content != b'ok':
            logging.error("fail to set image: %r", r.content)
        r.close()
        return True
    except Exception:
        logging.exception("error drawing image")
        return False

def clear():
    logging.info("clearing display")
    requests.get(f"{local_config.DISPLAY_URL}/clear",
                 timeout=local_config.DISPLAY_TIMEOUT)
