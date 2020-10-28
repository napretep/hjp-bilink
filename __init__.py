import os, sys, datetime, json, re
# import win32.win32clipboard as clipboard 
# import the main window object (mw) from aqt
from aqt import mw, gui_hooks
from html.parser import HTMLParser
from aqt.browser import Browser
from aqt.utils import showInfo, tooltip
from aqt.qt import *

from anki import hooks
import html

from dataclasses import dataclass
from enum import Enum
from operator import itemgetter
from typing import Callable, List, Optional, Sequence, Tuple, Union

helpSite = "https://gitee.com/huangjipan/hjp-bilink"
inputFileName = "input.json"
configFileName = "config.json"
helpFileName = "README.md"
relyLinkDir = "1423933177"
relyLinkConfigFileName = "config.json"
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
PREV_FOLDER = os.path.dirname(THIS_FOLDER)
RELY_FOLDER = os.path.join(PREV_FOLDER, relyLinkDir)
inputSchema='{"IdDescPairs":[],"addTag":""}'

class Link(object):
    def __init__(self, path, cfgpath, relycfgpath, prefix_cid="prefix_cid", defaultMode=999):
        self.path = path
        self.cfgpath = cfgpath
        self.confg = json.load(open(cfgpath, "r", encoding="utf-8"))
        self.relycfg = json.load(open(relycfgpath, "r", encoding="utf-8"))
        if defaultMode == 999:
            self.mode = self.confg["linkMode"]
        else:
            self.mode = defaultMode

        self.prefix = self.confg["cidPrefix"]
        self.fieldPosi = self.confg["appendNoteFieldPosition"]
        self.mapFuncPath = [
            self.completemap,  # mode0
            self.groupBygroup,  # mode1
            self.unlinkNode,  # mode2
            self.unlinkPath,#mode3
        ]
        if self.prefix != self.relycfg[prefix_cid]:
            self.relycfg[prefix_cid] = self.prefix
            json.dump(self.relycfg, open(relycfgpath, "w", encoding="utf-8"))
        self.fdata = {"IdDescPairs":[],"IdDescGroups":[]}
        '''fdata 并不存储原始的json数据,他用来去重,再分装到group和pair,这是对旧函数的兼容'''
        fdata=json.load(open(os.path.join(THIS_FOLDER, inputFileName), "r", encoding="utf-8"))
        same=[]
        for pl in fdata["IdDescPairs"]:
            for p in pl:
                if p["card_id"] in same:
                    continue
                else:
                    same.append(p["card_id"])
                    self.fdata["IdDescPairs"].append(p)
            self.fdata["IdDescGroups"].append(pl)
        self.fdata["addTag"]=fdata["addTag"]

    def start(self):
        if len(self.fdata["IdDescPairs"]) == 0 and len(self.fdata["IdDescGroups"]) == 0:
            showInfo("no data！")
            return
        tooltip("mode:" + str(int(self.mode)) + ",start")
        self.mapFuncPath[self.mode]()
        if self.confg["addTagEnable"]==1:
            if self.mode<=2:self.appendTagForAllNote()
        tooltip("finished!")

    # 下面的是工具
    def getCardNoteFromId(self, li: int) -> object:
        return mw.col.getCard(li).note()

    def appendTagForAllNote(self)-> None:
        """加tag,默认加时间戳,有空自己去改"""
        tagbase = self.confg["addTag"]+"::"
        tagtail = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        cidli = self.fdata["IdDescPairs"]
        if self.fdata["addTag"]!="":
            tagtail=self.fdata["addTag"]
        tag=tagbase+tagtail
        for cidpair in cidli:
            note=self.getCardNoteFromId(cidpair["card_id"])
            note.addTag(tag)
            note.flush()

    def appendIDtoNote(self, note, IdDescPair, dir : str = "→"):
        '''
        note必须是一个cardnote,posi是一个cardnote的位置,Id_DescribePair是卡号、描述的键值对
        '''
        if dir == '→':
            dir=self.confg["linkToSymbol"]
        if dir == '←':
            dir=self.confg["linkFromSymbol"]
        style=self.confg["linkStyle"]
        Id = IdDescPair["card_id"]
        descstr = self.getCardNoteFromId(IdDescPair["card_id"]).fields[self.confg["readDescFieldPosition"]]
        seRegx = self.confg["DEFAULT"]["regexForDescContent"] if self.confg["regexForDescContent"] == 0 else self.confg[
            "regexForDescContent"]
        Desc = IdDescPair["desc"] if len(IdDescPair["desc"]) > 1 else re.search(seRegx, descstr)[0]
        note.fields[self.fieldPosi] += f"<div card_id='{Id}' dir = '{dir}' style='{style}'>{dir}{Desc} {self.prefix}{Id}</div>\n"
        note.flush()

    def getCardIDfromNote(self, id : int) -> list:
        note = self.getCardNoteFromId(id)
        content = note.fields[self.fieldPosi]
        return re.findall(f"(?<={self.prefix})" + r"\d{13}", content)

    # 下面的是链接算法
    def AmapB(self, groupA, groupB):
        '''
        A位置的所有ID插入到B中,并作一个B的反向链接回A.
        json格式必须是AmapB起头,然后A位置输完要给一个换行符
        这个以后要大改.改好了
        '''
        fieldPosi = self.fieldPosi
        for idpA in groupA:
            Anote = self.getCardNoteFromId(idpA["card_id"])
            for idpB in groupB:
                Bnote = self.getCardNoteFromId(idpB["card_id"])
                if re.search(str(idpB["card_id"]), Anote.fields[fieldPosi]) is None:
                    self.appendIDtoNote(Anote, idpB)
                if re.search(str(idpA["card_id"]), Bnote.fields[fieldPosi]) is None:
                    self.appendIDtoNote(Bnote, idpA, dir="←")

    def completemap(self):
        '''
        完全图,没什么说的
        '''
        cidli = self.fdata["IdDescPairs"]
        fieldPosi = self.fieldPosi
        for cidP in cidli:
            if cidP["card_id"] == 0:
                continue
            # 笔记是一个对象
            note = self.getCardNoteFromId(cidP["card_id"])
            for linkcid in cidli:
                # 怎样才能访问到fields,需要用数字下标,访问到的是HTML模式
                IdA = cidP["card_id"]
                IdB = linkcid["card_id"]
                if IdA != IdB and (re.search(str(IdB), note.fields[fieldPosi]) is None):
                    self.appendIDtoNote(note, linkcid)

    def groupBygroup(self):
        '''
        将其首尾分段相连A-B-C
        '''
        cidli = self.fdata["IdDescGroups"]
        placeholder = {"card_id": 0, "desc": ""}
        if len(cidli) < 2:
            showInfo("link failed, not enough groups!")
            return
        else:  # 说明groupSeperIdx 至少2个
            for i in range(0, len(cidli) - 1):  # 0,1,2起步
                liA = cidli[i]
                liB = cidli[i + 1]
                self.AmapB(liA, liB)

    def unlinkNode(self):
        idpli = self.fdata["IdDescPairs"]
        for idp in idpli:
            id = str(idp["card_id"])
            linkli = self.getCardIDfromNote(int(id))

            for link in linkli:

                note = self.getCardNoteFromId(int(link))  # 链到的卡片上找自己

                content = re.sub(f'''<div card_id=["']{id}["'][\\s\\S]+?{id}</div>''', "", note.fields[self.fieldPosi])
                note.fields[self.fieldPosi] = content
                note.flush()
                note = self.getCardNoteFromId(idp["card_id"])
                content = re.sub(f'''<div card_id=["']{link}["'][\\s\\S]+?{link}</div>''', "",
                                 note.fields[self.fieldPosi])

                note.fields[self.fieldPosi] = content
                note.flush()

    def unlinkPath(self):
        idpli = self.fdata["IdDescPairs"]
        for i in range(0, len(idpli) - 1):
            idA = idpli[i]["card_id"]
            idB = idpli[i + 1]["card_id"]
            noteA = self.getCardNoteFromId(idA)
            noteB = self.getCardNoteFromId(idB)
            content = re.sub(f'''<div card_id=["']{str(idA)}["'][\\s\\S]+?{str(idA)}</div>''', "",
                             noteB.fields[self.fieldPosi])
            noteB.fields[self.fieldPosi] = content
            noteB.flush()
            content = re.sub(f'''<div card_id=["']{str(idB)}["'][\\s\\S]+?{str(idB)}</div>''', "",
                             noteA.fields[self.fieldPosi])
            noteA.fields[self.fieldPosi] = content
            noteA.flush()


