import os
from . import compatible_import as compatible

Anki = compatible.Anki
aqt = Anki.aqt
if Anki.isQt6:
    from PyQt6.QtCore import pyqtSignal
    from PyQt6.QtGui import QKeySequence
    from PyQt6.QtWidgets import QShortcut
else:
    from PyQt5.QtCore import pyqtSignal
    from PyQt5.QtGui import QKeySequence
    from PyQt5.QtWidgets import QShortcut
from anki import hooks
from aqt import browser
from anki.notes import Note
from anki.utils import isWin
from aqt import gui_hooks, progress, mw, webview, reviewer,addcards
from aqt.browser.previewer import MultiCardPreviewer, BrowserPreviewer
from aqt.editor import Editor
from aqt.reviewer import Reviewer
from aqt.utils import showInfo, tooltip

from . import menu
from .G import signals
from . import funcs
from .handle_js import on_js_message
from ..bilink.in_text_admin.backlink_monitor import handle_editor_will_munge_html
from . import events
from .language import Translate
from .configsModel import AnswerInfoInterface


def run():
    # thisDist = funcs.G.installAs.local if funcs.G.src.ADDON_VERSION[-1]=="l" else funcs.G.installAs.ankiweb
    # # 当本发行版是本地版,而且存在网络版
    # conflict = funcs.G.addonId in mw.addonManager.ankiweb_addons() and mw.addonManager.isEnabled(str(funcs.G.addonId)) and thisDist==funcs.G.installAs.local
    # if conflict:
    #     if funcs.Config.get().distChoice.value == funcs.G.installAs.ankiweb:
    #         return
    #
    # # 当本发行版是网络版,而且存在本地版
    #


    if funcs.G.ISDEBUG:
        funcs.Utils.print("hjp-bilink is debug")
    gui_hooks.webview_will_show_context_menu.append(menu.maker(menu.T.webview))
    gui_hooks.browser_will_show_context_menu.append(menu.maker(menu.T.browser_context))
    gui_hooks.browser_menus_did_init.append(menu.maker(menu.T.browser))
    # gui_hooks.add_cards_did_init.append(events.on_add_cards_did_init_handle)
    gui_hooks.main_window_did_init.append(menu.maker(menu.T.mainwin))
    gui_hooks.editor_will_show_context_menu.append(menu.maker(menu.T.editor_context))

    gui_hooks.reviewer_did_show_question.append(events.on_reviewer_did_show_question)

    gui_hooks.card_will_show.append(events.on_card_will_show)
    gui_hooks.add_cards_did_add_note.append(events.on_add_cards_did_add_note_handle)
    signals.on_clipper_closed.connect(funcs.on_clipper_closed_handle)
    gui_hooks.webview_did_receive_js_message.append(on_js_message)
    gui_hooks.editor_will_munge_html.append(handle_editor_will_munge_html)
    gui_hooks.profile_will_close.append(events.on_profile_will_close_handle)
    gui_hooks.browser_sidebar_will_show_context_menu.append(events.on_browser_sidebar_will_show_context_menu_handle)

    # GroupReview
    # signals.on_card_answerd.connect(funcs.CardOperation.group_review)
    signals.on_card_answerd.connect(lambda answerinfo:funcs.GviewOperation.更新卡片到期时间(f"{answerinfo.card_id}"))
    gui_hooks.reviewer_did_answer_card.append(lambda x, y, z: signals.on_card_answerd.emit(
            AnswerInfoInterface(platform=x, card_id=y.id, option_num=z)
    ))
    # signals.on_card_changed.connect(funcs.GroupReview.modified_card_record)
    hooks.note_will_flush.append(lambda x: signals.on_card_changed.emit(x))  # 能检查到更改field,tag,deck,只要显示了都会检测到
    hooks.notes_will_be_deleted.append(
            lambda col, nids :funcs.CardOperation.删除不存在的结点([mw.col.get_note(nid).card_ids()[0].__str__() for nid in nids ])
    )
    # gui_hooks.collection_did_load.append(lambda x: funcs.GroupReview.begin())
    # signals.on_group_review_search_string_changed.connect(funcs.GroupReview.build)

    # MonkeyPatch
    browser.browser.PreviewDialog = funcs.MonkeyPatch.BrowserPreviewer
    browser.Browser.setupMenus = funcs.MonkeyPatch.BrowserSetupMenus(browser.Browser.setupMenus, setupShortCuts)
    # reviewer.Reviewer._showEaseButtons = funcs.MonkeyPatch.Reviewer_showEaseButtons(reviewer.Reviewer._showEaseButtons)
    # reviewer.Reviewer.nextCard = funcs.MonkeyPatch.Reviewer_nextCard(reviewer.Reviewer.nextCard)
    addcards.AddCards.closeEvent = funcs.MonkeyPatch.AddCards_closeEvent(addcards.AddCards.closeEvent)
    setupAnkiLinkProtocol()


def test(*args, **kwargs):
    showInfo("hi")
    # web_content:"webview.WebContent"=args[0]
    # context= args[1]
    # if type(context) == reviewer.ReviewerBottomBar:
    #     funcs.write_to_log_file(str(type(context)), need_timestamp=True)
    #     funcs.write_to_log_file(web_content.body)
    # n:"browser" = args[0]
    # tooltip("test")
    # funcs.write_to_log_file(n.card_ids()[0].__str__())
    # signals.testsignal.blockSignals(True)


def setupShortCuts(self: "browser.Browser"):
    """"""
    cfg = funcs.Config.get()
    copylink, link, unlink, insert, linkpool = cfg.shortcut_for_copylink.value, cfg.shortcut_for_link.value, \
                                               cfg.shortcut_for_unlink.value, cfg.shortcut_for_insert.value, \
                                               cfg.shortcut_for_openlinkpool.value
    typ = funcs.AnkiLinksCopy2.LinkType
    cmd = funcs.AnkiLinksCopy2.Open.Card
    funcs_dict = {
            typ.inAnki    : funcs.copy_intext_links,
            typ.htmlbutton: cmd.from_htmlbutton,
            typ.htmllink  : cmd.from_htmllink,
            typ.markdown  : cmd.from_markdown,
            typ.orgmode   : cmd.from_orgmode,
    }
    QShortcut(QKeySequence(copylink), self).activated.connect(
            lambda: funcs_dict[cfg.default_copylink_mode.value](funcs.BrowserOperation.get_selected_card()))
    QShortcut(QKeySequence(link), self).activated.connect(
            lambda: funcs.LinkPoolOperation.link(FROM=funcs.DataFROM.shortCut))
    QShortcut(QKeySequence(unlink), self).activated.connect(
            lambda: funcs.LinkPoolOperation.unlink(FROM=funcs.DataFROM.shortCut))
    QShortcut(QKeySequence(insert), self).activated.connect(
            lambda: funcs.LinkPoolOperation.insert(FROM=funcs.DataFROM.shortCut))
    QShortcut(QKeySequence(linkpool), self).activated.connect(
            lambda: funcs.Dialogs.open_linkpool()
    )


def setupAnkiLinkProtocol():
    if isWin:
        if not funcs.CustomProtocol.exists():
            funcs.CustomProtocol.set()
            tooltip(Translate.发现未注册自定义url协议_现已自动注册_若出现反复注册_请以管理员身份运行anki)
        mw.app.appMsg.disconnect(mw.onAppMsg)
        mw.onAppMsg = funcs.MonkeyPatch.onAppMsgWrapper(mw)
        mw.app.appMsg.connect(mw.onAppMsg)
