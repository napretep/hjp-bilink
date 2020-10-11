import os,sys,time,json,re
# import win32.win32clipboard as clipboard 
# import the main window object (mw) from aqt
from aqt import mw,gui_hooks
from aqt.browser import Browser
from aqt.utils import showInfo,tooltip
from aqt.qt import *
from anki import hooks
import html
import time
from dataclasses import dataclass
from enum import Enum
from operator import itemgetter
from typing import Callable, List, Optional, Sequence, Tuple, Union
helpSite= "https://gitee.com/huangjipan/hjp-bilink"
inputFileName="test.txt"
configFileName="config.json"
helpFileName="README.md"
relyLinkDir="1423933177"
relyLinkConfigFileName="config.json"
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
PREV_FOLDER = os.path.dirname(THIS_FOLDER)
RELY_FOLDER = os.path.join(PREV_FOLDER,relyLinkDir)
errorType=[
    "card_id格式不正确","colSep分栏不正确","记录为空!"
]


class Link(object):
    def __init__(self,path,cfgpath,relycfgpath,prefix_cid="prefix_cid",defaultMode=999):
        self.path=path
        self.cfgpath=cfgpath
        self.confg=json.load(open(cfgpath,"r",encoding="utf-8"))
        self.relycfg=json.load(open(relycfgpath,"r",encoding="utf-8"))

        self.rowSep=self.confg["rowSeparator"]
        self.colSep=self.confg["colSeparator"]
        if defaultMode==999:
            self.mode=self.confg["linkMode"]  
        else:
            self.mode=defaultMode
        
        self.prefix=self.confg["cidPrefix"]
        self.fieldPosi=self.confg["appendNoteFieldPosition"]
        self.mapFuncPath=[
            self.completemap,
            self.groupBygroup
        ]
        if self.prefix != self.relycfg[prefix_cid]:
            self.relycfg[prefix_cid]=self.prefix
            json.dump(self.relycfg,open(relycfgpath,"w",encoding="utf-8"))

        with open(path,"r",encoding="utf-8") as fdata:
            fdata=fdata.read()
            fdata=re.sub(self.rowSep+self.rowSep+"{2,}",self.rowSep+self.rowSep,fdata)
            fdata=re.sub("^"+self.rowSep+"{1,}",'',fdata)
            fdata=re.sub(self.rowSep+"{1,}$",'',fdata)
            showInfo(fdata+",len="+str(len(fdata.split(self.rowSep))))
            self.fdata=fdata
            self.cidli=fdata.split(self.rowSep)

    def start(self):
        errorcode=self.safeCheck()
        if errorcode!=-1:
            showInfo(f"errorcode:{str(errorcode)}\n{errorType[errorcode]}")
            return
        showInfo("mode:"+str(int(self.mode))+",start")
        self.mapFuncPath[self.mode]()
        showInfo("finished!")

    def appendIDtoNote(self,note,content):
        '''
        note必须是一个cardnote,posi是一个cardnote的位置
        '''
        Id_DescribePair=content.split(self.colSep)
        Id=Id_DescribePair[0]
        Desc= Id_DescribePair[1] if len(Id_DescribePair)>1 else ''
        note.fields[self.fieldPosi]+=f"<div>{self.prefix}{Id} {Desc}</div>\n"
        note.flush()

    def AmapB(self,cidli):
        '''
        A位置的所有ID插入到B中,并作一个B的反向链接回A.
        TXT格式必须是AmapB起头,然后A位置输完要给一个换行符
        这个以后要大改.改好了
        '''
        fieldPosi=self.fieldPosi
        posi=0 #确定位置
        for cid in cidli:
            if cid == "":
                break
            posi += 1
        for BcardId in cidli[posi+1:]:
            Bnote=self.getCardNoteFromStr(BcardId)
            for AcardId in cidli[0:posi]:
                if re.search(AcardId,Bnote.fields[fieldPosi]) is None:
                #if not (AcardId in Bnote.fields[fieldPosi]):
                    self.appendIDtoNote(Bnote,AcardId)
                Anote=self.getCardNoteFromStr(AcardId)
                if re.search(BcardId,Anote.fields[fieldPosi]) is None:
                #if not (BcardId in Anote.fields[fieldPosi]):
                    self.appendIDtoNote(Anote,BcardId)              
    def completemap(self):
        '''
        完全图,没什么说的
        '''
        cidli=self.cidli
        fieldPosi=self.fieldPosi
        for cid in cidli:
            if cid=='':
                continue
            note=self.getCardNoteFromStr(cid)
            for linkcid in cidli:
                #怎样才能访问到fields,需要用数字下标,访问到的是HTML模式
                if cid != linkcid and (re.search(linkcid,note.fields[fieldPosi]) is None): #(linkcid  in note.fields[fieldPosi]):
                    self.appendIDtoNote(note,linkcid)       
    def safeCheck(self):
        #cardIDCheck
        countRowSep=0
        emptyposi=[]
        # if len(self.cidli)==1 and self.cidli[0]=='':
        #     return 2 #记录为空!
        for i in range(0,len(self.cidli)):
            cid=self.cidli[i]
            if cid=="":
                countRowSep+=1
                emptyposi.append(i)
                continue
            if not cid[0:13].isdigit():
                return 0#id格式不正确
            if len(cid.split(self.colSep))>2:
                return 1#记录分段格式不正确
        if countRowSep==len(self.cidli):
            return 2 #记录为空!
        return -1

    def groupBygroup(self):
        '''
        将其首尾分段相连A-B-C
        '''
        cidli=self.cidli
        groupidx=[]
        for idx in range(1, len(cidli)):
            if cidli[idx] == '':
                groupidx.append(idx)
            idx+=1
        if len(groupidx)<=1:
            self.AmapB(cidli)
        else:#说明groupidx 至少2个
            groupidx=[-1]+groupidx+[len(cidli)]# 至少4个
            liA=[]
            liB=[]
            for i in range(0,len(groupidx)-2):#0,1,2起步
                liA=cidli[groupidx[i]+1:groupidx[i+1]]
                liB=cidli[groupidx[i+1]+1:groupidx[i+2]]
                self.AmapB(liA+[""]+liB)
    def getCardNoteFromStr(self,li):
        '''
        li必须是开头含cardID的字符串
        '''
        return mw.col.getCard(int(li.split(self.colSep)[0])).note()        


