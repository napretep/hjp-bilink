from anki.notes import Note
from aqt.browser import Browser
from aqt import mw, gui_hooks, browser, AnkiQt
# from html.parser import HTMLParser
from aqt.reviewer import Reviewer
from aqt.editor import EditorWebView
from .linkTool import *
# from .linkTool import _translate
from aqt.qt import *
from aqt import dialogs
from aqt.webview import AnkiWebView
from aqt.previewer import Previewer
from anki.cards import Card
import os, sys, datetime, json, re,copy
from PyQt5 import QtCore, QtGui, QtWidgets
from dataclasses import dataclass
from enum import Enum
from operator import itemgetter
from typing import Callable, List, Optional, Sequence, Tuple, Union
from anki import hooks
from .input import Ui_input

class InputDialog(QDialog,Ui_input):
    def __init(self, parent=None):
        QDialog.__init(self,parent)
        self.selectedData=copy.deepcopy(inputSchema)
        mw.InputDialog=self
        self.term={
        "pair":"pair",
        "card_id":"card_id",
        "desc":"desc",
        "addTag":"addTag"
        }
        # self.setWindowModality(Qt.NonModal)
        self.row=0
        self.cols=["group","desc","card_id"]
        self.initUI()
        self.setupModel()
        self.addEvents()
        self.treeIsChanging=False
        self.show()#光show没用,还得实例化后加一个exec()

    def initUI(self):
        '''UI初始化'''
        self.setupUi(self)
        #designer部件顶层可自定义窗体布局,我不必再加一个.
        self.inputTree.customContextMenuRequested.connect(self.contextMenuOnInputTree)

    def selectedLink(self,mode:int=999):
        delog("开启selected LINK",dbg=True)
        self.loadFromTreeSelected()
        setupFunction(mode=mode,inputJSON=self.selectedData)
        pass

    def contextMenuOnInputTree(self,prefix="hjp-bilink|"):
        '''设置右键菜单'''
        self.inputTree.contextMenu = QMenu(self)
        self.inputTree.contextMenu.addAction(f"{prefix} '全部展开/折叠'").triggered.connect(self.toggleEXPorCOL)
        self.inputTree.contextMenu.addAction(f"{prefix}'选中删除'").triggered.connect(self.deletItem)
        contexthelper(None,self.inputTree.contextMenu,need=["link","clear"])
        selectedLinkMenu = self.inputTree.contextMenu.addMenu(f"{prefix}'选中连接'")
        def connectMenu(Menu:QMenu,desc:str,mode:int):
            Menu.addAction(desc).triggered.connect(lambda _ : self.selectedLink(mode=mode))
        list(map(lambda x,y:connectMenu(selectedLinkMenu,x,y),algPathDict["desc"],algPathDict["mode"]))

        self.inputTree.contextMenu.popup(QCursor.pos())
        self.inputTree.contextMenu.show()
    def onDoubleClick(self,index):
        item=self.model.itemFromIndex(index)
        showInfo(currentLang)

    # '''暂时先不搞这个bug,太难了.___20210124021251搞定了!'''
    # https://stackoverflow.com/questions/26227885/drag-and-drop-rows-within-qtablewidget
    def onDrop(self, e:QDropEvent):
        '''这个东西的难点在于,移除item会导致index对不上,从而导致移空'''
        def removeChild(item:QStandardItem):
            return item.parent().takeRow(item.row())#takeRow先取出后appenrow,这个顺序非常重要!!!!
        selectedIndexesLi=self.inputTree.selectedIndexes()
        selectedItemLi=list(map(self.model.itemFromIndex,selectedIndexesLi))
        drop_row=self.inputTree.indexAt(e.pos())
        targetItem = self.model.itemFromIndex(drop_row)
        if targetItem.parent()!=None:
            targetItem=targetItem.parent()
            if targetItem.parent()!=None:
                targetItem = targetItem.parent()
        removedItemLi=list(map(lambda x:removeChild(x),selectedItemLi))
        nothin= list(map(lambda x: targetItem.appendRow(x),removedItemLi))
        self.JSONsave()
        delog("onDrop",dbg=True)
        e.ignore()

    def addEvents(self):
        self.inputTree.doubleClicked.connect(self.onDoubleClick)
        self.inputTree.dropEvent = self.onDrop
        self.fileWatcher = QFileSystemWatcher()
        self.fileWatcher.addPath(os.path.join(THIS_FOLDER, inputFileName))
        self.fileWatcher.fileChanged.connect(self.JSONtoModel)
        self.model.dataChanged.connect(self.JSONsave)
        self.tagContent.textChanged.connect(self.JSONsave)

    def setupModel(self):
        '''数据模型初始化'''
        # https://github.com/daun4168/BobsSimulator/blob/0f4d13628f9c46fb87e0140eed4ec61489dbe661/Test/test.py
        self.model=QStandardItemModel()
        self.rootNode=self.model.invisibleRootItem()
        self.rootNode.setDropEnabled(False)
        self.rootNode.setEditable(False)
        self.rootNode.setSelectable(False)
        self.rootNode.setDragEnabled(False)
        self.model.setHorizontalHeaderLabels([self.term["card_id"]+"+"+self.term["desc"]])
        self.inputTree.setModel(self.model)
        self.JSONtoModel()

    def loadJson(self):
        self.data: json = json.load(open(os.path.join(THIS_FOLDER, inputFileName), "r", encoding="utf-8"))
    def deletItem(self):
        LI=self.inputTree.selectedIndexes()
        if len(LI)>0:
            for i in range(len(LI)):
                item=self.model.itemFromIndex(LI[i])
                row=item.row()
                col=item.column()
                father=item.parent()
                if father != None:
                    father.removeRow(row)
                else:
                    self.rootNode.removeRow(row)
        self.JSONsave()
    def toggleEXPorCOL(self):
        if self.treeIsExpanded:
            root=self.rootNode
            tree=self.inputTree
            for group in [self.rootNode.child(i) for i in range(root.rowCount())]:
                list(map(lambda x: tree.collapse(x.index()),[group.child(i) for i in range(group.rowCount())]))
            self.treeIsExpanded=False
        else:
            self.inputTree.expandAll()
            self.treeIsExpanded=True

    # dbg = True
    def loadFromTreeSelected(self):
        self.selectedData=copy.deepcopy(inputSchema)
        LI = self.inputTree.selectedIndexes()
        def tool(item:QStandardItem):
            if item.level==1:
                self.selectedData["IdDescPairs"].append([{
                    "card_id":int(item.child(0).text()),
                    "desc":item.child(1).text()
                }])
        if len(LI)>0:
            itemLi=list(map(lambda x: self.model.itemFromIndex(x) , LI))
            list(map(lambda x:tool(x) , itemLi))


    def loadFromTree(self):
        self.data=copy.deepcopy(inputSchema)
        self.data["addTag"]=self.tagContent.text()
        if self.rootNode.rowCount()>0:#groups
            for i in range(self.rootNode.rowCount()):#每个group
                group:List=[]
                self.data["IdDescPairs"].append(group)
                for j in range(self.rootNode.child(i).rowCount()):#每个group中的pair个数
                    try:
                        pair:dict={
                            "card_id":int(self.rootNode.child(i).child(j).child(0).text()),
                            "desc":self.rootNode.child(i).child(j).child(1).text()
                        }
                        self.data["IdDescPairs"][i].append(pair)
                    except:
                        continue
                        pass
    def JSONtoModel(self):
        '''装载INPUT.JSON文件到表格'''
        self.loadJson()
        self.rootNode.clearData()
        self.model.removeRows(0,self.model.rowCount())
        _=self.term
        for groupNum in range(0,len(self.data["IdDescPairs"])):
            gpairs=self.data["IdDescPairs"][groupNum]
            parent = QStandardItem(str(groupNum))
            parent.level = 0
            parent.setFlags(parent.flags()&~Qt.ItemIsEditable&~Qt.ItemIsDragEnabled&~Qt.ItemIsSelectable)
            self.rootNode.appendRow([parent])
            for pairNum in range(0,len(gpairs)):
                pairs=gpairs[pairNum]
                pairsItem=QStandardItem(_["pair"])
                pairsItem.level = 1
                pairsItem.setFlags(pairsItem.flags()&~Qt.ItemIsEditable&~Qt.ItemIsDropEnabled)
                parent.appendRow([pairsItem])
                child1 = QStandardItem(str(pairs[_["card_id"]]))
                child2 = QStandardItem(pairs[_["desc"]])
                child2.setFlags(child1.flags()&~Qt.ItemIsDropEnabled&~Qt.ItemIsDragEnabled&~Qt.ItemIsSelectable)
                child1.setFlags(
                    child2.flags()&
                    ~Qt.ItemIsDropEnabled&
                    ~Qt.ItemIsDragEnabled&
                    ~Qt.ItemIsSelectable&
                    ~Qt.ItemIsEditable)#不可拖拽不可选中不可编辑
                child1.level = child2.level = 2
                pairsItem.appendRow([child1])
                pairsItem.appendRow([child2])
        self.tagContent.setText(self.data[_["addTag"]])
        self.lastrowcount = self.rootNode.rowCount()
        self.inputTree.expandAll()
        self.treeIsExpanded=True
        delog("JSON读取到模型完毕",dbg=True)

    def JSONsave(self):
        '''数据保存'''
        self.loadFromTree()
        json.dump(self.data,
                  open(os.path.join(THIS_FOLDER, inputFileName), "w", encoding="utf-8"),
                  indent=4,
                  ensure_ascii=False)
        delog("JSONsave完成",dbg=True)

    def closeEvent(self, QCloseEvent):
        '''关闭时要保存数据'''
        mw.InputDialog=None
        if len(self.data["IdDescPairs"])>0:
            self.JSONsave()
        else:
            destroyFuntion()