def setupFunction(mode=999):
    input = os.path.join(THIS_FOLDER, inputFileName)
    cfg = os.path.join(THIS_FOLDER, configFileName)
    relycfg = os.path.join(RELY_FOLDER, relyLinkConfigFileName)
    Linker = Link(input, cfg, relycfg, defaultMode=mode)
    Linker.start()


def destroyFuntion():
    fdata = open(os.path.join(THIS_FOLDER, inputFileName), "w", encoding="utf-8")
    fdata.write(inputSchema)
    fdata.close()
    tooltip(f"{inputFileName} inited")


# mw.col.getCard(li).note()
def multicopyFunction(self, groupCopy=False):
    cfgpath = os.path.join(THIS_FOLDER, configFileName)
    confg = json.load(open(cfgpath, "r", encoding="utf-8"))
    s = json.load(open(os.path.join(THIS_FOLDER, inputFileName), "r", encoding="utf-8"))
    group = []
    browser = self
    if len(browser.selectedCards()) == 0:
        showInfo("nothing to copy!")
        return
    for card_id in browser.selectedCards():
        note = mw.col.getCard(card_id).note()  # 读取卡片
        content = note.fields[confg["appendNoteFieldPosition"]]  # 读取字段
        seRegx = confg["DEFAULT"]["regexForDescContent"] if confg["regexForDescContent"] == 0 else confg[
            "regexForDescContent"]  # 读取正则规则
        Desc = re.search(seRegx, content)[0]  # 综上读取描述文字
        pair = {"card_id": card_id, "desc": Desc}
        if groupCopy:
            group.append(pair)
        else:
            s["IdDescPairs"].append([pair])
    if len(group) > 0:
        s["IdDescPairs"].append(group)
    json.dump(s, open(os.path.join(THIS_FOLDER, inputFileName), "w", encoding="utf-8"), indent=4, ensure_ascii=False)
    tooltip(str(len(browser.selectedCards())) + " card has been appended to the json file")

