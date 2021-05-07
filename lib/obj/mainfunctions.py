"""
这个文件保存常用函数
"""
import copy
from functools import reduce
from typing import List

from PyQt5.QtCore import QUrl, QObject
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QTreeView
from aqt import mw, dialogs
from aqt.browser import Browser
from aqt.utils import showInfo
from aqt.webview import AnkiWebView

from .languageObj import rosetta as say

from .inputObj import Input
from .utils import BaseInfo, console, Params, Pair, CustomSignals, wrapper_webview_refresh, wrapper_browser_refresh, \
    No_hierarchical_tag, compatible_browser_sidebar_refresh
from ..dialogs.DialogInput import InputDialog
from ..dialogs.DialogAnchor import AnchorDialog
from ..dialogs.DialogConfig import ConfigDialog
from ..dialogs.DialogVersion import VersionDialog


def func_contactMe():
    # url =  QUrl(r"start chrome 'G:/备份/数学书大全/微分方程/俄罗斯数学教材选译-常微分方程（庞特里亚金）.pdf#page=20'")
    url = QUrl(BaseInfo().groupSite)
    QDesktopServices.openUrl(url)
    # QProcess.start()
    # # app = QApplication(sys.argv)
    # mainWin = testwindow()
    # # availableGeometry = app.desktop().availableGeometry(mainWin)
    # # mainWin.resize(availableGeometry.width() * 2 / 3, availableGeometry.height() * 2 / 3)
    # mainWin.exec()
    # # sys.exit(app.exec_())


def func_supportMe():
    showInfo(say("请多多转发支持!"))


def func_anchorUpdate():
    """对外的接口"""
    Input().anchor_updateVersion()


def func_config():
    """打开配置文件"""
    ConfigDialog().exec()


def func_version():
    """返回版本号"""
    DialogSingleCheck(VersionDialog)


def func_help():
    """返回帮助页面"""
    Input().helpSite_open()


def func_openInput(*args, **kwargs):
    """打开input对话框"""
    DialogSingleCheck(InputDialog)


def DialogSingleCheck(Dialog):
    """单一窗口的打开"""
    consoler_Name = BaseInfo().dialogName
    dialog = Dialog.__name__
    if dialog not in mw.__dict__[consoler_Name]:
        mw.__dict__[consoler_Name][dialog] = None
    if mw.__dict__[consoler_Name][dialog] is not None:
        mw.__dict__[consoler_Name][dialog].activateWindow()
    else:
        mw.__dict__[consoler_Name][dialog] = Dialog()
        mw.__dict__[consoler_Name][dialog].exec()
    """返回input窗口"""

def func_openAnchor(*args, **kwargs):
    """打开anchor对话框"""
    param = Params(**kwargs)
    card_id = param.pair.card_id
    dialog = AnchorDialog.__name__
    addonName = BaseInfo().dialogName
    if dialog not in mw.__dict__[addonName]:
        mw.__dict__[addonName][dialog] = {}
    dialog_dict = mw.__dict__[addonName][dialog]
    if card_id not in dialog_dict:
        dialog_dict[card_id] = None
    if dialog_dict[card_id] is not None:
        mw.__dict__[addonName][dialog][card_id].activateWindow()
    else:
        mw.__dict__[addonName][dialog][card_id] = AnchorDialog(param.pair, parent=param.parent)
        mw.__dict__[addonName][dialog][card_id].exec()


def func_clearInput():
    """清空input文件"""
    Input().dataLoad().dataReset().dataSave()
    console(say("input 已清空")).talk.end()


def func_onProgramClose():
    """当要关闭的时候,做一些事情."""
    func_clearInput()
    console().logFileClear.end()


def func_completeMap(*args, **kwargs):
    """完全图链接,此时group分组不影响."""
    param = Params(**kwargs)
    pairLi = param.input.dataFlat().dataUnique().val()  # 不分group,只有pairs
    console(pairLi.__str__()).log.end()
    i = param.input
    [list(map(lambda pairB: i.pair_insert(pairA, pairB), pairLi)) for pairA in pairLi]
    if "selected" in param.features:
        mode = say("多选模式")
    else:
        mode = say("普通模式")
    console(f"""[{mode}]-{say("已按完全图完成链接")}""").talk.end()

def func_GroupByGroup(*args, **kwargs):
    """组到组链接"""
    param = Params(**kwargs)
    input_obj: Input = param.input
    PairLi: List[List[Pair]] = input_obj.dataObj_
    console(PairLi.__str__()).log.end()
    reduce(input_obj.group_bijectReducer, PairLi)
    if "selected" in param.features:
        mode = say("多选模式")
    else:
        mode = say("普通模式")
    console(f"""[{mode}]-{say("已按组到组完成链接")}""").talk.end()

def func_unlinkByNode(*args, **kwargs):
    """按结点取消链接"""
    param = Params(**kwargs)
    input_obj: Input = param.input
    pairLi = input_obj.dataFlat().dataUnique().val()
    console(pairLi.__str__()).log.end()
    [list(map(lambda pairB: input_obj.anchor_unbind(pairA, pairB), pairLi)) for pairA in pairLi]
    if "selected" in param.features:
        mode = say("多选模式")
    else:
        mode = say("普通模式")
    console(f"""[{mode}]-{say("已按结点取消链接")}""").talk.end()

