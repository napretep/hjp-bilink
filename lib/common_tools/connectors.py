import aqt
from PyQt5.QtCore import pyqtSignal
from anki.notes import Note
from anki.utils import isWin
from aqt import gui_hooks, progress, mw
from aqt.editor import Editor
from aqt.utils import showInfo, tooltip
from . import menu
from .G import signals
from . import funcs, wrappers, compatible_import
from .handle_js import on_js_message
from ..bilink.in_text_admin.backlink_monitor import handle_editor_will_munge_html
from . import events
from anki.scheduler.v3 import Scheduler
from .language import Translate
from .interfaces import AnswerInfoInterface
from anki import hooks

def run():
    gui_hooks.webview_will_show_context_menu.append(menu.maker(menu.T.webview))
    gui_hooks.browser_will_show_context_menu.append(menu.maker(menu.T.browser_context))
    gui_hooks.browser_menus_did_init.append(menu.maker(menu.T.browser))
    # gui_hooks.browser_menus_did_init.append(menu.maker(menu.T.browser_searchbar_context))
    gui_hooks.add_cards_did_init.append(events.on_add_cards_did_init_handle)
    gui_hooks.main_window_did_init.append(menu.maker(menu.T.mainwin))
    # gui_hooks.main_window_did_init.append()
    gui_hooks.card_will_show.append(funcs.HTML_injecttoweb)
    signals.on_clipper_closed.connect(funcs.on_clipper_closed_handle)
    signals.on_card_answerd.connect(funcs.CardOperation.auto_review)
    gui_hooks.webview_did_receive_js_message.append(on_js_message)
    gui_hooks.editor_will_munge_html.append(handle_editor_will_munge_html)
    gui_hooks.profile_will_close.append(events.on_profile_will_close_handle)
    gui_hooks.add_cards_did_add_note.append(events.open_grahper_with_newcard)
    gui_hooks.browser_sidebar_will_show_context_menu.append(events.on_browser_sidebar_will_show_context_menu_handle)
    gui_hooks.reviewer_did_answer_card.append(lambda x, y, z: signals.on_card_answerd.emit(
        AnswerInfoInterface(platform=x, card_id=y.id, option_num=z)
    ))
    signals.on_card_changed.connect(funcs.AutoReview.modified_card_record)
    # gui_hooks.backend_did_block.append(lambda : signals.testsignal.emit())
    # gui_hooks.reviewer_did_answer_card.append(test)
    # #munge是在editor保存之前的数据,而他又只提供当前field的数据,所以读取不到note整体变化后的数据
    hooks.note_will_flush.append(lambda x : signals.on_card_changed.emit(x)) #能检查到更改field,tag,deck,只要显示了都会检测到
    # hooks.note_will_flush.append(test)
    # hooks.card_will_flush.append(test)
    # Note.flush = wrappers.func_wrapper(after=[lambda  : signals.testsignal.emit()])(Note.flush)
    setupAnkiLinkProtocol()
    gui_hooks.collection_did_load.append(lambda x:funcs.AutoReview.begin() )
    signals.on_auto_review_search_string_changed.connect(funcs.AutoReview.build)





def test(*args, **kwargs):
    n:"Note" = args[0]
    tooltip("backend_did_flush", period=1000)
    funcs.write_to_log_file(n.card_ids()[0].__str__())
    # signals.testsignal.blockSignals(True)



def setupAnkiLinkProtocol():
    if isWin:
        if not funcs.CustomProtocol.exists():
            funcs.CustomProtocol.set()
            tooltip(Translate.发现未注册自定义url协议_现已自动注册_若出现反复注册_请以管理员身份运行anki)
        mw.app.appMsg.disconnect(mw.onAppMsg)
        mw.onAppMsg = funcs.MonkeyPatch.onAppMsgWrapper(mw)
        mw.app.appMsg.connect(mw.onAppMsg)
