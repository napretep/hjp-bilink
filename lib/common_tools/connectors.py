from anki.notes import Note
from aqt import gui_hooks, progress, mw
from aqt.editor import Editor
from aqt.utils import showInfo, tooltip
from . import menu
from .G import signals
from . import funcs,wrappers,compatible_import
from .handle_js import on_js_message
from ..bilink.in_text_admin.backlink_monitor import handle_editor_will_munge_html
from anki.scheduler.v3  import Scheduler

def run():
    gui_hooks.webview_will_show_context_menu.append(menu.maker(menu.T.webview))
    gui_hooks.browser_will_show_context_menu.append(menu.maker(menu.T.browser_context))
    gui_hooks.browser_menus_did_init.append(menu.maker(menu.T.browser))

    gui_hooks.main_window_did_init.append(menu.maker(menu.T.mainwin))
    gui_hooks.card_will_show.append(funcs.HTML_injecttoweb)
    signals.on_clipper_closed.connect(funcs.on_clipper_closed_handle)
    gui_hooks.webview_did_receive_js_message.append(on_js_message)
    gui_hooks.editor_will_munge_html.append(handle_editor_will_munge_html)
    gui_hooks.profile_will_close.append(funcs.LinkPoolOperation.clear)
    # #munge是在editor保存之前的数据,而他又只提供当前field的数据,所以读取不到note整体变化后的数据
    # gui_hooks.editor_did_fire_typing_timer.append(on_editor_did_fire_typing_timer_handle)
    # mw.reviewer.show = wrappers.func_wrapper(after=[test])(mw.reviewer.show)


def test(*args, **kwargs):
    from . import funcs
    funcs.write_to_log_file(mw.reviewer.cardQueue.__str__())