def func_unlinkByPath(*args, **kwargs):
    """按路径取消链接"""
    param = Params(**kwargs)
    input_obj: Input = param.input
    pairLi = input_obj.dataFlat().dataUnique().val()
    console("pairLi=" + list(map(lambda pair: pair.desc, pairLi)).__str__()).log.end()
    reduce(lambda x, y: input_obj.anchor_unbind(x, y), pairLi)
    if "selected" in param.features:
        mode = say("多选模式")
    else:
        mode = say("普通模式")
    console(f"""[{mode}]-{say("已按路径取消链接")}""").talk.end()


def func_addTagToAllNote(param: Params = None, ):
    """给所有的Note加tag"""


class LinkStarter(QObject):
    """开始链接的入口,预处理,根据模式选择一种链接算法"""
    linkedSignal = CustomSignals.start().linkedEvent

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.signal = CustomSignals
        self.func_linkStarter(*args, **kwargs)
        self.linkedSignal.emit()

    @wrapper_webview_refresh
    @wrapper_browser_refresh
    def func_linkStarter(self, *args, **kwargs):
        """开始链接的入口,预处理,根据模式选择一种链接算法"""
        param = Params(**kwargs)
        if param.mode == 999: param.mode = param.input.baseinfo.config_obj.defaultLinkMode
        if "selected" in param.features:  # 如果是选中模式,直接读取dict
            if isinstance(param.parent, QTreeView):
                param.input = param.parent.parent.input
            if "browserShortCut" in param.features and isinstance(param.parent, Browser):
                pass
        else:
            param.input.dataLoad()
        # if mw.state == "review": mw.reviewer.cleanup()
        if len(param.input.data["IdDescPairs"]) == 0:
            console(say("input中没有数据！")).showInfo.talk.end()
            return False
        browser = dialogs.open("Browser", mw)
        compatible_browser_sidebar_refresh(browser)
        browser.model.layoutChanged.emit()
        browser.editor.setNote(None)
        funcli[param.mode](**param.__dict__)
        compatible_browser_sidebar_refresh(browser)
        browser.model.layoutChanged.emit()
        browser.editor.setNote(None)
        browser.model.reset()  # 关键作用
        if param.input.baseinfo.config_obj.addTagEnable == 1 and "noTag" not in param.features:
            if No_hierarchical_tag:
                searchStr = " or ".join(["cid:" + p.card_id for p in param.input.dataflat_])
            else:
                param.input.note_addTagAll()
                searchStr = f"tag:{param.input.tag}*"
            console(searchStr).log.end()
            browser.model.search(searchStr)


def func_browserInsert(*args, **kwargs):
    """专门用于browser界面的id拷贝,clear参数代表清空后再插入, group参数代表编组插入,从入口处解决卡片重复问题,不带入input模型
    """
    param = Params(**kwargs)
    if "selected" in param.features and hasattr(param.parent, "parent") and isinstance(param.parent.parent,
                                                                                       AnchorDialog):
        cardLi: List[str] = [pair.card_id for pair in param.parent.parent.input.dataflat_]
    else:
        cardLi: List[str] = list(map(lambda x: str(x), param.parent.selectedCards()))
    if len(cardLi) == 0:
        console(say("没有选中任何卡片")).talk.end()
        return
    inputObj = Input()
    beforeNum = afterNum = 0
    if "clear" not in param.features:
        datastr = inputObj.data.__str__()
        beforeNum = len(cardLi)
        protoCardLi = copy.deepcopy(cardLi)
        for id in protoCardLi:
            if id in datastr: cardLi.remove(id)
        afterNum = len(cardLi)
        if cardLi == []:
            console(say("所选卡片早已插入,跳过任务")).talk.end()
            inputObj.dataLoad().dataSave()
            return
    else:
        inputObj = inputObj.dataReset().dataSave()
    pairLi = inputObj.pairLi_extract(cardLi)
    dataObjLi = inputObj.dataObj().val()
    if "group" in param.features:
        dataObjLi.append(pairLi)
    else:
        list(map(lambda x: dataObjLi.append([x]), pairLi))
    inputObj.data = dataObjLi
    inputObj.dataSave()
    if (beforeNum - afterNum) > 0:
        console(f"{str(beforeNum - afterNum)}{say('张卡片重复插入, 已去重')},{str(afterNum)}{say('张卡片已插入')}") \
            .talk.end()
    else:
        console(f"{str(len(cardLi))}{say('张卡片已插入')}").talk.end()
    return


def func_singleInsert(*args, **kwargs):
    """
    @param param:
    @param  clear , last,  tag
    """
    param = Params(**kwargs)
    inputObj = Input()
    datastr = inputObj.data.__str__()
    if "tag" in param.features:
        inputObj.data["addTag"] = param.pair.desc
        console(say("刚插入的标签为:") + param.pair.desc).talk.end()
    else:
        param.pair.desc = param.pair.desc if param.pair.desc != "" else inputObj.desc_extract(c=param.pair)
        if "clear" in param.features:
            inputObj = inputObj.dataReset().dataSave()
        else:
            if param.pair.card_id in datastr and param.pair.desc in datastr:
                console(say("所选卡片早已插入,跳过任务")).talk.end()
                return
            elif param.pair.card_id in datastr and not param.pair.desc in datastr:
                inputObj.card_remove(param.pair)
                inputObj.dataSave()
        if "last" in param.features and len(inputObj.data["IdDescPairs"]) > 0:
            inputObj.data["IdDescPairs"][-1].append(param.pair.__dict__)
        else:
            inputObj.data["IdDescPairs"].append([param.pair.__dict__])
        console(say("成功插入{卡片-描述}对:") + param.pair.__dict__.__str__()).talk.end()
    return inputObj.dataSave()


funcli = [func_completeMap, func_GroupByGroup, func_unlinkByNode, func_unlinkByPath,
          func_browserInsert, func_singleInsert]
