"""
专门用来加按钮的文件
"""
from aqt import gui_hooks
from aqt.webview import AnkiWebView

from .mainfunctions import *
from .utils import *


def func_menuAddBrowserInsert(param: Params = None):
    """browser插入类函数集合"""
    prefix = "" if "prefix" not in param.need else consolerName
    menuNameLi = list(map(lambda x: prefix + say(x), ["清除后选中卡片插入", "将选中卡片插入", "将选中卡片编组插入"]))
    needli = ["clear", "", "group"]
    if "prefix" in param.need:
        linkmenu = param.menu
    else:
        linkmenu = param.menu.addMenu(say("插入"))
    browser = param.parent
    list(map(lambda x, y: linkmenu.addAction(x).triggered.connect(lambda: func_browserInsert(browser, need=(y,))),
             menuNameLi, needli))
    pass


def func_menuAddLink(param: Params = None):
    """用来给连接类型的函数加按钮"""
    menuNameLi = list(map(lambda x: say(x), ["默认连接", "完全图连接", "组到组连接", "按结点取消连接", "按路径取消连接"]))
    prefix = "" if "prefix" not in param.need else consolerName
    linkmenu = param.menu.addMenu(prefix + say("连接"))
    modeLi = [999, 0, 1, 2, 3]
    list(map(
        lambda x, y: linkmenu.addAction(x).triggered.connect(lambda: func_linkStarter(mode=y)), menuNameLi, modeLi))
    if "selected" in param.need:
        linkmenu2 = param.menu.addMenu(prefix + say("选中连接"))
        list(map(
            lambda x, y: linkmenu2.addAction(x).triggered.connect(
                lambda: func_linkStarter(mode=y, param=param)), menuNameLi, modeLi))


def func_menuAddClearOpen(param: Params = None):
    """用来给清除和打开input功能加按钮"""
    prefix = "" if "prefix" not in param.need else consolerName
    menuli = ["清空input", "打开input"]
    funcli = [func_clearInput, func_openInput]
    list(map(lambda x, y: param.menu.addAction(f"{prefix}{say(x)}").triggered.connect(y), menuli, funcli))


def func_menuAddBaseMenu(param: Params = None):
    """基础的如,help,config,version"""
    menuli = ["调整config", "查看版本", "打开插件页面"]
    funcli = [func_config, func_version, func_help]
    list(map(lambda x, y: param.menu.addAction(f"{say(x)}").triggered.connect(y), menuli, funcli))


def func_menuAddSingleInsert(param: Params = None):
    """用来添加常规插入按钮组"""
    menuli = list(map(lambda x: say(x), ["先清除再插入", "直接插入", "插入上一个组", "选中文字更新标签"]))
    needli = ["clear", "", "last", "tag"]
    prefix = "" if "prefix" not in param.need else consolerName
    papamenu = param.menu.addMenu(prefix + say("插入"))

    list(map(
        lambda x, y: papamenu.addAction(x).triggered.connect(
            lambda: func_singleInsert(param=param, need=(y,))), menuli, needli))


def func_menuAddHelper(param: Params = None):
    """提供大部分类似的按钮添加操作帮助"""
    if "link" in param.need: func_menuAddLink(param=param)
    if "browserinsert" in param.need: func_menuAddBrowserInsert(param=param)
    if "clear/open" in param.need: func_menuAddClearOpen(param=param)
    if "basicMenu" in param.need: func_menuAddBaseMenu(param=param)
    if "insert" in param.need: func_menuAddSingleInsert(param=param)
    pass


def func_add_browsermenu(browser: Browser = None):
    """给browser的bar添加按钮"""
    if hasattr(browser, "hjp_link"):
        menu: QMenu = browser.hjp_Link
    else:
        menu = browser.hjp_Link = QMenu("hjp_link")
        browser.menuBar().addMenu(browser.hjp_Link)
    '''
    连接:5个,插入:3个,打开,清空,配置,版本,帮助
    '''
    param = Params(menu=menu, parent=browser, need=("link", "browserinsert", "clear/open", "basicMenu",))
    func_menuAddHelper(param=param)


def fun_add_browsercontextmenu(browser: Browser, menu: QMenu):
    """用来给browser加上下文菜单"""
    param = Params(menu=menu, parent=browser, need=("browserinsert", "prefix",))
    func_menuAddHelper(param=param)


def func_add_editorcontextmenu(view: AnkiWebView, menu: QMenu):
    """用来给editor界面加上下文菜单"""
    editor = view.editor
    selected = editor.web.selectedText()
    try:
        card_id = editor.card.id
    except:
        console(say("由于这里无法读取card_id, 连接菜单不在这显示"))
        return
    param = Params(menu=menu, parent=view, card_id=str(card_id), desc=selected,
                   need=("insert", "clear/open", "prefix",))
    func_menuAddHelper(param=param)


def func_add_webviewcontextmenu(view: AnkiWebView, menu: QMenu):
    """正如其名,给webview加右键菜单"""
    selected = view.page().selectedText()
    cid = "0"
    if view.title == "main webview" and mw.state == "review":
        cid = mw.reviewer.card.id
    elif view.title == "previewer":
        cid = view.parent().card().id
    if cid != "0":
        param = Params(desc=selected, card_id=str(cid),
                       parent=view, menu=menu, need=("link", "insert", "clear/open", "prefix",))
        func_menuAddHelper(param=param)


gui_hooks.browser_menus_did_init.append(func_add_browsermenu)
gui_hooks.browser_will_show_context_menu.append(fun_add_browsercontextmenu)
gui_hooks.profile_will_close.append(func_clearInput)
gui_hooks.editor_will_show_context_menu.append(func_add_editorcontextmenu)
gui_hooks.webview_will_show_context_menu.append(func_add_webviewcontextmenu)
