"""初试入口"""
from aqt import gui_hooks

from .lib.obj.HTML_converterObj import HTML_converter
from .lib.obj.MenuAdder import *


def checkUpdate():
    """检查更新,检查配置表是否对应"""
    needUpdate = False
    base = BaseInfo()
    config_template = base.configTemplateJSON
    user_config_dir = base.configDir
    if os.path.isfile(user_config_dir) and os.path.exists(user_config_dir):
        config = base.configJSON
    else:
        config = {}

    if "VERSION" not in config or config_template["VERSION"] != config["VERSION"]:
        needUpdate = True
        config["VERSION"] = config_template["VERSION"]
        for key, value in config_template.items():
            if key not in config:
                config[key] = value
        for key, value in config.items():
            if key not in config_template:
                config.__deleteitem__(key)
    if needUpdate:
        json.dump(config, open(base.configDir, "w", encoding="utf-8"), indent=4,
                  ensure_ascii=False)
        func_version()

def data_selectedFromBrowserTable(browser, *args, **kwargs):
    """从?"""
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
        LinkStarter(mode=int(param.input.baseinfo.config_obj.defaultLinkMode), **param.__dict__)
    else:
        console(say("未选择卡片")).talk.end()


def shortcut_browserTableSelected_unlink(browser: Browser, *args, **kwargs):
    """根据默认链接参数对选中的卡片进行反链接"""
    param = data_selectedFromBrowserTable(browser)
    if param is not None:
        LinkStarter(mode=int(param.input.baseinfo.config_obj.defaultUnlinkMode), **param.__dict__)
    else:
        console(say("未选择卡片")).talk.end()


def shortcut_browserTableSelected_insert(browser: Browser, *args, **kwargs):
    """根据默认插入参数对选中的卡片进行插入"""
    param = data_selectedFromBrowserTable(browser)
    insertMode = {4: "", 5: "clear", 6: "group"}
    if param is not None:
        param.features += [insertMode[int(param.input.baseinfo.config_obj.defaultInsertMode)], "noTag"]
        LinkStarter(mode=4, **param.__dict__)
    else:
        console(say("未选择卡片")).talk.end()


def wrapper_shortcut(func):
    def shortcutconnect(k, v, self_, *args, **kwargs):
        if v[0] != "":
            self_.__dict__["hjp_bilink_action" + k] = \
                QShortcut(QKeySequence(v[0]), self_, activated=lambda: v[1](self_, *args, **kwargs))
        else:
            return None

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


def shortcut_addto_originalcode(*arg, **kwargs):
    """用来绑定快捷键,有些快捷键还是失效的,需要再改进 TODO"""
    Browser.__init__ = wrapper_shortcut(Browser.__init__)
    # 下面的快捷键不支持
    # AnkiWebView.__init__ = wrapper_shortcut(AnkiWebView.__init__)
    # EditorWebView.__init__ = wrapper_shortcut(EditorWebView.__init__)


def HTML_injecttoweb(htmltext, card, kind):
    """在web渲染前,注入html代码,"""
    if kind in [
        "previewQuestion",
        "previewAnswer",
        "reviewQuestion",
        "reviewAnswer",
        "clayoutQuestion",
        "clayoutAnswer",
    ]:
        p = Input()
        field = p.note_id_load(Pair(card_id=str(card.id))).fields[p.insertPosi]
        fielddata = HTML_converter().feed(field).HTMLdata_load()

        html_addedButton = HTML_converter().feed(htmltext) \
            .HTMLdata_load().HTMLdata_save().HTMLButton_selfdata_make(fielddata).HTMLdata_save().HTML_get().HTML_text
        console("最终结果:" + html_addedButton).log.end()
        return html_addedButton
    else:
        return htmltext


def func_add_browsermenu(browser: Browser = None):
    """给browser的bar添加按钮"""
    if hasattr(browser, "hjp_bilink"):
        menu: QMenu = browser.hjp_bilink
    else:
        menu = browser.hjp_bilink = QMenu("hjp_bilink")
        browser.menuBar().addMenu(browser.hjp_bilink)
    '''
    链接:5个,插入:3个,打开,清空,配置,版本,帮助
    '''
    func_menuAddHelper(menu=menu, parent=browser, actionTypes=["link", "browserinsert", "clear_open", "basicMenu"])


# @debugWatcher
def fun_add_browsercontextmenu(browser: Browser, menu: QMenu):
    """用来给browser加上下文菜单"""
    func_menuAddHelper(menu=menu, parent=browser, features=["prefix"], actionTypes=["browserinsert"])


def func_add_editorcontextmenu(view: AnkiWebView, menu: QMenu):
    """用来给editor界面加上下文菜单"""
    editor = view.editor
    selected = editor.web.selectedText()
    try:
        card_id = editor.card.id
    except:
        console(say("由于这里无法读取card_id, 链接菜单不在这显示")).talk.end()
        return

    func_menuAddHelper(menu=menu, parent=view, pair=Pair(card_id=str(card_id), desc=selected),
                       features=["prefix"], actionTypes=["insert", "clear_open", ])


def func_add_webviewcontextmenu(view: AnkiWebView, menu: QMenu):
    """正如其名,给webview加右键菜单"""
    selected = view.page().selectedText()
    cid = "0"
    if view.title == "main webview" and mw.state == "review":
        cid = mw.reviewer.card.id
    elif view.title == "previewer" and view.parent() is not None and view.parent().card() is not None:
        cid = view.parent().card().id
    if cid != "0":
        func_menuAddHelper(pair=Pair(desc=selected, card_id=str(cid)), features=["prefix"],
                           parent=view, menu=menu, actionTypes=["link", "insert", "clear_open", "anchor", "alter_deck",
                                                                "alter_tag"])


checkUpdate()

config = BaseInfo().config_obj

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

# gui_hooks.profile_did_open.append(shortcut_addto_originalcode)
gui_hooks.card_will_show.append(HTML_injecttoweb)
gui_hooks.browser_menus_did_init.append(func_add_browsermenu)
gui_hooks.browser_will_show_context_menu.append(fun_add_browsercontextmenu)
gui_hooks.profile_will_close.append(func_onProgramClose)
gui_hooks.editor_will_show_context_menu.append(func_add_editorcontextmenu)
gui_hooks.webview_will_show_context_menu.append(func_add_webviewcontextmenu)
