"""
G.py 就是GLOBAL.py, 存放一些持续不变的常量
"""

from .src_admin import SrcAdmin
from .tools.signals import CustomSignals

from aqt import mw


class MW: pass


if mw is None:
    mw = MW()

signals = CustomSignals.start()
src = SrcAdmin.start()
addonName = src.addon_name
mw.__dict__[addonName] = {}
mw.__dict__[addonName]["card_window"] = {}
mw.__dict__[addonName]["clipper"] = {}
mw.__dict__[addonName]["pdf_prev"] = {}  #
mw.__dict__[addonName]["anchor_window"] = {}
mw.__dict__[addonName]["input_window"] = {}
mw.__dict__[addonName]["VersionDialog"] = None
mw_addonName = mw.__dict__[addonName]
mw_current_card_id = None
mw_card_window = mw_addonName["card_window"]  # anchor第一个链接出来的窗口
mw_win_clipper = mw_addonName["clipper"]
mw_pdf_prev = mw_addonName["pdf_prev"]  # mw_pdf_prev[pdfname][pdfpagenum]
mw_anchor_window = mw_addonName["anchor_window"]  # anchor本身的窗口
mw_input_window = mw_addonName["input_window"]  # input窗口
mw_VersionDialog = mw_addonName["VersionDialog"]
browser_addon_menu = None