class Link(object):
    def __init(self, path, cfgpath, relycfgpath, prefix_cid="prefix_cid", defaultMode=999,_from=None,inputJSON=None):
        delog("Link启动",dbg=True)
        self.path = path
        self.cfgpath = cfgpath
        self.confg = json.load(open(cfgpath, "r", encoding="utf-8"))
        self.relycfg = json.load(open(relycfgpath, "r", encoding="utf-8"))
        self.tag=""
        delog(f"linkmode={str(self.confg['linkMode'])},defaultMode={defaultMode},",dbg=True)
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
        if inputJSON==None:
            fdata=json.load(open(os.path.join(THIS_FOLDER, inputFileName), "r", encoding="utf-8"))
        else:
            fdata=inputJSON
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
        delog("linkstart启动",dbg=True)
        if mw.state == "review":
            mw.reviewer.cleanup()
        if len(self.fdata["IdDescPairs"]) == 0 and len(self.fdata["IdDescGroups"]) == 0:
            showInfo("input中没有数据！")
            return
        delog("linkstart启动2",dbg=True)
        delog(f"{consolerName}:mode=" + str(int(self.mode)) + ",链接开始",dbg=True)
        self.mapFuncPath[self.mode]()
        delog("linkstart启动3",dbg=True)
        if self.confg["addTagEnable"]==1:
            if self.mode<len(self.mapFuncPath):self.appendTagForAllNote()
        delog(f"{consolerName}:链接结束!",dbg=True)

        if mw.state == "review":
            mw.reviewer.show()

        return self.tag

    # 下面的是工具
    def getCardNoteFromId(self, li: int) -> Note:
        return mw.col.getCard(li).note()

    def appendTagForAllNote(self)-> None:
        """加tag,默认加时间戳,有空自己去改"""
        tagbase = self.confg["addTagRoot"]+"::"
        tagtail = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        cidli = self.fdata["IdDescPairs"]
        delog(f"这里是appendTagForAllNote,fdata['addTag']={self.fdata['addTag']}",dbg=True)
        if self.fdata["addTag"]!="":
            tagtail=self.fdata["addTag"]
        tag=tagbase+tagtail
        for cidpair in cidli:
            note=self.getCardNoteFromId(cidpair["card_id"])
            note.addTag(tag)
            # note.flush() 临时注释
        self.tag=tag

    def appendIDtoNote(self, note, IdDescPair, dir : str = "→"):
        '''
        note必须是一个cardnote,posi是一个cardnote的位置,Id_DescribePair是卡号、描述的键值对
        '''
        if dir == '→':
            direction=self.confg["linkToSymbol"]
        if dir == '←':
            direction=self.confg["linkFromSymbol"]
        style=self.confg["linkStyle"]
        Id = IdDescPair["card_id"]
        descstr = self.getCardNoteFromId(IdDescPair["card_id"]).fields[self.confg["readDescFieldPosition"]]#这里做了重复操作.和multicopy时的功能一样
        seRegx = self.confg["DEFAULT"]["regexForDescContent"] if self.confg["regexForDescContent"] == 0 else self.confg[
            "regexForDescContent"]
        try:
            Desc = IdDescPair["desc"] if len(IdDescPair["desc"]) >= 1 else re.search(seRegx, descstr)[0]
        except:
            showInfo(f"{consolerName}:'正则读取描述字符失败!'")
            return
        note.fields[self.fieldPosi] += f"<button card_id='{Id}' dir = '{dir}' style='font-size:inherit;{style}'>{direction}{Desc} {self.prefix}{Id}</button>\n"
        # note.flush() 临时注释

    def getCardIDfromNote(self, id : int) -> List[str]:
        note = self.getCardNoteFromId(id)
        content = note.fields[self.fieldPosi]
        return re.findall(f"(?<={self.prefix})" + r"\d{13}", content)
    def delAnchor(self,id:str,note:Note)->str:
        # <div card_id="1578352706361" dir="→" style=""><br></div>
        return re.sub(f'''<(:?div|button) card_id=["']{id}["'][\\s\\S]+?{id}</(:?div|button)>''', "",
                             note.fields[self.fieldPosi])
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
        delog(f"{consolerName}:已按完全图完成链接",dbg=True)

    def groupBygroup(self):
        '''
        将其首尾分段相连A-B-C
        '''
        delog("我在完全图连接中",dbg=True)
        cidli = self.fdata["IdDescGroups"]
        placeholder = {"card_id": 0, "desc": ""}
        if len(cidli) < 2:
            showInfo("链接失败,组连接至少需要两个组!")
            return
        else:  # 说明groupSeperIdx 至少2个
            for i in range(0, len(cidli) - 1):  # 0,1,2起步
                liA = cidli[i]
                liB = cidli[i + 1]
                self.AmapB(liA, liB)
        delog(f"{consolerName}:已按组完成链接",dbg=True)

    def unlinkNode(self):
        idpli = self.fdata["IdDescPairs"]
        for idp in idpli:
            id = str(idp["card_id"])
            linkli = self.getCardIDfromNote(int(id))
            for link in linkli:
                note = self.getCardNoteFromId(int(link))  # 链到的卡片上找自己
                note.fields[self.fieldPosi] = self.delAnchor(id,note)
                # note.flush() 临时注释
                note = self.getCardNoteFromId(idp["card_id"])

                note.fields[self.fieldPosi] = self.delAnchor(link,note)
                # note.flush() 临时注释
        delog(f"{consolerName}:已按节点取消彼此链接",dbg=True)

    def unlinkPath(self):
        idpli = self.fdata["IdDescPairs"]
        for i in range(0, len(idpli) - 1):
            idA = idpli[i]["card_id"]
            idB = idpli[i + 1]["card_id"]
            noteA = self.getCardNoteFromId(idA)
            noteB = self.getCardNoteFromId(idB)
            noteB.fields[self.fieldPosi] = self.delAnchor(str(idA),noteB) #content
            # noteB.flush() 临时注释
            noteA.fields[self.fieldPosi] = self.delAnchor(str(idB),noteA)
            # noteA.flush() 临时注释
        delog(f"{consolerName}:已按路径取消路径节点上的彼此链接",dbg=True)




