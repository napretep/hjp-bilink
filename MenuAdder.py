from aqt import mw, gui_hooks, AnkiQt
from aqt.browser import Browser
from aqt.qt import *
from .language import rosetta as say
from .mainfunctions import *


def func_browser_link(menu: QMenu, parent: QObject = None):
    """链接类函数集合"""
    menuNameLi = list(map(lambda x: say(x), ["默认连接", "完全图连接", "组到组连接", "按结点取消连接", "按路径取消连接"]))
    linkmenu = menu.addMenu(say("连接"))
    list(map(lambda x: linkmenu.addAction(x), menuNameLi))



func_dict_need = {
    "browserlink": func_browser_link
}


def func_menuhelper(menu: QMenu, parent: QObject = None, need: list = None):
    """提供大部分类似的按钮添加操作帮助"""
    if "browserlink" in need:
        func_dict_need["browserlink"](menu, parent)
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
    func_menuhelper(menu, need=["browserlink"])


gui_hooks.browser_menus_did_init.append(func_add_browsermenu)
