"""
这个文件保存常用函数
"""
from aqt import mw, dialogs
from aqt.browser import Browser
from aqt.webview import AnkiWebView

from .InputDialog import InputDialog
from .inputObj import Input, Pair, Params
from .language import rosetta as say
from .utils import *


def func_config():
    """打开配置文件"""
    return Input().configOpen()


def func_version():
    """返回版本号"""
    showInfo(VERSION)


def func_help():
    """返回帮助页面"""
    return Input().helpSiteOpen()


def func_openInput():
    """打开input对话框"""
    try:
        mw.InputDialog.activateWindow()
    except:
        mw.InputDialog = InputDialog()
        mw.InputDialog.exec()
        mw.activateWindow()
    """返回input窗口"""


def func_clearInput():
    """清空input文件"""
    return Input().dataLoad.dataReset.dataSave


def func_completeMap(param: Params = None):
    """完全图连接"""
    cardGroupLi = param.input.data["IdDescPairs"]
    insertPosi = param.input.config["appendNoteFieldPosition"]
    prefix = param.input.config["cidPrefix"]


def func_GroupByGroup(param: Params = None):
    """组到组连接"""


def func_unlinkByNode(param: Params = None):
    """按结点取消连接"""


def func_unlinkByPath(param: Params = None):
    """按路径取消连接"""


def func_addTagToAllNote(param: Params = None, ):
    """给所有的Note加tag"""


def func_linkStarter(mode=999, param: Params = None):
    """开始连接的入口,预处理,根据模式选择一种连接算法"""
    funcli = [func_completeMap, func_GroupByGroup, func_unlinkByNode, func_unlinkByPath]
    param.input = Input()
    if mode == 999: mode = param.input.config["linkMode"]
    if "seleted" in param.need:
        """如果是选中模式,直接读取dict"""
        pass
    else:
        if mw.state == "review": mw.reviewer.cleanup()
        if len(param.input.data["IdDescPairs"]) == 0:
            showInfo(say("input中没有数据！"))
            return False
        browser = dialogs.open("Browser", mw)
        browser.model.layoutChanged.emit()
        browser.editor.setNote(None, hide=True)
        funcli[mode](param=param)
        browser.maybeRefreshSidebar()
        browser.model.layoutChanged.emit()
        if param.input.config["addTagEnable"] == 1:
            func_addTagToAllNote(param=param)
            browser.model.search(f"tag:{param.input.data['addTag']}")
        if mw.state == "review": mw.reviewer.show()
        if isinstance(param.parent, AnkiWebView) and param.parent.title == "previewer":
            param.parent.parent().render_card()


def func_browserInsert(browser: Browser, need: tuple = None):
    """专门用于browser界面的id拷贝
    need: group , clear
    """
    cardLi: List[str] = list(map(lambda x: str(x), browser.selectedCards()))
    if len(cardLi) == 0:
        showInfo(say("没有选中任何卡片"))
        return
    inputObj = Input()
    idDescPairLi = inputObj.pairExtract(cardLi)
    if "clear" in need:
        inputObj = inputObj.dataReset.dataSave
    if "group" in need:
        inputObj.data["IdDescPairs"].append(idDescPairLi)
    else:
        list(map(lambda x: inputObj.data["IdDescPairs"].append([x]), idDescPairLi))
    return inputObj.dataSave


def func_singleInsert(param: Params = None, need: tuple = None):
    """
    @param param:
    @param need: clear , last,  tag
    """
    inputObj = Input()
    if "tag" in need:
        inputObj.data["addTag"] = param.desc
    else:
        desc1 = param.desc if param.desc != "" else inputObj.descExtract(c=param.card_id)
        pair = Pair(param.card_id, desc1)
        if "clear" in need:
            inputObj = inputObj.dataReset
        if "last" in need and len(inputObj.data["IdDescPairs"]) > 0:
            inputObj.data["IdDescPairs"][-1].append(pair.__dict__)
        else:
            inputObj.data["IdDescPairs"].append([pair.__dict__])
    return inputObj.dataSave