def setupFunction(browser:Browser=None,_from=None,mode=999,inputJSON=None):
    delog(f"setupFunction被启动,此时mode={mode}",dbg=True)
    input = os.path.join(THIS_FOLDER, inputFileName)
    cfg = os.path.join(THIS_FOLDER, configFileName)
    relycfg = os.path.join(RELY_FOLDER, relyLinkConfigFileName)
    try:
        browser.model.layoutChanged.emit()
    except:
        browser=dialogs.open("Browser",mw)
        browser.model.layoutChanged.emit()
    browser.maybeRefreshSidebar()
    browser.editor.setNote(None, hide=True)
    Linker = Link(input, cfg, relycfg, defaultMode=mode,_from=_from,inputJSON=inputJSON)
    tag=Linker.start()
    delog(f"{consolerName}:'操作完成',tag={tag}")
    # mw.onBrowse()
    browser.editor.setNote(None, hide=True) #用来刷新browser后避免编辑窗口中的数据滞后从而导致重新被修改.
    browser.model.layoutChanged.emit()
    browser.model.search(f"tag:{tag}")
    if isinstance(_from,AnkiWebView) and _from.title=="previewer":
        _from.parent().render_card()

def destroyFuntion():
    # fdata = open(os.path.join(THIS_FOLDER, inputFileName), "w", encoding="utf-8")
    json.dump(inputSchema,open(os.path.join(THIS_FOLDER, inputFileName), "w", encoding="utf-8"),
                  indent=4,
                  ensure_ascii=False)
    delog(f"{consolerName}:{inputFileName} '初始化完毕'")


