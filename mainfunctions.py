"""
这个文件保存常用函数
"""

from aqt import dialogs

from .InputDialog import InputDialog
from .inputObj import *
from .language import rosetta as say
from .utils import *


def func_config():
    """打开配置文件"""
    return Input().configOpen()


def func_version():
    """返回版本号"""
    console(VERSION).showInfo.talk()


def func_help():
    """返回帮助页面"""
    return Input().helpSiteOpen()


def func_openInput():
    """打开input对话框"""
    try:
        mw.InputDialog.activateWindow()
    except:
        mw.InputDialog = InputDialog.end()
        mw.InputDialog.exec()
        mw.activateWindow()
    """返回input窗口"""


def func_clearInput():
    """清空input文件"""
    return Input().dataLoad.dataReset.dataSave


def func_onProgramClose():
    """当要关闭的时候,做一些事情."""
    func_clearInput()
    console().logFileClear.end()


def func_completeMap(param: Params = None):
    """完全图链接,此时group分组不影响."""
    data = param.input.dataFlat.dataUnique.val  # 不分group,只有pairs
    console(data.__str__()).log.end()
    i = param.input
    [list(map(lambda pairB: i.note_insertPair(pairA, pairB), data)) for pairA in data]


def func_GroupByGroup(param: Params = None):
    """组到组链接"""
    input_obj = param.input
    data: List[List[Pair]] = input_obj.dataObj.val
    console(data.__str__()).log.end()
    reduce(input_obj.group_bijectReducer, data)


def func_unlinkByNode(param: Params = None):
    """按结点取消链接"""
    objInput = param.input
    pairLi = objInput.dataLoad.dataObj.dataFlat.dataUnique.val
    console(pairLi.__str__()).log.end()
    [list(map(lambda pairB: objInput.anchor_unbind(pairA, pairB), pairLi)) for pairA in pairLi]


def func_unlinkByPath(param: Params = None):
    """按路径取消链接"""
    objInput = param.input
    pairLi = objInput.dataLoad.dataObj.dataFlat.dataUnique.val
    console("pairLi=" + list(map(lambda pair: pair.desc, pairLi)).__str__()).log.end()
    reduce(lambda x, y: objInput.anchor_unbind(x, y), pairLi)


def func_addTagToAllNote(param: Params = None, ):
    """给所有的Note加tag"""


def func_linkStarter(mode=999, param: Params = None):
    """开始链接的入口,预处理,根据模式选择一种链接算法"""
    funcli = [func_completeMap, func_GroupByGroup, func_unlinkByNode, func_unlinkByPath]
    param.input = Input()
    if mode == 999: mode = param.input.config["linkMode"]
    if "seleted" in param.need:
        """如果是选中模式,直接读取dict"""
        pass
    else:
        if mw.state == "review": mw.reviewer.cleanup()
        if len(param.input.data["IdDescPairs"]) == 0:
            console(say("input中没有数据！")).showInfo.talk()
            return False
        browser = param.parent if isinstance(param.parent, Browser) else dialogs.open("Browser", mw)
        browser.maybeRefreshSidebar()
        browser.model.layoutChanged.emit()
        browser.editor.setNote(None)
        funcli[mode](param=param)
        browser.maybeRefreshSidebar()
        browser.model.layoutChanged.emit()
        browser.editor.setNote(None)
        browser.model.reset()  # 关键作用
        if param.input.config["addTagEnable"] == 0:
            func_addTagToAllNote(param=param)
            browser.model.search(f"tag:{param.input.data['addTag']}")
        if mw.state == "review": mw.reviewer.show()
        if isinstance(param.parent, AnkiWebView):
            if param.parent.title == "previewer":
                param.parent.parent().render_card()
            if param.parent.title == "main webview":
                mw.reviewer.show()


def func_browserInsert(browser: Browser, need: tuple = None):
    """专门用于browser界面的id拷贝
    need: group , clear
    """
    cardLi: List[str] = list(map(lambda x: str(x), browser.selectedCards()))
    if len(cardLi) == 0:
        console(say("没有选中任何卡片")).showInfo.talk()
        return
    inputObj = Input()
    if "clear" in need: inputObj = inputObj.dataReset.dataSave
    pairLi = inputObj.pair_extract(cardLi)
    dataObj = inputObj.dataObj.val
    if "group" in need:
        dataObj.append(pairLi)
    else:
        list(map(lambda x: dataObj.append([x]), pairLi))
    inputObj.data = dataObj
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
        desc1 = param.desc if param.desc != "" else inputObj.desc_extract(c=param.card_id)
        pair = Pair(card_id=param.card_id, desc=desc1)
        if "clear" in need:
            inputObj = inputObj.dataReset
        if "last" in need and len(inputObj.data["IdDescPairs"]) > 0:
            inputObj.data["IdDescPairs"][-1].append(pair.__dict__)
        else:
            inputObj.data["IdDescPairs"].append([pair.__dict__])
    return inputObj.dataSave
