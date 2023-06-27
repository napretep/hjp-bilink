# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'models.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2022/10/26 3:21'
"""
import abc
import datetime
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Dict, NewType

from .compatible_import import *
from . import funcs, baseClass, language, widgets,funcs2
from .all_models.basic_models import *
from .all_models.view_node_models import *
from .all_models.view_self_models import *
from .all_models.view_edge_models import *
from .all_models.view_batch_node_models import *
from .all_models.view_create_dialog_model import *
from .all_models.global_config_tableitem_model import *

