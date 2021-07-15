from aqt.previewer import Previewer, BrowserPreviewer

from . import signals
from . import clipper_imports
from . import funcs, handles, wrappers
from aqt import mw, gui_hooks
from ..dialogs.DialogCardPrev import SingleCardPreviewerMod


class Connector(object):
    event_dict = {
        signals.all.on_data_refresh_webview: funcs.webview_refresh,
        signals.all.on_data_refresh_browser: funcs.browser_refresh,
        signals.all.on_data_refresh_all: funcs.browser_and_webview_refresh,
        signals.all.on_currentEdit_will_show: handles.on_currentEdit_will_show_handle,
    }

    def __init__(self):
        clipper_imports.funcs.event_handle_connect(self.event_dict)


connector = Connector()

# mw.onEditCurrent=wrappers.signal_wrapper(signal=signals.ALL.on_currentEdit_will_show)(mw.onEditCurrent)

# reviewer,browserPreviewer,customPreviewer,全部加上关闭PDFprev的功能.
mw.onEditCurrent = wrappers.func_wrapper(before=[[handles.on_currentEdit_will_show_handle, None]])(mw.onEditCurrent)
Previewer.closeEvent = wrappers.Previewer_close_wrapper(Previewer.closeEvent)
BrowserPreviewer._on_prev_card = wrappers.BrowserPreviewer_card_change_wrapper(BrowserPreviewer._on_prev_card)
BrowserPreviewer._on_next_card = wrappers.BrowserPreviewer_card_change_wrapper(BrowserPreviewer._on_next_card)
gui_hooks.state_did_change.append(handles.on_state_did_change_handle)