def getCardDesc(card_id:int,confg:object)->str:
    """根据预设参数读取卡片的内容作为链接的描述字符串,如果读取失败,返回 读取描述字符失败"""
    note = mw.col.getCard(card_id).note()
    content = note.fields[confg["readDescFieldPosition"]]
    seRegx = confg["DEFAULT"]["regexForDescContent"] if confg["regexForDescContent"] == 0 else confg[
        "regexForDescContent"]
    try:
        Desc = re.search(seRegx, content)[0]#if desc == "" else desc  # 综上读取描述文字
    except:
        showInfo(f"{consolerName}:'正则读取描述字符失败!'")
        return "读取描述字符失败"
    return Desc[0:confg['descMaxLength'] if len(Desc)>confg['descMaxLength'] and confg['descMaxLength']!=0  else len(Desc)]

#multicopyFunction 和  singlecopyFunction 代码高度重叠,以后要统一 TODO
def multicopyFunction(self, groupCopy :bool = False,desc : str ="",clearInput :bool = False) -> None:
    if clearInput: destroyFuntion()
    cfgpath = os.path.join(THIS_FOLDER, configFileName)
    confg = json.load(open(cfgpath, "r", encoding="utf-8"))
    s = json.load(open(os.path.join(THIS_FOLDER, inputFileName), "r", encoding="utf-8"))
    group = []
    browser = self
    if len(browser.selectedCards()) == 0:
        showInfo("没有选中任何卡片!")
        return
    for card_id in browser.selectedCards():
        pair = {"card_id": card_id, "desc": getCardDesc(card_id,confg) }
        if groupCopy:
            group.append(pair)
        else:
            s["IdDescPairs"].append([pair])
    if len(group) > 0:
        s["IdDescPairs"].append(group)
    json.dump(s, open(os.path.join(THIS_FOLDER, inputFileName), "w", encoding="utf-8"), indent=4, ensure_ascii=False)
    delog(f"{consolerName}:"+str(len(browser.selectedCards())) + f" '张卡被加入到'input")


