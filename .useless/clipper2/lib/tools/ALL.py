from . import objs
import logging

import importlib
signals = objs.CustomSignals().start()
ISDEBUG = True
DEBUG_LEVEL = logging.DEBUG
# CONFIG = objs.CONFIG
connects = {}
pdfview = None
clipper = None