def displayFunction():
    Url = QUrl.fromLocalFile("" + os.path.join(THIS_FOLDER, inputFileName))
    QDesktopServices.openUrl(Url)


def configFunction():
    Url = QUrl.fromLocalFile("" + os.path.join(THIS_FOLDER, configFileName))
    QDesktopServices.openUrl(Url)


def helpFunction():
    Url = QUrl(helpSite)
    QDesktopServices.openUrl(Url)


menuActionCollect = {}
menuToolsItems = {
    'linkDefault': lambda m=999: setupFunction(mode=999),
    'linkAll': lambda m=0: setupFunction(mode=0),
    'linkGroupToGroup': lambda m=1: setupFunction(mode=1),
    'unlinkNode': lambda m=2: setupFunction(mode=2),
    'unlinkPath': lambda m=3: setupFunction(mode=3),
    'initInput': destroyFuntion,
    'show': displayFunction,
    'config': configFunction,
    'help': helpFunction,
}

'''

'''


def linkActToMainMenu():
    '''
    将函数与钩子配对加到菜单里
    '''
    for name, action in menuToolsItems.items():
        menuActionCollect[name] = QAction(name, mw)
        menuActionCollect[name].triggered.connect(action)
        mw.form.menuTools.addAction(menuActionCollect[name])


def setUpMenuShortcut(self):
    # 将参数命名为browser
    browser = self
    '''
    #如果browser存在,直接让m读取menulinking属性,如果不存在,我们就自己创建一个
    函数用的是QMenu
    然后访问menubar也就是菜单栏,插入一个菜单.方法是insertmenu,参数是self.mw.form.menuTools.menuAction表示表单动作,
    menulinking就是刚建立的表单按钮,也就是Qmenu.
    '''
    try:
        m = self.hjp_Link
    except:
        self.hjp_Link = QMenu("hjp_link")
        self.menuBar().insertMenu(self.mw.form.menuTools.menuAction(), self.hjp_Link)
        m = self.hjp_Link
    for name, action in menuToolsItems.items():
        menuActionCollect[name] = QAction(name, mw)
        menuActionCollect[name].triggered.connect(action)
        m.addAction(menuActionCollect[name])


def AddToTableContextMenu(browser, menu):
    actionCopyCidAll = QAction("hjpCopyCidAlltoInputJson", browser)
    actionCopyCidAll.triggered.connect(lambda _, b=browser: multicopyFunction(b))
    menu.addAction(actionCopyCidAll)
    actionGroupCopy = QAction("hjpAsGroupCopytoInputJson", browser)
    actionGroupCopy.triggered.connect(lambda _, b=browser: multicopyFunction(b, groupCopy=True))
    menu.addAction(actionGroupCopy)


gui_hooks.browser_menus_did_init.append(setUpMenuShortcut)
gui_hooks.browser_will_show_context_menu.append(AddToTableContextMenu)
gui_hooks.profile_will_close.append(destroyFuntion)

# linkActToMainMenu()
