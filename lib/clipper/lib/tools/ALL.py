from . import objs
import logging

import importlib

signals = objs.signals
ISDEBUG = False
DEBUG_LEVEL = logging.DEBUG
CONFIG = objs.CONFIG
connects = {}
pdfview = None
clipper = None
