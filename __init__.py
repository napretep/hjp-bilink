"""初试入口"""
from .MenuAdder import *
from aqt.webview import AnkiWebPage


def data_selectedFromBrowserTable(browser, *args, **kwargs):
    cardLi: List[str] = list(map(lambda x: str(x), browser.selectedCards()))
    inputObj = Input()
    if len(cardLi) > 0:
        inputObj.data = inputObj.pairLi_extract(cardLi)
        console("inputObj.data:" + inputObj.data.__str__()).log.end()
        param = Params(input=inputObj, parent=browser, features=["selected", "browserShortCut"])
        return param
    else:
        return None


def shortcut_inputDialog_open(*args, **kwargs):
    """打开input对话框"""
    func_openInput()


def shortcut_inputFile_clear(*args, **kwargs):
    """清空input"""
    func_clearInput()


def shortcut_browserTableSelected_link(browser: Browser, *args, **kwargs):
    """根据默认链接参数对选中的卡片进行链接, 如果是按组到组链接, 则强制每一个卡片为一组"""
    param = data_selectedFromBrowserTable(browser)
    if param is not None:
        func_linkStarter(mode=int(param.input.configObj.defaultLinkMode), **param.__dict__)
    else:
        console(say("未选择卡片")).talk.end()


def shortcut_browserTableSelected_unlink(browser: Browser, *args, **kwargs):
    """根据默认链接参数对选中的卡片进行反链接"""
    param = data_selectedFromBrowserTable(browser)
    if param is not None:
        func_linkStarter(mode=int(param.input.configObj.defaultUnlinkMode), **param.__dict__)
    else:
        console(say("未选择卡片")).talk.end()


def shortcut_browserTableSelected_insert(browser: Browser, *args, **kwargs):
    """根据默认插入参数对选中的卡片进行插入"""
    param = data_selectedFromBrowserTable(browser)
    insertMode = {4: "", 5: "clear", 6: "group"}
    if param is not None:
        param.features += [insertMode[int(param.input.configObj.defaultInsertMode)], "noTag"]
        func_linkStarter(mode=4, **param.__dict__)
    else:
        console(say("未选择卡片")).talk.end()


def wrapper_shortcut(func):
    def shortcutconnect(k, v, self_, *args, **kwargs):
        self_.__dict__["hjp_bilink_action" + k] = \
            QShortcut(QKeySequence(v[0]), self_, activated=lambda: v[1](self_, *args, **kwargs))

    @functools.wraps(func)
    def shortCut_add(self, *args, **kwargs):
        self_ = sys._getframe(1).f_locals["self"].__str__()
        result = func(self, *args, **kwargs)
        for place in placeDict:
            if place == "all":
                list(map(lambda k: shortcutconnect(k, placeDict[place][k], self, *args, **kwargs), placeDict[place]))
            elif place in self_:
                list(map(lambda k: shortcutconnect(k, placeDict[place][k], self, *args, **kwargs), placeDict[place]))
        return result

    return shortCut_add


config = Params(**Input().config)
globalShortcutDict = {
    "InputDialog_open": (config.shortcut_inputDialog_open, shortcut_inputDialog_open),
    "inputFile_clear": (config.shortcut_inputFile_clear, shortcut_inputFile_clear)
}

browserShortcutDict = {
    "Link": (config.shortcut_browserTableSelected_link, shortcut_browserTableSelected_link,),
    "Unlink": (config.shortcut_browserTableSelected_unlink, shortcut_browserTableSelected_unlink),
    "Insert": (config.shortcut_browserTableSelected_insert, shortcut_browserTableSelected_insert)
}
placeDict = {"all": globalShortcutDict, "Browser": browserShortcutDict}


def shortcut_addto_originalcode(*arg, **kwargs):
    Browser.__init__ = wrapper_shortcut(Browser.__init__)
    AnkiWebView.__init__ = wrapper_shortcut(AnkiWebView.__init__)
    EditorWebView.__init__ = wrapper_shortcut(EditorWebView.__init__)


# AnkiWebView.dropEvent=
# AnkiWebView.allowDrops=True
gui_hooks.profile_did_open.append(shortcut_addto_originalcode)
