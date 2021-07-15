from . import utils
from aqt import mw

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
mw_card_window = mw_addonName["card_window"]
mw_win_clipper = mw_addonName["clipper"]
mw_pdf_prev = mw_addonName["pdf_prev"]  # mw_pdf_prev[pdfname][pdfpagenum]
mw_anchor_window = mw_addonName["anchor_window"]
mw_input_window = mw_addonName["input_window"]
mw_VersionDialog = mw_addonName["VersionDialog"]