def singlecopyFunction(card_id : int,groupCopy :bool = False,desc : str = "",clearInput : bool = False) -> None:
    if clearInput:destroyFuntion()
    cfgpath = os.path.join(THIS_FOLDER, configFileName)
    confg = json.load(open(cfgpath, "r", encoding="utf-8"))
    s = json.load(open(os.path.join(THIS_FOLDER, inputFileName), "r", encoding="utf-8"))
    # showInfo(desc)
    desc1=desc if desc !="" else getCardDesc(card_id,confg)
    pair = {"card_id": card_id, "desc":desc1}
    delog(f"{consolerName}:card=" + str(card_id) + ",desc=" + desc)
    if groupCopy:
        try:
            s["IdDescPairs"][-1].append(pair)
        except:
            s["IdDescPairs"].append([pair])
        delog(f"{consolerName}: {json.dumps(pair, ensure_ascii=False)} '已经被插入到''上一个组'")
    else:
        s["IdDescPairs"].append([pair])
        delog(f"{consolerName}:"+json.dumps(pair, ensure_ascii=False) + f" '已经被插入到'input")
    json.dump(s, open(os.path.join(THIS_FOLDER, inputFileName), "w", encoding="utf-8"), indent=4, ensure_ascii=False)


def copyTagFromSelected(tag):
    s = json.load(open(os.path.join(THIS_FOLDER, inputFileName), "r", encoding="utf-8"))
    s["addTag"]=tag
    delog(f"{consolerName}:'标签'"+ "{"+f':"{tag}"' + "}"+f"'已经更新到'Input")
    json.dump(s, open(os.path.join(THIS_FOLDER, inputFileName), "w", encoding="utf-8"), indent=4, ensure_ascii=False)


