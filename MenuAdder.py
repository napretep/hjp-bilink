from aqt import mw, gui_hooks, AnkiQt
from aqt.browser import Browser
from aqt.qt import *
from .language import rosetta as say
from .mainfunctions import *


def func_menuAddBrowserInsert(menu: QMenu,browser:Browser):
    """browser插入类函数集合"""
    menuNameLi=list(map(lambda x:say(x),["清除后选中卡片插入","将选中卡片插入","将选中卡片编组插入"]))
    need=["","group","clear"]
    linkmenu = menu.addMenu(say("插入"))
    list(map(lambda x,y:linkmenu.addAction(x).triggered.connect(lambda :func_browserCopy(browser,need=[y])), menuNameLi,need))
    pass


def func_menuAddLink(menu: QMenu):
    """连接类函数集合
    @param menu:
    @type menu:
    """
    menuNameLi = list(map(lambda x: say(x), ["默认连接", "完全图连接", "组到组连接", "按结点取消连接", "按路径取消连接"]))
    linkmenu = menu.addMenu(say("连接"))

    modeLi = [999, 0, 1, 2, 3]
    list(
        map(lambda x, y: linkmenu.addAction(x).triggered.connect(lambda: func_linkStarter(mode=y)), menuNameLi, modeLi))


func_dict_need = {
    "link": func_menuAddLink,
    "browserinsert": func_menuAddBrowserInsert
}


def func_menuAddHelper(menu: QMenu, parent:Union[Browser,QObject] = None, need: list = None):
    """提供大部分类似的按钮添加操作帮助"""
    if "link" in need:
        func_dict_need["link"](menu)
    if "browserinsert" in need:
        func_dict_need["browserinsert"](menu,parent)
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
    func_menuAddHelper(menu,browser, need=["link", "browserinsert"])


gui_hooks.browser_menus_did_init.append(func_add_browsermenu)
