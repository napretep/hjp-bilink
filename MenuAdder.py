"""
专门用来加按钮的文件
"""
from aqt import gui_hooks
from aqt.qt import *

from .language import rosetta as say
from .mainfunctions import *


def func_menuAddBrowserInsert(menu: QMenu, browser: Browser, prefix=""):
    """browser插入类函数集合"""
    menuNameLi = list(map(lambda x: prefix + say(x), ["清除后选中卡片插入", "将选中卡片插入", "将选中卡片编组插入"]))
    need = ["", "group", "clear"]
    if prefix != "":
        linkmenu = menu
    else:
        linkmenu = menu.addMenu(say("插入"))
    list(map(lambda x, y: linkmenu.addAction(x).triggered.connect(lambda: func_browserCopy(browser, need=[y])),
             menuNameLi, need))
    pass


def func_menuAddLink(menu: QMenu):
    """用来给连接类型的函数加按钮"""
    menuNameLi = list(map(lambda x: say(x), ["默认连接", "完全图连接", "组到组连接", "按结点取消连接", "按路径取消连接"]))
    linkmenu = menu.addMenu(say("连接"))

    modeLi = [999, 0, 1, 2, 3]
    list(
        map(lambda x, y: linkmenu.addAction(x).triggered.connect(lambda: func_linkStarter(mode=y)), menuNameLi, modeLi))


def func_menuAddClearOpen(menu: QMenu):
    """用来给清除和打开input功能加按钮"""
    menuli = ["清空input", "打开input"]
    funcli = [func_clearInput, func_openInput]
    list(map(lambda x, y: menu.addAction(f"{say(x)}").triggered.connect(y), menuli, funcli))


def func_menuAddBaseMenu(menu: QMenu):
    """基础的如,help,config,version"""
    menuli = ["调整config", "查看版本", "打开插件页面"]
    funcli = [func_config, func_version, func_help]
    list(map(lambda x, y: menu.addAction(f"{say(x)}").triggered.connect(y), menuli, funcli))


func_dict_need = {
    "link": func_menuAddLink,
    "browserinsert": func_menuAddBrowserInsert,
    "clean/open": func_menuAddClearOpen,
    "basicMenu": func_menuAddBaseMenu
}


def func_menuAddHelper(menu: QMenu, parent: Union[Browser, QObject] = None, need: list = None):
    """提供大部分类似的按钮添加操作帮助"""
    if "link" in need: func_dict_need["link"](menu)
    if "browserinsert" in need:
        if "prefix" in need:
            func_dict_need["browserinsert"](menu, parent, prefix="hjp-bilink|")
        else:
            func_dict_need["browserinsert"](menu, parent)
    if "clean/open" in need: func_dict_need["clean/open"](menu)
    if "basicMenu" in need: func_dict_need["basicMenu"](menu)
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
    func_menuAddHelper(menu, browser, need=["link", "browserinsert", "clean/open", "basicMenu"])


def fun_add_browsercontextmenu(browser: Browser, menu: QMenu):
    """用来给browser加上下文菜单"""
    func_menuAddHelper(menu, browser, need=["browserinsert", "prefix"])


gui_hooks.browser_menus_did_init.append(func_add_browsermenu)
gui_hooks.browser_will_show_context_menu.append(fun_add_browsercontextmenu)