def displayFunction(parent:QWidget=mw):
    try :
        Input=mw.InputDialog
        Input.activateWindow()
    except:
        Input=InputDialog()
        Input.exec()
        Input.activateWindow()



def configFunction():
    Url = QUrl.fromLocalFile("" + os.path.join(THIS_FOLDER, configFileName))
    QDesktopServices.openUrl(Url)


def helpFunction():
    Url = QUrl(helpSite)
    QDesktopServices.openUrl(Url)

def testFunction(browser: Browser):
    browser.model.search("1 -1")
    browser.editor.setNote(None)
def versionFunction():
    showInfo(hjp_bilink_VERSION)

def linkActionToMenu(Menu:QMenu,_from=None):
    def connectMenu(Menu:QMenu,desc:str,mode:int,_from=None,browser=browser):
        return Menu.addAction(desc).triggered.connect(lambda: setupFunction(browser=browser,mode=mode,_from=_from))
    list(map( lambda x,y:connectMenu(Menu,x,y,_from=_from), algPathDict["desc"],algPathDict["mode"]))

def appendActionToMenu(Menu:QMenu,selected="",card_id=0):
    Menu.addAction(f"'先清除再插入''插入'").triggered.connect(lambda _:singlecopyFunction(card_id,desc=selected,clearInput=True))
    Menu.addAction(f"'直接''插入'").triggered.connect(lambda _:singlecopyFunction(card_id,desc=selected))
    Menu.addAction(f"'插入''上一个组'").triggered.connect(lambda _:singlecopyFunction(card_id,desc=selected,groupCopy=True))
    Menu.addAction(f"'选中文字更新''标签'").triggered.connect(lambda _:copyTagFromSelected(selected))