def setupFunction(mode=999):
    txt=os.path.join(THIS_FOLDER,inputFileName)
    cfg=os.path.join(THIS_FOLDER,configFileName)
    relycfg=os.path.join(RELY_FOLDER,relyLinkConfigFileName)
    Linker=Link(txt,cfg,relycfg,defaultMode=mode)
    Linker.start()

def destroyFuntion():
    fdata=open(os.path.join(THIS_FOLDER,inputFileName),"w",encoding="utf-8")
    fdata.write("")
    fdata.close()
    showInfo("cleared")

def multicopyFunction(self):
    browser = self
    s=""
    if len(browser.selectedCards())==0:
        showInfo("nothing to copy!")
        return 
    for card_id in browser.selectedCards():#取出来的是id
        s+="\n"+str(card_id)
    fdata=open(os.path.join(THIS_FOLDER,inputFileName),"a",encoding="utf-8")
    fdata.write(s)
    fdata.close()
    showInfo(s[1:]+"\nhas been append to the txt file")

def displayFunction():
    Url=QUrl.fromLocalFile(""+os.path.join(THIS_FOLDER,inputFileName))
    QDesktopServices.openUrl(Url)
def configFunction():
    Url=QUrl.fromLocalFile(""+os.path.join(THIS_FOLDER,configFileName))
    QDesktopServices.openUrl(Url)
def helpFunction():
    #config=json.load(open(os.path.join(THIS_FOLDER,configFileName),"r",encoding="utf-8"))
    #Url=QUrl.fromLocalFile(""+os.path.join(THIS_FOLDER,helpFileName))
    Url=QUrl(helpSite)
    QDesktopServices.openUrl(Url)

menuActionCollect={}
menuToolsItems={
    'linkDefault':lambda m=999:setupFunction(mode=999),
    'linkAll':lambda m=0:setupFunction(mode=0),
    'linkGroupToGroup':lambda m=1:setupFunction(mode=1),
    'clear':destroyFuntion,
    'show':displayFunction,
    'config':configFunction,
    'help':helpFunction,
}

'''

'''
def linkActToMainMenu():
    '''
    将函数与钩子配对加到菜单里
    '''
    for name,action in  menuToolsItems.items():
        menuActionCollect[name]=QAction(name,mw)
        menuActionCollect[name].triggered.connect(action)
        mw.form.menuTools.addAction(menuActionCollect[name])
def setUpMenuShortcut(self):
    #将参数命名为browser
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
    for name,action in  menuToolsItems.items():
        menuActionCollect[name]=QAction(name,mw)
        menuActionCollect[name].triggered.connect(action)
        m.addAction(menuActionCollect[name])
def AddToTableContextMenu(browser,menu):
    actionCopyCidAll = QAction("hjpCopyCidAlltoTxt",browser)
    actionCopyCidAll.triggered.connect(lambda _, b=browser:multicopyFunction(b))
    menu.addAction(actionCopyCidAll)
gui_hooks.browser_menus_did_init.append(setUpMenuShortcut)
gui_hooks.browser_will_show_context_menu.append(AddToTableContextMenu)
#linkActToMainMenu()

