"""
专门用来加按钮的文件
"""
from aqt import gui_hooks
from aqt.editor import EditorWebView
from aqt.webview import AnkiWebView

from .language import rosetta as say
from .mainfunctions import *
from .utils import *


def func_menuAddBrowserInsert(menu: QMenu, browser: Browser, need: tuple = ("none",)):
    """browser插入类函数集合"""
    prefix = "" if "prefix" not in need else consolerName
    menuNameLi = list(map(lambda x: prefix + say(x), ["清除后选中卡片插入", "将选中卡片插入", "将选中卡片编组插入"]))
    needli = ["", "group", "clear"]
    if "prefix" in need:
        # console("prefixneed")
        linkmenu = menu
    else:
        # console("prefixdontneed")
        linkmenu = menu.addMenu(say("插入"))
    list(map(lambda x, y: linkmenu.addAction(x).triggered.connect(lambda: func_browserInsert(browser, need=(y,))),
             menuNameLi, needli))
    pass


def func_menuAddLink(menu: QMenu, need: tuple = ("none",)):
    """用来给连接类型的函数加按钮"""
    menuNameLi = list(map(lambda x: say(x), ["默认连接", "完全图连接", "组到组连接", "按结点取消连接", "按路径取消连接"]))
    prefix = "" if "prefix" not in need else consolerName
    linkmenu = menu.addMenu(prefix + say("连接"))
    modeLi = [999, 0, 1, 2, 3]
    list(map(
        lambda x, y: linkmenu.addAction(x).triggered.connect(lambda: func_linkStarter(mode=y)), menuNameLi, modeLi))
    if "selected" in need:
        linkmenu2 = menu.addMenu(prefix + say("选中连接"))
        list(map(
            lambda x, y: linkmenu2.addAction(x).triggered.connect(
                lambda: func_linkStarter(mode=y, need=need)), menuNameLi, modeLi))


def func_menuAddClearOpen(menu: QMenu, need: tuple = ("none",)):
    """用来给清除和打开input功能加按钮"""
    prefix = "" if "prefix" not in need else consolerName
    menuli = ["清空input", "打开input"]
    funcli = [func_clearInput, func_openInput]
    list(map(lambda x, y: menu.addAction(f"{prefix}{say(x)}").triggered.connect(y), menuli, funcli))


def func_menuAddBaseMenu(menu: QMenu):
    """基础的如,help,config,version"""
    menuli = ["调整config", "查看版本", "打开插件页面"]
    funcli = [func_config, func_version, func_help]
    list(map(lambda x, y: menu.addAction(f"{say(x)}").triggered.connect(y), menuli, funcli))


def func_menuAddSingleInsert(menu: QMenu, card_id=0, selected="", need: tuple = ("none",)):
    """用来添加常规插入按钮组"""
    menuli = list(map(lambda x: say(x), ["先清除再插入", "直接插入", "插入上一个组", "选中文字更新标签"]))
    needli = ["clear", "", "last", "tag"]
    prefix = "" if "prefix" not in need else consolerName
    papamenu = menu.addMenu(prefix + say("插入"))
    list(map(
        lambda x, y: papamenu.addAction(x).triggered.connect(
            lambda: func_singleInsert(card_id=card_id, desc=selected, need=(y,))), menuli, needli))


def func_menuAddHelper(
        menu: QMenu,
        parent: Union[Browser, QObject, EditorWebView] = None,
        need: tuple = ("none",),
        card_id: int = 0,
        selected: str = ""):
    """提供大部分类似的按钮添加操作帮助"""
    if "link" in need: func_menuAddLink(menu, need=need)
    if "browserinsert" in need: func_menuAddBrowserInsert(menu, parent, need=need)
    if "clear/open" in need: func_menuAddClearOpen(menu, need=need)
    if "basicMenu" in need: func_menuAddBaseMenu(menu)
    if "insert" in need: func_menuAddSingleInsert(menu, card_id=card_id, selected=selected, need=need)
    pass


def func_add_browsermenu(browser: Browser):
    """给browser的bar添加按钮"""
    if hasattr(browser, "hjp_link"):
        menu: QMenu = browser.hjp_Link
    else:
        menu = browser.hjp_Link = QMenu("hjp_link")
        browser.menuBar().addMenu(browser.hjp_Link)
    '''
    连接:5个,插入:3个,打开,清空,配置,版本,帮助
    '''
    func_menuAddHelper(menu, browser, need=("link", "browserinsert", "clear/open", "basicMenu",))


def fun_add_browsercontextmenu(browser: Browser, menu: QMenu):
    """用来给browser加上下文菜单"""
    func_menuAddHelper(menu, browser, need=("browserinsert", "prefix",))


def func_add_editorcontextmenu(view: AnkiWebView, menu: QMenu):
    """用来给editor界面加上下文菜单"""
    editor = view.editor
    selected = editor.web.selectedText()
    try:
        card_id = editor.card.id
    except:
        console(say("由于这里无法读取card_id, 连接菜单不在这显示"))
        return
    func_menuAddHelper(menu, view, need=("insert", "clear/open", "prefix",), card_id=card_id, selected=selected)


def func_add_webviewcontextmenu(view: AnkiWebView, menu: QMenu):
    """正如其名,给webview加右键菜单"""
    selected = view.page().selectedText()
    cid = 0
    if view.title == "main webview" and mw.state == "review":
        cid = mw.reviewer.card.id
    elif view.title == "previewer":
        cid = view.parent().card().id
    if cid != 0:
        func_menuAddHelper(menu, view, need=("link", "insert", "clear/open", "prefix",), selected=selected, card_id=cid)


gui_hooks.browser_menus_did_init.append(func_add_browsermenu)
gui_hooks.browser_will_show_context_menu.append(fun_add_browsercontextmenu)
gui_hooks.profile_will_close.append(func_clearInput)
gui_hooks.editor_will_show_context_menu.append(func_add_editorcontextmenu)
gui_hooks.webview_will_show_context_menu.append(func_add_webviewcontextmenu)