def contexthelper(view:Union[AnkiWebView,None,Browser], menu:QMenu, selected="",card_id=None,need=["link","append","open","clear","browser"],prefix="hjp-bilink|"):
    if card_id == None:
        card_id=0
    AppendInputMenu = menu.addMenu(f"{prefix}'插入'input")
    if "append" in need:
        appendActionToMenu(AppendInputMenu,selected=selected,card_id=card_id)
    elif "browser" in need:
        AddToTableContextMenu(view,AppendInputMenu,prefix="")
    if "open" in need:
        menu.addAction(f"{prefix}'打开'input").triggered.connect(displayFunction)
    if "clear" in need:
        menu.addAction(f"{prefix}'清空'input").triggered.connect(destroyFuntion)
    if "link" in need:
        hjpBilinkLinkerMenu=menu.addMenu(prefix+"连接")
        linkActionToMenu(hjpBilinkLinkerMenu,_from=view)



def setUpBrowserMenuShortcut(browser:Browser):
    # 将参数命名为browser
    # browser = self
    '''
    #如果browser存在,直接让m读取menulinking属性,如果不存在,我们就自己创建一个
    函数用的是QMenu
    然后访问menubar也就是菜单栏,插入一个菜单.方法是insertmenu,参数是self.mw.form.menuTools.menuAction表示表单动作,
    menulinking就是刚建立的表单按钮,也就是Qmenu.
    '''
    try:
        m = browser.hjp_Link
    except:
        browser.hjp_Link = QMenu("hjp_link")
        browser.menuBar().insertMenu(browser.mw.form.menuTools.menuAction(), browser.hjp_Link)
        m = browser.hjp_Link
    # m1=m.addMenu("连接")
    # contexthelper
    contexthelper(browser,m,need=["browser","open","clear","link"],prefix="")
    m.addAction('调整config').triggered.connect(configFunction)
    m.addAction("查看版本").triggered.connect(versionFunction)
    m.addAction('打开插件页面').triggered.connect(helpFunction)


def AddToTableContextMenu(browser, menu,prefix="hjp|"):
    actionCopyCidAllWithClear = QAction(prefix+"先清除再将选中卡片插入",browser)
    actionCopyCidAllWithClear.triggered.connect(lambda _, b=browser: multicopyFunction(b,clearInput=True))
    menu.addAction(actionCopyCidAllWithClear)
    actionCopyCidAll = QAction(prefix+"将选中的卡片插入", browser)
    actionCopyCidAll.triggered.connect(lambda _, b=browser: multicopyFunction(b))
    menu.addAction(actionCopyCidAll)
    actionGroupCopy = QAction(prefix+"将选中的卡片编组插入", browser)
    actionGroupCopy.triggered.connect(lambda _, b=browser: multicopyFunction(b, groupCopy=True))
    menu.addAction(actionGroupCopy)

def AddToWebviewContextMenu(view:AnkiWebView, menu:QMenu):
    selected = view.page().selectedText()
    cid=0
    if view.title == "main webview" and mw.state=="review":
        cid=mw.reviewer.card.id
    elif view.title =="previewer":
        cid=view.parent().card().id #用parent访问上一层,那个插件和这个是一致的.
    if cid!=0:
        contexthelper(view, menu, selected=selected, card_id=cid)

def AddToEditorContextMenu(view:AnkiWebView,menu:QMenu):
    editor=view.editor
    selected: str = editor.web.selectedText()
    try:
        card_id=editor.card.id
        #delog(f"cardid={str(card_id)}")
    except:
        delog(f"{consolerName}:'由于这里无法读取card_id, 连接菜单不在这显示'")
        return
    contexthelper(view,menu,selected=selected,card_id=card_id,need=["append","open","clear"])



# gui_hooks.browser_menus_did_init.append(setUpBrowserMenuShortcut)
# gui_hooks.browser_will_show_context_menu.append(AddToTableContextMenu)
# gui_hooks.profile_will_close.append(destroyFuntion)
# gui_hooks.editor_will_show_context_menu.append(AddToEditorContextMenu)
# gui_hooks.webview_will_show_context_menu.append(AddToWebviewContextMenu)
delog("linker.py运行完",dbg=True)