from . import utils
from aqt import mw
class MW:
    pass


if mw is None:
    mw = MW()
addonName = utils.BaseInfo().dialogName
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
