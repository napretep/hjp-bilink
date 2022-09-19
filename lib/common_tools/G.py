# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'G.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2021/7/30 9:47'
G.py 就是GLOBAL.py, 存放一些持续不变的常量
"""
from typing import Optional



from . import signals, src_admin, objs, widgets, language
# from .src_admin import SrcAdmin
# from .signals import CustomSignals
# from .objs import DB_admin

from typing import TYPE_CHECKING
from .compatible_import import *
import os

class installAs:
    local=0
    ankiweb=1

if TYPE_CHECKING:
    from .configsModel import GroupReviewDictInterface, ConfigModel


class MW: pass


isQt6 = Anki.isQt6

if mw is None:
    mw = MW()



QTMAXINT = 2147483647
QTMININT = -2147483647

addonId= 1420819673
say = language.rosetta
ISDEBUG = ISDEBUG
DB = objs.DB_admin()  # 这个是通用DB,如果要用linkdata请用linkdata_admin里的DB
signals = signals.CustomSignals.start()
src = src_admin.src
addonName = src.dialog_name
CONFIG: "ConfigModel" = None
mw.__dict__[addonName] = {}
mw.__dict__[addonName]["progresser"] = None
mw.__dict__[addonName]["card_window"] = {}
mw.__dict__[addonName]["clipper"] = {}
mw.__dict__[addonName]["pdf_prev"] = {}  #
mw.__dict__[addonName]["anchor_window"] = {}
mw.__dict__[addonName]["input_window"] = None
mw.__dict__[addonName]["VersionDialog"] = None
mw.__dict__[addonName]["grapher"] = None
mw_addonName = mw.__dict__[addonName]
mw_current_card_id = None
mw_card_window: "dict" = mw_addonName["card_window"]  # anchor第一个链接出来的窗口
mw_win_clipper = None
mw_pdf_prev = mw_addonName["pdf_prev"]  # mw_pdf_prev[pdfname][pdfpagenum]
mw_anchor_window = mw_addonName["anchor_window"]  # anchor本身的窗口
mw_linkpool_window = mw_addonName["input_window"]  # input窗口
mw_VersionDialog = mw_addonName["VersionDialog"]
mw_progresser = mw.__dict__[addonName]["progresser"]
mw_universal_worker = None
mw_grapher = mw.__dict__[addonName]["grapher"] # grapher是临时视图, 也叫链接池视图
mw_gview = {}
GViewAdmin_window = None
GViewAutoShow_window = None
mw_addcard_to_grapher_on = False
browser_addon_menu = None
GroupReview_dict: "Optional[GroupReviewDictInterface]" = None  # 卡片ID映射到searchString
GroupReview_tempfile: "set" = set()  # 只保存卡片id
GroupReview_timer = QTimer()
GroupReview_version: "float" = 0
nextCard_interval: "list[int]" = []  # 用来记录连续过快复习
cardChangedTime = -1


