#
# """初试入口"""
# from anki import notes
# from anki.notes import Note
# from aqt import gui_hooks
# from aqt.editor import EditorWebView, Editor
# from .lib.obj.editor_monitor import handle_editor_did_load_note, handle_editor_will_munge_html
#
# from .lib.obj.HTMLbutton_render import HTMLbutton_make
# from .lib.obj.handle_js import on_js_message
# from .lib.obj.MenuAdder import *
# from .lib.obj.utils import userInfoDir
# from .lib.dialogs.DialogAnchor import AnchorDialog
# from .lib.dialogs.DialogCardPrev import SingleCardPreviewerMod, EditNoteWindowFromThisLinkAddon
# from aqt.editcurrent import EditCurrent
# from .lib.obj import clipper_imports
# from .lib.obj import ModuleProxy
# from .lib.obj.connectors import Connector
# from .lib.obj import handles, wrappers, signals
# from .lib.obj.SrcAdmin import SrcAdmin
#
# from .lib.bilink.tools import funcs
# from .lib.bilink import dialogs
#
# if funcs.config_check_update():
#     p = dialogs.VersionDialog()
#     p.exec()
#
#
# def data_selectedFromBrowserTable(browser, *args, **kwargs):
#     """从?"""
#     cardLi: List[str] = list(map(lambda x: str(x), browser.selectedCards()))
#     inputObj = Input()
#     if len(cardLi) > 0:
#         inputObj.data = inputObj.pairLi_extract(cardLi)
#         console("inputObj.data:" + inputObj.data.__str__()).log.end()
#         param = Params(input=inputObj, parent=browser, features=["selected", "browserShortCut"])
#         return param
#     else:
#         return None
#
#
# def shortcut_inputDialog_open(*args, **kwargs):
#     """打开input对话框"""
#     tooltip(say("input开启"))
#     func_openInput()
#
#
# def shortcut_inputFile_clear(*args, **kwargs):
#     """清空input"""
#     func_clearInput()
#
#
# def shortcut_browserTableSelected_link(browser: Browser, *args, **kwargs):
#     """根据默认链接参数对选中的卡片进行链接, 如果是按组到组链接, 则强制每一个卡片为一组"""
#     param = data_selectedFromBrowserTable(browser)
#     if param is not None:
#         LinkStarter(mode=int(param.input.baseinfo.config_obj.defaultLinkMode), **param.__dict__)
#     else:
#         console(say("未选择卡片")).talk.end()
#
#
# def shortcut_browserTableSelected_unlink(browser: Browser, *args, **kwargs):
#     """根据默认链接参数对选中的卡片进行反链接"""
#     param = data_selectedFromBrowserTable(browser)
#     if param is not None:
#         LinkStarter(mode=int(param.input.baseinfo.config_obj.defaultUnlinkMode), **param.__dict__)
#     else:
#         console(say("未选择卡片")).talk.end()
#
#
# def shortcut_browserTableSelected_insert(browser: Browser, *args, **kwargs):
#     """根据默认插入参数对选中的卡片进行插入"""
#     param = data_selectedFromBrowserTable(browser)
#     insertMode = {4: "", 5: "clear", 6: "group"}
#     if param is not None:
#         param.features += [insertMode[int(param.input.baseinfo.config_obj.defaultInsertMode)], "noTag"]
#         LinkStarter(mode=4, **param.__dict__)
#     else:
#         console(say("未选择卡片")).talk.end()
#
# def shortcut_CopyLink(p, *args, **kwargs):
#     """根据默认插入参数对选中的卡片进行插入"""
#     func_Copylink(parent=p)
#
# def wrapper_shortcut(func):
#     def shortcutconnect(k, v, self_, *args, **kwargs):
#         if v[0] != "":
#             self_.__dict__["hjp_bilink_action" + k] = \
#                 QShortcut(QKeySequence(v[0]), self_, activated=lambda: v[1](self_, *args, **kwargs))
#         else:
#             return None
#
#     @functools.wraps(func)
#     def shortCut_add(self, *args, **kwargs):
#         self_ = sys._getframe(0).f_locals["self"].__str__()
#         result = func(self, *args, **kwargs)
#         for place in placeDict:
#             if place == "all":
#                 list(map(lambda k: shortcutconnect(k, placeDict[place][k], self, *args, **kwargs), placeDict[place]))
#             elif isinstance(self,place):
#                 list(map(lambda k: shortcutconnect(k, placeDict[place][k], self, *args, **kwargs), placeDict[place]))
#         return result
#
#     return shortCut_add
#
#
# def shortcut_addto_originalcode(*arg, **kwargs):
#     """用来绑定快捷键,有些快捷键还是失效的,需要再改进 """
#     Browser.__init__ = wrapper_shortcut(Browser.__init__)
#     AnchorDialog.__init__= wrapper_shortcut(AnchorDialog.__init__)
#     SingleCardPreviewerMod.__init__ = wrapper_shortcut(SingleCardPreviewerMod.__init__)
#     EditCurrent.__init__ = wrapper_shortcut(EditCurrent.__init__)
#     EditNoteWindowFromThisLinkAddon.__init__ = wrapper_shortcut(EditNoteWindowFromThisLinkAddon.__init__)
#     Previewer.__init__ = wrapper_shortcut(Previewer.__init__)
#
#
# def HTML_injecttoweb(htmltext, card, kind):
#     """在web渲染前,注入html代码,"""
#     if kind in [
#         "previewQuestion",
#         "previewAnswer",
#         "reviewQuestion",
#         "reviewAnswer"
#     ]:
#         html_string = HTMLbutton_make(htmltext, card)
#         console(html_string).log.end()
#         return html_string
#     else:
#         return htmltext
#
#
# def func_add_browsermenu(browser: Browser = None):
#     """给browser的bar添加按钮"""
#     if hasattr(browser, "hjp_bilink"):
#         menu: QMenu = browser.hjp_bilink
#     else:
#         menu = browser.hjp_bilink = QMenu("hjp_bilink")
#         browser.menuBar().addMenu(browser.hjp_bilink)
#     '''
#     链接:5个,插入:3个,打开,清空,配置,版本,帮助
#     '''
#     func_menuAddHelper(menu=menu, parent=browser,
#                        actionTypes=["link", "browserinsert", "clear_open_input", "open_clipper", "basicMenu",
#                                     "openStorageDir"])
#
#
# def fun_add_browsercontextmenu(browser: Browser, menu: QMenu):
#     """用来给browser加上下文菜单"""
#     func_menuAddHelper(menu=menu, parent=browser, features=["prefix"], actionTypes=["browserinsert"])
#     func_menuAddHelper(menu=menu, parent=browser, features=["prefix"], actionTypes=["browsercopylink"])
#     func_menuAddHelper(menu=menu, parent=browser, features=["prefix"], actionTypes=["browser_clipper_open"])
#
#
# def func_add_editorcontextmenu(view: AnkiWebView, menu: QMenu):
#     """用来给editor界面加上下文菜单"""
#
#     editor:Editor = view.editor
#     selected = editor.web.selectedText()
#     try:
#         card_id = editor.note.card_ids()[0]
#     except:
#         console(say("由于这里无法读取card_id, 链接菜单不在这显示")).talk.end()
#         return
#
#     func_menuAddHelper(menu=menu, parent=view, pair=Pair(card_id=str(card_id), desc=selected),
#                        features=["prefix"], actionTypes=["insert", "clear_open_input", ])
#
#
# def func_add_webviewcontextmenu(view: AnkiWebView, menu: QMenu):
#     """正如其名,给webview加右键菜单"""
#     selected = view.page().selectedText()
#     cid = "0"
#     if view.title == "main webview" and mw.state == "review":
#         cid = mw.reviewer.card.id
#     elif view.title == "previewer" and view.parent() is not None and view.parent().card() is not None:
#         cid = view.parent().card().id
#     if cid != "0":
#         func_menuAddHelper(pair=Pair(desc=selected, card_id=str(cid)), features=["prefix"],
#                            parent=view, menu=menu, actionTypes=["webviewcopylink", "link", "insert", "alter_deck",
#                                                                 "alter_tag", "clear_open_input", "anchor",
#                                                                 "webview_clipper_open"])
#
# # def editor_shortcuts(cuts,editor):
# #     if not editor.addMode:
# #         return
# #     cuts.extend(list(globalShortcutDict.values()))
#
# # def mw_shortcuts(state, shortcuts):
# #     if state == "review":
# #         shortcuts.extend(list(globalShortcutDict.values()))
#
# def test_func(note, ):
#     # for i in args:
#     #     showInfo(i.__str__())
#     # for k,v in kwargs.items():
#     #     showInfo(f"{k}:{v}")
#     showInfo(f"""args={note.__str__()}""")
#
#
#
#
#
# config = BaseInfo().config_obj
# cfg = Config()
#
# # globalShortcutDict = {
# #     "InputDialog_open": (cfg.user_cfg["shortcut_inputDialog_open"], shortcut_inputDialog_open),
# #     "inputFile_clear": (cfg.user_cfg["shortcut_inputFile_clear"], shortcut_inputFile_clear)
# #
# # }
#
# # browserShortcutDict = {
# #     "Link": (cfg.user_cfg["shortcut_browserTableSelected_link"], shortcut_browserTableSelected_link,),
# #     "Unlink": (cfg.user_cfg["shortcut_browserTableSelected_unlink"], shortcut_browserTableSelected_unlink),
# #     "Insert": (cfg.user_cfg["shortcut_browserTableSelected_insert"], shortcut_browserTableSelected_insert),
# #     "copylink": (cfg.user_cfg["shortcut_copylink"], shortcut_CopyLink)
# # }
# # placeDict = {"all": globalShortcutDict, Browser: browserShortcutDict}
#
# gui_hooks.reviewer_did_answer_card.append(handles.on_reviewer_did_answer_card_handle)
# # gui_hooks.state_shortcuts_will_change.append(mw_shortcuts)
# # gui_hooks.editor_did_init_shortcuts.append(editor_shortcuts)
# gui_hooks.editor_did_load_note.append(handle_editor_did_load_note)
# gui_hooks.editor_will_munge_html.append(handle_editor_will_munge_html)  # 实时监测
# # gui_hooks.editor_did_unfocus_field.append(handle_editor_did_unfocus_field)
# gui_hooks.editor_will_show_context_menu.append(func_add_editorcontextmenu)
# # gui_hooks.editor_did_fire_typing_timer(test_func)
# gui_hooks.profile_did_open.append(shortcut_addto_originalcode)
# gui_hooks.profile_will_close.append(func_onProgramClose)
# gui_hooks.card_will_show.append(HTML_injecttoweb)
# gui_hooks.browser_menus_did_init.append(func_add_browsermenu)
# # gui_hooks.main_window_did_init.append(func_add_mainwindowmenu)
# gui_hooks.browser_will_show_context_menu.append(fun_add_browsercontextmenu)
# gui_hooks.webview_will_show_context_menu.append(func_add_webviewcontextmenu)
# gui_hooks.webview_did_receive_js_message.append(on_js_message)
#
# # from .lib.clipper.lib.Clipper import Clipper,Clipper2
# # from .lib.obj.tools import events, objs, funcs, ALL
#
#
# print, print_ = clipper_imports.funcs.logger(__name__)
# clipper_imports.ALL.signals.on_cardlist_addCard.connect(ModuleProxy.on_cardlist_addCard_handle)
# clipper_imports.ALL.signals.on_anki_card_create.connect(ModuleProxy.on_anki_card_create_handle)
# clipper_imports.ALL.signals.on_anki_field_insert.connect(ModuleProxy.on_anki_field_insert_handle)
# clipper_imports.ALL.signals.on_anki_browser_activate.connect(ModuleProxy.on_anki_browser_activate_handle)
# clipper_imports.ALL.signals.on_anki_file_create.connect(ModuleProxy.on_anki_file_create_handle)
# clipper_imports.ALL.signals.on_config_ankidata_load.connect(ModuleProxy.on_config_ankidata_load_handle)
# # clipper_imports.ALL.signals.on_clipper_closed.connect(funcs.on_clipper_closed)
# # print("ALL.signals.on_config_ankidata_load.connect(ModuleProxy.on_config_ankidata_load_handle)")
# # clipper = Clipper2(mw)
# # print("clipper = Clipper()")
# # pageitem = PageItem5(PageInfo("./resource/徐森林_数学分析_第8章.pdf", 0), rightsidebar=clipper.rightsidebar)
# # event = events.PageItemAddToSceneEvent(pageItem=pageitem, eventType=events.PageItemAddToSceneEvent.addPageType)
# # objs.CustomSignals.start().on_pageItem_addToScene.emit(event)
#
#
# # mw.col.add_note(note=notes.Note(mw.col,model=mw.col.models))
#
