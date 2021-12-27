# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = '$NAME.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2021/7/30 9:09'
"""
import dataclasses
import logging
import shutil
import sys, platform, subprocess
import tempfile
from urllib.parse import quote

import uuid
from collections import Sequence
from datetime import datetime
import time
from math import ceil
from typing import Union, Optional, NewType, Callable, List, Iterable, Type, Any

from PyQt5.QtCore import pyqtSignal, QThread, QUrl, QTimer, Qt, QSettings, QMimeData, QRectF, QRect, QPointF
import json
import os
import re
from functools import reduce

from PyQt5.QtGui import QDesktopServices, QIcon
from PyQt5.QtWidgets import QApplication, QToolButton, QLineEdit, QInputDialog, QHBoxLayout, QPushButton, QWidget, \
    QGridLayout, QLabel, QSpinBox, QComboBox, QRadioButton, QDialog, QFormLayout, QTabWidget, QListWidget, QVBoxLayout, \
    QMessageBox, QTextEdit
from anki import stdmodels, notes
from anki.cards import Card
from anki.notes import Note
from anki.utils import pointVersion, isWin
from aqt import mw, dialogs, AnkiQt
from aqt.browser import Browser
from aqt.browser.previewer import BrowserPreviewer, Previewer, MultiCardPreviewer
from aqt.operations.card import set_card_deck
from aqt.reviewer import Reviewer, RefreshNeeded
from aqt.utils import showInfo, tooltip, tr
from aqt.webview import AnkiWebView
from bs4 import BeautifulSoup, element
from . import G, compatible_import
from .language import Translate,rosetta
from .objs import LinkDataPair, LinkDataJSONInfo
from ..bilink.dialogs.custom_cardwindow import SingleCardPreviewerMod
from .interfaces import ConfigInterface, AnswerInfoInterface, AutoReviewDictInterface, GViewData, GraphMode, \
    ConfigInterfaceItem

class MenuMaker:

    @staticmethod
    def gview_ankilink(menu,data):
        act = [Translate.文内链接, Translate.html链接, Translate.markdown链接, Translate.orgmode链接]
        f = [lambda: AnkiLinks.copy_gview_as(AnkiLinks.Type.inAnki, data),
             lambda: AnkiLinks.copy_gview_as(AnkiLinks.Type.html, data),
             lambda: AnkiLinks.copy_gview_as(AnkiLinks.Type.markdown, data),
             lambda: AnkiLinks.copy_gview_as(AnkiLinks.Type.orgmode, data), ]
        list(map(lambda x: menu.addAction(act[x]).triggered.connect(f[x]), range(len(f))))
        return menu

class GviewOperation:

    @staticmethod
    def save(data:GViewData=None,data_li:"Iterable[GViewData]"=None,exclude=None):
        """"""
        if data:
            prepare_data = data.to_DB_format()
            if exclude is not None:
                prepare_data.pop(exclude)
            with G.DB.go(G.DB.table_Gview) as DB:
                DB.replace(**prepare_data).commit(need_commit=False)

            return
        elif data_li:
            with G.DB.go(G.DB.table_Gview) as DB:
                for data in data_li:
                    prepare_data = data.to_DB_format()
                    if exclude is not None:
                        prepare_data.pop(exclude)
                    DB.replace(**prepare_data).commit(need_commit=False)
            return

    @staticmethod
    def exists(data:GViewData=None,name=None,uuid=None):
        DB = G.DB
        DB.go(DB.table_Gview)
        exists=False
        if data:
            exists=DB.exists(DB.EQ(uuid=data.uuid))
        elif name:
            exists=DB.exists(DB.EQ(name=name))
        elif uuid:
            exists = DB.exists(DB.EQ(uuid=uuid))
        DB.end()
        return exists
    @staticmethod
    def load(uuid=None,gviewdata:"GViewData"=None,pairli=None):
        """"""
        data = None
        if uuid is not None:
            DB=G.DB
            DB.go(DB.table_Gview)
            data1 = DB.select(DB.EQ(uuid=uuid)).return_all().zip_up().to_gview_data()[0]
            data = GViewData(uuid=data1.uuid, name=data1.name, nodes=json.loads(data1.nodes),
                             edges=json.loads(data1.edges))
        elif gviewdata is not None:
            with G.DB.go(G.DB.table_Gview) as DB:
                data1 = DB.select(DB.EQ(uuid=gviewdata.uuid)).return_all().zip_up().to_gview_data()[0]
            data = GViewData(uuid=data1.uuid, name=data1.name, nodes=json.loads(data1.nodes),
                             edges=json.loads(data1.edges))
        elif pairli is not None:
            data = GviewOperation.find_by_card(pairli)

        return data
    @staticmethod
    def load_all()->'List[GViewData]':
        DB=G.DB
        DB.go(DB.table_Gview)
        DB.excute_queue.append(DB.sqlstr_RECORD_SELECT_ALL.format(tablename=DB.tab_name))
        records = DB.return_all().zip_up().to_gview_data()
        return list(map(lambda data:GViewData(
                    uuid=data.uuid,name=data.name,nodes=json.loads(data.nodes),edges=json.loads(data.edges)) ,records))

    @staticmethod
    def find_by_card(pairli:'list[LinkDataPair]')->'set[GViewData]':
        """找到卡片所属的gview记录 """
        DB = G.DB
        DB.go(DB.table_Gview)

        def pair_to_gview(pair):
            card_id = pair.card_id
            datas = DB.select(DB.LIKE("nodes", f"%\"{card_id}\"%")).return_all().zip_up().to_gview_data()
            return set(map(
                lambda data:GViewData(
                    uuid=data.uuid,name=data.name,nodes=json.loads(data.nodes),edges=json.loads(data.edges)) ,datas))
        all_records = list(map(lambda x: pair_to_gview(x),pairli))
        final_givew = reduce(lambda x,y:x&y,all_records) if len(all_records)>0 else set()
        DB.end()
        return final_givew


    @staticmethod
    def update(data:GViewData):
        """"""
        DB = G.DB
        DB.go(DB.table_Gview)
        d = data.to_DB_format()
        d.pop("uuid")
        DB.update(values=DB.VALUEEQ(**d),where=DB.EQ(uuid=data.uuid)).commit()
            # name=d["name"],nodes=d["nodes"],edges=d["edges"]
        DB.end()

    @staticmethod
    def delete(uuid:str=None,uuid_li:"Iterable[str]"=None):
        """"""
        DB = G.DB
        DB.go(DB.table_Gview)
        if uuid:
            DB.delete(where=DB.VALUEEQ(uuid=uuid)).commit()
            DB.end()
            return
        elif uuid_li:
            for uuid in uuid_li:
                DB.delete(where=DB.VALUEEQ(uuid=uuid)).commit()
            DB.end()
            return
    @staticmethod
    def get_correct_input(placeholder=""):
        def view_name_check(name: str,placeholder="") -> bool:
            if name=="" or re.search(r"\s", name) or re.search("::::", name) \
                    or re.search("\s","".join(name.split("::"))) or "".join(name.split("::"))=="":
                tooltip(Translate.视图命名规则)
                return False
            if GviewOperation.exists(name=name):
                tooltip(Translate.视图名已存在)
                return False
            return True

        while True:
            viewName, submitted = QInputDialog.getText(None, "input", Translate.视图名, QLineEdit.Normal, placeholder)
            if not submitted:
                break
            if viewName == placeholder:
                submitted=False
                break
            if view_name_check(viewName,placeholder):
                break
        return (viewName, submitted)

    @staticmethod
    def create(nodes=None,edges=None,name=""):
        if name=="":
            name, submitted = GviewOperation.get_correct_input()
        else:
            submitted=True
        if not submitted: return
        uuid = UUID.by_random()
        data = GViewData(uuid, name, nodes, edges)
        # 去检查一下scene变大时,item的scene坐标是否会改变
        GviewOperation.save(data)
        Dialogs.open_grapher(gviewdata=data, mode=GraphMode.view_mode)


    @staticmethod
    def create_from_pair(pairs_li: 'list[G.objs.LinkDataPair]',name=""):
        nodes: "dict[str,list[Optional[float,int],Optional[float,int]]]" = {}
        list(map(lambda x: nodes.__setitem__(x.card_id, [None, None]), pairs_li))
        edges: "list[list[str,str]]" = []
        GviewOperation.create(nodes,edges,name=name)

    @staticmethod
    def insert(pairs_li: 'list[G.objs.LinkDataPair]'):
        all_gview = GviewOperation.load_all()
        check = {}
        list(map(lambda data: check.__setitem__(data.name,data),all_gview))
        # name_li = list()
        viewname, okPressed = QInputDialog.getItem(None, "Get gview", "", set(check.keys()), 0, False)
        if not okPressed:
            return
        Dialogs.open_grapher(pair_li=pairs_li,gviewdata=check[viewname], mode=GraphMode.view_mode)

class Utils(object):
    @dataclasses.dataclass
    class MenuType:
        ankilink=0

    @staticmethod
    def make_backup_file_name(filename,path=""):
        file = "backup_"+datetime.now().strftime("%Y%m%d%H%M%S")+"_"+os.path.split(filename)[-1]
        if not path:
            return os.path.join(*os.path.split(filename)[:-1],file)
        else:
            return os.path.join(path,file)

    @staticmethod
    def percent_calc(total,count,begin,ratio):
        return ceil(count/total*ratio)+begin

    @staticmethod
    def emptystr(s):
        return not re.match(r"\S",s)

    @staticmethod
    def tooltip(s):
        if G.ISDEBUG:
            tooltip(s)
    @staticmethod
    def showInfo(s):
        if G.ISDEBUG:
            showInfo(s)
    @staticmethod
    def rect_center_pos(rect:'Union[QRectF,QRect]'):
        return QPointF(rect.x()+rect.width()/2,rect.y()+rect.height()/2)

    @staticmethod
    def print(*args,need_timestamp=True, **kwargs):
        if G.ISDEBUG:
            if need_timestamp: print(datetime.now().strftime("%Y%m%d%H%M%S"))
            print(*args, **kwargs)

class AutoReview(object):
    """这是一套性能优化方案, AutoReview由于每次回答都要去数据库查询一遍,因此我们想了一招来更新缓存
    1,监听卡片的变化,
    """

    @staticmethod
    def begin():
        """入口,要从配置读东西,保存到某地,现在看来保存到G是最合适的,还需要设计数据结构"""
        if Config.get().auto_review.value==False:
            return
        AutoReview.build()
        G.AutoReview_timer.timeout.connect(AutoReview.update)
        G.AutoReview_timer.start(G.src.autoreview_update_interval)

    @staticmethod
    def build():
        G.AutoReview_dict = AutoReviewDictInterface()
        searchs:"list[str]" = Config.get().auto_review_search_string.value
        for search in searchs:
            if search == "" or not re.search(r"\S",search):
                continue
            for_due = "(is:new OR is:due)" if Config.get().auto_review_just_due_card.value else ""
            global_str = f"({Config.get().auto_review_global_condition.value})"
            cids = mw.col.find_cards(f"({search}) {for_due} {global_str if global_str!='()' else ''}")
            list(map(lambda cid: G.AutoReview_dict.card_group_insert(cid, search), cids))
            list(map(lambda cid: G.AutoReview_dict.search_group_insert(cid, search), cids))
        G.AutoReview_dict.build_union_search()
        G.AutoReview_dict.update_version()

    @staticmethod
    def update():
        """从配置表加载查询条件,然后去搜索,组织,并更新到数据库
        这个函数需要定期执行,要给一些优化,
        这里是重点对象, 首先执行一次联合查询, 然后检查原本在的是否消失, 原本不在的是否新增
        https://blog.csdn.net/qq_34130509/article/details/89473503
        """
        if Config.get().auto_review.value==False:
            return
        def search_result_not_changed():
            """在这里,我们检查有没有必要更新"""
            new_cids = set(mw.col.find_cards(G.AutoReview_dict.union_search))
            old_cids = G.AutoReview_dict.card_group.keys()
            need_add_card = new_cids - old_cids
            need_del_card = old_cids - new_cids
            return len(need_add_card)==0 and len(need_del_card)==0
        #临时文件没有变化则退出
        if len(G.AutoReview_tempfile) == 0:
            return
        #临时文件有变化,且临时文件cid不属于集合,则检查原集合是否有改动,无改动则退出
        not_belong_to_card_group = len(G.AutoReview_tempfile & G.AutoReview_dict.card_group.keys())==0
        if not_belong_to_card_group and search_result_not_changed():
            G.AutoReview_tempfile.clear()
            return
        #其他的筛选条件太难选了.到这里就直接建立吧
        AutoReview.build()
        G.AutoReview_tempfile.clear()

    @staticmethod
    def modified_card_record(note:Note):
        """将卡片写到一个全局变量,作为集合"""
        if Config.get().auto_review.value==False:
            return
        G.AutoReview_tempfile|=set(note.card_ids())


    @staticmethod
    def save_search_to_config(browser:Browser):
        """把搜索栏的内容拷贝下来粘贴到配置表"""
        c=Config.get()
        curr_string = browser.form.searchEdit.currentText()
        if curr_string=="" or not re.search(r"\S",curr_string):
            tooltip("不接受空格与空值<br>null string or empty string is not allowed")
            return
        setv = set(c.auto_review_search_string.value)
        setv.add(curr_string)
        c.auto_review_search_string.value = list(setv)
        Config.save(c)
        G.signals.on_auto_review_search_string_changed.emit()


class HTMLOperation:

    pass


class Config:

    @staticmethod
    def read(cfg:ConfigInterface, data: "dict"):
        for key, value in data.items():
            if key in cfg.get_editable_config():
                item: "ConfigInterfaceItem" = cfg[key]
                # if not validate_dict[item.component](value,item):
                if not Config.get_validate(item)(value,item):
                    showInfo(f"{key}={value}<br>is invalid, overwritten")
                    # write_to_log_file(f"{key}={value}\n"+str(Config.get_validate(item)(value,item)),need_timestamp=True)
                    continue
                cfg[key].value = value

    @staticmethod
    def get_validate(item:"ConfigInterfaceItem"):

        w = ConfigInterface.Widget
        d={ #不写在这的必须要有自己的validate
            w.spin:lambda x,item: type(x) == int and  item.limit[0]<=x<=item.limit[1],
            w.radio:lambda x,item: type(x) == bool,
            w.line:lambda x,item: type(x)==str,
            w.label:lambda x,item: type(x)==str,
            w.text:lambda x,item: type(x)==str,
            w.combo:lambda x,item:x in item.limit,
        }

        if item.validate(item.value,item) is None:
            # write_to_log_file(str(item.validate(item.value, item)))
            return d[item.component]
        else:
            return item.validate

    @staticmethod
    def get() -> ConfigInterface:
        """静态方法,直接调用即可"""
        if G.CONFIG is None:
            template = ConfigInterface()
            if os.path.exists(G.src.path.userconfig):
                file_str = open(G.src.path.userconfig, "r", encoding="utf-8").read()
            else:
                file_str = template.to_json_string()
            try:
                data = json.loads(file_str)
                Config.read(template,data)
                G.CONFIG=template
            except:
                backfile = Utils.make_backup_file_name(G.src.path.userconfig)
                if os.path.exists(G.src.path.userconfig):
                    shutil.copy(G.src.path.userconfig,backfile)
                    showInfo(f"config file load failed, backup and overwrite")
                Config.save(template)

        return G.CONFIG

    @staticmethod
    def save(config: ConfigInterface=None,path=None):
        # showInfo("Config.save")
        if path is None: path = G.src.path.userconfig
        if config is None:config = ConfigInterface()
        template = ConfigInterface()
        Config.read(template,config.get_dict())
        template.save_to_file(path)
        G.CONFIG = template

    @staticmethod
    def make_widget(configitem:"ConfigInterfaceItem"):
        value, validate, widgetType = configitem.value,configitem.validate,configitem.component
        typ = ConfigInterface.Widget
        tipbutton = QToolButton()
        tipbutton.setIcon(QIcon(G.src.ImgDir.help))
        tipbutton.clicked.connect(lambda:tooltip("<br>".join(configitem.instruction),period=7000))
        container = QWidget()
        layout = QHBoxLayout()
        w=None
        if widgetType == typ.spin:
            w=QSpinBox(container)
            w.setRange(configitem.limit[0],configitem.limit[1])
            w.setValue(value)
            w.valueChanged.connect(lambda x:configitem.setValue(x))
        elif widgetType == typ.line:
            w=QLineEdit()
            w.setText(value)
            w.textChanged.connect(lambda :configitem.setValue(w.text()))
        elif widgetType == typ.combo:
            w=QComboBox(container)
            list(map(lambda x:w.addItem(x.name,x.value),configitem.limit))
            w.setCurrentIndex(w.findData(value))
            w.currentIndexChanged.connect(lambda x:configitem.setValue(w.currentData(role=Qt.UserRole)) )
        elif widgetType == typ.radio:
            w=QRadioButton(container)
            w.setChecked(value)
            w.clicked.connect(lambda:configitem.setValue(w.isChecked()))
        elif widgetType == typ.list:
            w=Config.List(configitem)
        elif widgetType == typ.label:
            w=QLabel(container)
            w.setText(configitem.display(value))
        elif widgetType == typ.text:
            w=QTextEdit(container)
            w.setContentsMargins(0,0,0,0)
            w.setText(value)
        if w==None:return False
        layout.addWidget(w)
        layout.addWidget(tipbutton)
        container.setLayout(layout)
        return container

    class List(QWidget):
        def __init__(self,configitem:"ConfigInterfaceItem"):
            super().__init__()
            self.item = configitem
            self.list = QListWidget(self)
            self.G_Layout=QGridLayout()
            self.add_button = QToolButton(self)
            self.del_button = QToolButton(self)
            self.init_UI()
            self.init_data()
            self.all_event=G.objs.AllEventAdmin([
                [self.add_button.clicked,self.on_add_button_clicked_handle],
                [self.del_button.clicked,self.on_del_button_clicked_handle]
            ]).bind()

        def on_add_button_clicked_handle(self):
            while True:
                value,submitted = QInputDialog.getText(self, "input", "", QLineEdit.Normal, "")
                if not submitted:
                    return
                if not Config.get_validate(self.item)(value):
                    tooltip("invalid input")
                else:
                    self.item.value.append(value)
                    self.init_data()
                    break
            G.signals.on_auto_review_search_string_changed.emit()

        def on_del_button_clicked_handle(self):
            idx = self.list.selectedIndexes()
            if not idx:
                return
            item = self.list.itemFromIndex(idx[0])
            self.item.value.remove(item.text())
            self.init_data()
            G.signals.on_auto_review_search_string_changed.emit()

        def init_UI(self):
            # self.setMaximumHeight(300)
            self.setMinimumHeight(100)
            self.list.setMaximumHeight(300)
            V_layout=QVBoxLayout()
            self.add_button.setIcon(QIcon(G.src.ImgDir.item_plus))
            self.del_button.setIcon(QIcon(G.src.ImgDir.delete))
            V_layout.addWidget(self.add_button)
            V_layout.addWidget(self.del_button)
            self.G_Layout.addWidget(self.list,0,0,5,1)
            self.G_Layout.addLayout(V_layout,0,1,1,1,alignment=Qt.AlignTop)
            # self.G_Layout.addWidget(self.add_button,0,1,1,1,alignment=Qt.AlignTop)
            # self.G_Layout.addWidget(self.del_button,1,1,1,1,alignment=Qt.AlignTop)
            self.G_Layout.setContentsMargins(0,0,0,0)
            self.list.setContentsMargins(0,0,0,0)
            self.setLayout(self.G_Layout)
            pass

        def init_data(self):
            self.list.clear()
            for data in self.item.value:
                if re.search("\S",data):
                    self.list.addItem(data)
            pass

        def init_events(self):

            pass

    # class TextPicker(QWidget):
    #     def __init__(self,item:ConfigInterfaceItem):
    #         super().__init__()
    #         self.item = item
    #         self.button=QToolButton()
    #         self.label=QLabel


class GrapherOperation:
    @staticmethod
    def refresh():
        from ..bilink.dialogs.linkdata_grapher import Grapher
        if isinstance(G.mw_grapher, Grapher):
            G.mw_grapher.on_card_updated.emit(None)


class LinkDataOperation:
    """针对链接数据库的操作,
    这里的LinkDataOperation.bind/unbind和LinkPoolOperation中的link/unlink是类似但不同,不冲突.
    因为那是一个link池里的操作,而这不是, 这是一个普通的链接操作
    """
    @staticmethod
    def read(card_id):
        from ..bilink.linkdata_admin import read_card_link_info
        return read_card_link_info(card_id)

    @staticmethod
    def write(card_id, data):
        from ..bilink.linkdata_admin import write_card_link_info
        return write_card_link_info(card_id, data)

    @staticmethod
    def bind(card_idA:'Union[str,LinkDataJSONInfo]', card_idB:'Union[str,LinkDataJSONInfo]', needsave=True):
        """needsave关闭后,需要自己进行save"""
        if isinstance(card_idA,LinkDataJSONInfo) and isinstance(card_idB,LinkDataJSONInfo):
            cardA,cardB = card_idA,card_idB
        else:
            from ..bilink import linkdata_admin
            cardA = linkdata_admin.read_card_link_info(card_idA)
            cardB = linkdata_admin.read_card_link_info(card_idB)
        if cardB.self_data not in cardA.link_list:
            cardA.append_link(cardB.self_data)
            if needsave: cardA.save_to_DB()
        if cardA.self_data not in cardB.link_list:
            cardB.append_link(cardA.self_data)
            if needsave: cardB.save_to_DB()

    @staticmethod
    def unbind(card_idA:'Union[str,LinkDataJSONInfo]', card_idB:'Union[str,LinkDataJSONInfo]', needsave=True):
        """needsave关闭后,需要自己进行save"""
        if isinstance(card_idA,LinkDataJSONInfo) and isinstance(card_idB,LinkDataJSONInfo):
            cardA,cardB = card_idA,card_idB
        else:
            from ..bilink import linkdata_admin
            cardA = linkdata_admin.read_card_link_info(card_idA)
            cardB = linkdata_admin.read_card_link_info(card_idB)
        if cardB.self_data in cardA.link_list:
            cardA.remove_link(cardB.self_data)
            if needsave: cardA.save_to_DB()
        if cardA.self_data in cardB.link_list:
            cardB.remove_link(cardA.self_data)
            if needsave: cardB.save_to_DB()

    @staticmethod
    def backup(cfg:"ConfigInterface",now=None):
        if not now:now=datetime.now().timestamp()
        db_file = G.src.path.DB_file
        path = cfg.auto_backup_path.value
        backup_name = Utils.make_backup_file_name(db_file, path)
        shutil.copy(db_file, backup_name)
        cfg.last_backup_time.value = now
        cfg.save_to_file(G.src.path.userconfig)

    @staticmethod
    def need_backup(cfg:"ConfigInterface",now)->bool:
        if not cfg.auto_backup.value:
            return False
        last = cfg.last_backup_time.value
        if (now - last) / 3600 < cfg.auto_backup_interval.value:
            return False
        return True

class Compatible:
    @staticmethod
    def CardId():
        if pointVersion() < 45:
            CardId = NewType("CardId", int)
            return CardId
        else:
            from anki.cards import CardId
            return CardId

    @staticmethod
    def NoteId():
        if pointVersion() < 45:
            NoteId = NewType("NoteId", int)
            return NoteId
        else:
            from anki.notes import NoteId
            return NoteId

    @staticmethod
    def DeckId():
        if pointVersion() < 45:
            DeckId = NewType("DeckId", int)
            return DeckId
        else:
            from anki.decks import DeckId
            return DeckId

    @staticmethod
    def BrowserPreviewer():
        if pointVersion() < 45:
            DeckId = NewType("DeckId", int)
            return DeckId
        else:
            from anki.decks import DeckId
            return DeckId


class BrowserOperation:
    @staticmethod
    def search(s) -> Browser:
        """注意,如果你是自动搜索,需要自己激活窗口"""
        browser: Browser = BrowserOperation.get_browser()
        # if browser is not None:
        if not isinstance(browser, Browser):
            browser: Browser = dialogs.open("Browser", mw)

        browser.search_for(s)
        return browser

    @staticmethod
    def refresh():
        browser: Browser = BrowserOperation.get_browser()
        if isinstance(browser, Browser):
            # if dialogs._dialogs["Browser"][1] is not None:
            browser.sidebar.refresh()
            browser.model.reset()
            browser.editor.setNote(None)

    @staticmethod
    def get_browser(OPEN=False):
        browser: Browser = dialogs._dialogs["Browser"][1]
        if not isinstance(browser, Browser) and OPEN:
            browser = dialogs.open("Browser")
        return browser

    @staticmethod
    def get_selected_card():
        browser = BrowserOperation.get_browser(OPEN=True)
        card_ids = browser.selected_cards()
        result = [ LinkDataPair(str(card_id),CardOperation.desc_extract(card_id)) for card_id in card_ids ]
        return result

class CustomProtocol:
    # 自定义url协议,其他的都是固定的,需要获取anki的安装路径

    @staticmethod
    def set():
        root = QSettings("HKEY_CLASSES_ROOT", QSettings.NativeFormat)
        root.beginGroup("ankilink")
        root.setValue("Default", "URL:Ankilink")
        root.setValue("URL Protocol", "")
        root.endGroup()
        command = QSettings(r"HKEY_CLASSES_ROOT\anki.ankiaddon\shell\open\command", QSettings.NativeFormat)
        shell_open_command = QSettings(r"HKEY_CLASSES_ROOT\ankilink\shell\open\command", QSettings.NativeFormat)
        shell_open_command.setValue(r"Default", command.value("Default"))

    @staticmethod
    def exists():
        setting = QSettings(r"HKEY_CLASSES_ROOT\ankilink", QSettings.NativeFormat)
        return len(setting.childGroups()) > 0


class CardOperation:

    @staticmethod
    def auto_review(answer:AnswerInfoInterface):
        """用来同步复习卡片"""

        if Config.get().auto_review.value==0:
            return
        if answer.card_id not in G.AutoReview_dict.card_group:
            return
        if Config.get().auto_review_comfirm_dialog.value:
            go_on = QMessageBox.information(None,"auto_review",Translate.自动复习提示,QMessageBox.Yes|QMessageBox.No)
            if go_on == QMessageBox.No:
                return
        searchs = G.AutoReview_dict.card_group[answer.card_id]

        sched = compatible_import.mw.col.sched
        reportstring = ""
        for search in searchs:
            cids = G.AutoReview_dict.search_group[search]
            for cid in cids:
                card = mw.col.get_card(CardId(cid))
                button_num = sched.answerButtons(card)
                ease = answer.option_num if button_num>=answer.option_num else button_num
                if card.timer_started is None: card.timer_started = time.time() - 60
                CardOperation.answer_card(card,ease)
                reportstring += str(cid) + ":" + CardOperation.desc_extract(cid) + "<br>"
        mw.col.reset()
        reportstring+="以上卡片已经同步复习<br>cards above has beend sync reviewed"
        tooltip(reportstring,period=5000)


    @staticmethod
    def answer_card(card,ease):
        sched = mw.col.sched
        while True:
            try:
                sched.answerCard(card, ease)
                break
            except:
                time.sleep(0.2)
                continue


    @staticmethod
    def create(model_id: "int" = None, deck_id: "int" = None, failed_callback: "Callable" = None):
        if model_id is not None and not (type(model_id)) == int:
            model_id = int(model_id)
        if deck_id is not None and not (type(deck_id)) == int:
            deck_id = int(deck_id)

        if model_id is None:
            if not "Basic" in mw.col.models.allNames():
                # mw.col.models.add(stdmodels.addBasicModel(mw.col))
                material = json.load(open(G.src.path.card_model_template, "r", encoding="utf-8"))
                new_model = mw.col.models.new("Basic")
                new_model["flds"] = material["flds"]
                new_model["tmpls"] = material["tmpls"]
                mw.col.models.add(new_model)
            model = mw.col.models.by_name("Basic")
        else:
            if mw.col.models.have(model_id):
                model = mw.col.models.get(model_id)
            else:
                tooltip(f"modelId don't exist:{model_id}")
                if failed_callback:
                    failed_callback()

        note = notes.Note(mw.col, model=model)
        if deck_id is None:
            deck_id = mw.col.decks.current()["id"]
        else:
            if not mw.col.decks.have(deck_id):
                tooltip(f"deck_id don't exist:{deck_id}")
        mw.col.add_note(note, deck_id=deck_id)
        note.flush()
        return str(note.card_ids()[0])

    @staticmethod
    def clipbox_insert_field(clipuuid, timestamp=None):
        """用于插入clipbox到指定的卡片字段,如果这个字段存在这个clipbox则不做操作"""
        if platform.system() in {"Darwin", "Linux"}:
            tooltip("当前系统暂时不支持该功能\n current os not supports the feature")
            return
        else:
            from ..clipper2.exports import fitz

        def bookmark_to_tag(bookmark: "list[list[int,str,int]]"):
            tag_dict = {}
            if len(bookmark) == 0:
                return tag_dict
            level, content, pagenum = bookmark[0][0], bookmark[0][1], bookmark[0][2]
            tag_dict[pagenum] = re.sub(r"\s|\r|\n", "-", content)
            level_stack = []
            level_stack.append([level, content, pagenum])
            for item in bookmark[1:]:
                level, content, pagenum = item[0], re.sub(r"\s|\r|\n", "-", item[1]), item[2]
                if level == 1:
                    tag_dict[pagenum] = content
                else:
                    while len(level_stack) != 0 and level_stack[-1][0] >= level:
                        level_stack.pop()
                    content = f"{level_stack[-1][1]}::{content}"
                    tag_dict[pagenum] = content
                level_stack.append([level, content, pagenum])
            return tag_dict

        DB = G.DB
        DB.go(DB.table_clipbox)
        clipbox_ = DB.select(uuid=clipuuid).return_all().zip_up()[0]
        clipbox = G.objs.ClipboxRecord(**clipbox_)
        DB.end()
        DB.go(DB.table_pdfinfo)
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        card_id_li = clipbox.card_id.split(",")
        for card_id in card_id_li:
            if not card_id.isdigit():
                continue
            pdfinfo_ = DB.select(uuid=clipbox.pdfuuid).return_all().zip_up()[0]
            pdfinfo = G.objs.PDFinfoRecord(**pdfinfo_)
            pdfname = os.path.basename(pdfinfo.pdf_path)
            pdfname_in_tag = re.sub(r"\s|\r|\n", "-", pdfname[0:-4])
            note = mw.col.getCard(CardId(int(card_id))).note()
            html = reduce(lambda x, y: x + "\n" + y, note.fields)
            if clipbox.uuid not in html:
                note.fields[clipbox.QA] += \
                    f"""<img class="hjp_clipper_clipbox" src="hjp_clipper_{clipbox.uuid}_.png"><br>\n"""
            if clipbox.comment != "" and clipbox.uuid not in html:
                note.fields[clipbox.commentQA] += \
                    f"""<p class="hjp_clipper_clipbox text" id="{clipbox.uuid}">{clipbox.comment}</p>\n"""

            note.addTag(f"""hjp-bilink::timestamp::{timestamp}""")
            # print(f"in the loop, timestamp={timestamp}")
            note.addTag(f"""hjp-bilink::books::{pdfname_in_tag}::page::{clipbox.pagenum}""")
            doc: "fitz.Document" = fitz.open(pdfinfo.pdf_path)
            toc = doc.get_toc()
            if len(toc) > 0:
                # 读取缓存的书签
                jsonfilename = os.path.join(tempfile.gettempdir(),
                                            UUID.by_hash(pdfinfo.pdf_path) + ".json")
                if os.path.exists(jsonfilename):  # 存在直接读
                    bookdict = json.loads(open(jsonfilename, "r", encoding="utf-8").read())
                else:  # 不存在则新建
                    bookdict = bookmark_to_tag(toc)
                    json.dump(bookdict, open(jsonfilename, "w", encoding="utf-8"), indent=4, ensure_ascii=False)
                pagelist = sorted(list(bookdict.keys()), key=lambda x: int(x))  # 根据bookdict的键名(页码)进行排序

                atbookmark = -1
                for idx in range(len(pagelist)):
                    # 这里是在选择card所在的页码插入到合适的标签之间的位置,比如标签A在36页,标签B在38页, card指向37页,那么保存在标签A中.
                    #
                    if int(pagelist[idx]) > clipbox.pagenum:
                        if idx > 0:
                            atbookmark = pagelist[idx - 1]
                        break
                if atbookmark != -1:
                    note.addTag(f"""hjp-bilink::books::{pdfname_in_tag}::bookmark::{bookdict[atbookmark]}""")
            note.flush()
        DB.end()

    @staticmethod
    def refresh():
        def prev_refresh(p: Previewer):
            # return False
            """在被包裹的函数执行完后刷新"""
            _last_state = p._last_state
            _card_changed = p._card_changed
            p._last_state = None
            p._card_changed = True
            p._render_scheduled()
            p._last_state = _last_state
            p._card_changed = _card_changed

        browser: Browser = BrowserOperation.get_browser()
        if browser is not None and browser._previewer is not None:
            prev_refresh(browser._previewer)
        if mw.state == "review":
            mw.reviewer._refresh_needed = RefreshNeeded.NOTE_TEXT
            mw.reviewer.refresh_if_needed()  # 这个功能时好时坏,没法判断.
        for k, v in G.mw_card_window.items():
            if v is not None:
                prev_refresh(v)
        QTimer.singleShot(2000, lambda: tooltip("anki的自动刷新功能还存在问题,如果出现显示空白,请手动重新加载卡片"))

    @staticmethod
    def exists(id):
        return card_exists(id)

    @staticmethod
    def note_get(id):
        return note_get(id)

    @staticmethod
    def desc_extract(card_id, fromField=False):
        """读取逻辑, 默认从数据库读取,除非强制 fromField=True"""
        return desc_extract(card_id, fromField)

    @staticmethod
    def get_correct_id(card_id):
        from . import objs
        if isinstance(card_id, objs.LinkDataPair):  # 有可能把pair传进来的
            cid = card_id.int_card_id
        elif isinstance(card_id,Card):
            cid=card_id.id
        elif isinstance(card_id, str):
            cid = int(card_id)
        elif type(card_id) == int:
            cid = card_id
        else:
            raise TypeError("参数类型不支持:" + card_id.__str__())
        return cid

class Media:
    @staticmethod
    def clipbox_png_save(clipuuid):
        if platform.system() in {"Darwin", "Linux"}:
            tooltip("当前系统暂时不支持该功能")
            return
        else:
            from ..clipper2.exports import fitz
        mediafolder = os.path.join(mw.pm.profileFolder(), "collection.media")
        DB = G.DB
        clipbox_ = DB.go(DB.table_clipbox).select(uuid=clipuuid).return_all().zip_up()[0]
        clipbox = G.objs.ClipboxRecord(**clipbox_)
        DB.end()
        pdfinfo_ = DB.go(DB.table_pdfinfo).select(uuid=clipbox.pdfuuid).return_all().zip_up()[0]
        pdfinfo = G.objs.PDFinfoRecord(**pdfinfo_)
        DB.end()
        doc: "fitz.Document" = fitz.open(pdfinfo.pdf_path)
        # 0.144295302 0.567695962 0.5033557047 0.1187648456
        page = doc.load_page(clipbox.pagenum)
        pagerect: "fitz.rect_like" = page.rect
        x0, y0 = clipbox.x * pagerect.width, clipbox.y * pagerect.height
        x1, y1 = x0 + clipbox.w * pagerect.width, y0 + clipbox.h * pagerect.height
        pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2),
                                 clip=fitz.Rect(x0, y0, x1, y1))
        pngdir = os.path.join(mediafolder, f"""hjp_clipper_{clipbox.uuid}_.png""")
        write_to_log_file(pngdir + "\n" + f"w={pixmap.width} h={pixmap.height}")
        if os.path.exists(pngdir):
            # showInfo("截图已更新")
            os.remove(pngdir)
        pixmap.save(pngdir)


class LinkPoolOperation:
    """针对链接池设计"""
    class M:
        """各种状态选择"""
        before_clean = 0
        directly = 1
        by_group = 2
        complete_map = 3
        group_by_group = 4
        unlink_by_path = 5
        unlink_by_node = 6

    @staticmethod
    def both_refresh(*args):
        """0,1,2 可选刷新"""
        o = [CardOperation, BrowserOperation, GrapherOperation]
        if len(args) > 0:
            for i in args:
                o[i].refresh()
        else:
            for Op in o:
                Op.refresh()

    @staticmethod
    def get_template():
        d = {"IdDescPairs": [], "addTag": ""}
        return d

    @staticmethod
    def read():
        d = json.load(open(G.src.path.linkpool_file, "r", encoding="utf-8"))
        x = G.objs.LinkPoolModel(fromjson=d)
        return x

    @staticmethod
    def insert(pair_li: "list[G.objs.LinkDataPair]"=None, mode=1, need_show=True,FROM=None):
        if FROM==DataFROM.shortCut:
            pair_li = BrowserOperation.get_selected_card()
            if len(pair_li)==0:
                tooltip(Translate.请选择卡片)
                return
            mode = Config.get().default_insert_mode.value
        L = LinkPoolOperation
        if mode == L.M.before_clean:
            L.clear()
            d = L.read()
            d.IdDescPairs = [[pair] for pair in pair_li]
        elif mode == L.M.directly:
            d = L.read()
            d.IdDescPairs += [[pair] for pair in pair_li]
        elif mode == L.M.by_group:
            d = L.read()
            d.IdDescPairs += [[pair for pair in pair_li]]
        else:
            raise TypeError("不支持的操作")
        L.write(d.todict())
        from ..bilink.dialogs.linkpool import LinkPoolDialog
        if need_show:
            if isinstance(G.mw_linkpool_window, LinkPoolDialog):
                G.mw_linkpool_window.activateWindow()
            else:
                G.mw_linkpool_window = LinkPoolDialog()
                G.mw_linkpool_window.show()

    @staticmethod
    def clear():
        d = LinkPoolOperation.get_template()
        LinkPoolOperation.write(d)
        return LinkPoolOperation

    @staticmethod
    def write(d: "dict"):
        json.dump(d, open(G.src.path.linkpool_file, "w", encoding="utf-8"))
        return LinkPoolOperation

    @staticmethod
    def exists():
        return os.path.exists(G.src.path.linkpool_file)

    @staticmethod
    def link(mode=4, pair_li: "Optional[list[G.objs.LinkDataPair]]" = None,FROM=None):
        if FROM==DataFROM.shortCut:
            pair_li = BrowserOperation.get_selected_card()
            if len(pair_li)==0:
                tooltip(Translate.请选择卡片)
                return
            mode = Config.get().default_link_mode.value
        def on_quit_handle(timestamp):
            cfg = Config.get()
            if cfg.open_browser_after_link.value==1:
                if cfg.add_link_tag.value==1:
                    BrowserOperation.search(f"""tag:hjp-bilink::timestamp::{timestamp}""").activateWindow()
                else:
                    s=""
                    for pair in pair_li:
                        s+=f"cid:{pair.card_id} or "
                    BrowserOperation.search(s[0:-4]).activateWindow()
            G.mw_progresser.close()
            G.mw_universal_worker.allevent.unbind()
            LinkPoolOperation.both_refresh()

        from . import widgets
        if pair_li is not None:
            LinkPoolOperation.insert(pair_li, mode=LinkPoolOperation.M.before_clean, need_show=False)
        G.mw_progresser = widgets.UniversalProgresser() #实例化一个进度条
        G.mw_universal_worker = LinkPoolOperation.LinkWorker(mode=mode) #实例化一个子线程
        G.mw_universal_worker.allevent = G.objs.AllEventAdmin([ #给子线程的不同情况提供回调函数
            [G.mw_universal_worker.on_quit, on_quit_handle], #完成时回调
            [G.mw_universal_worker.on_progress, G.mw_progresser.value_set], #进度回调
        ]).bind()
        G.mw_universal_worker.start()

    @staticmethod
    def unlink(mode=6, pair_li: "Optional[list[G.objs.LinkDataPair]]" = None,FROM=None):
        if FROM==DataFROM.shortCut:
            pair_li = BrowserOperation.get_selected_card()
            if len(pair_li)==0:
                tooltip(Translate.请选择卡片)
                return
            mode=Config.get().default_unlink_mode.value
        LinkPoolOperation.link(mode=mode, pair_li=pair_li)


    class LinkWorker(QThread):
        on_progress = pyqtSignal(object)
        on_quit = pyqtSignal(object)

        def __init__(self, mode=3):
            super().__init__()

            self.waitting = False
            self.timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            self.allevent: 'Optional[G.objs.AllEventAdmin]' = None
            self.timegap = 0.1
            self.mode = mode

        def run(self):
            from ..bilink import linkdata_admin
            L = LinkPoolOperation
            d = L.read()
            cfg = Config.get()
            linkdatali = d.tolinkdata()
            flatten:"list[LinkDataJSONInfo]"= reduce(lambda x,y:x+y,linkdatali,[])
            total,count = len(flatten),0

            #先加tag

            for pair in flatten:
                pair.add_tag(d.addTag)
                if cfg.add_link_tag.value:
                    pair.add_timestamp_tag(self.timestamp)
                count+=1
                self.on_progress.emit(Utils.percent_calc(total,count,0,25))

            #根据不同的模式进行不同的操作
            if self.mode in {L.M.complete_map,L.M.unlink_by_node}:
                total, count = len(flatten), 0
                for linkinfoA in flatten:
                    total2, count2 = len(flatten), 0
                    for linkinfoB in flatten:
                        if linkinfoB.self_data.card_id!=linkinfoA.self_data.card_id:
                            if self.mode == L.M.complete_map:
                                LinkDataOperation.bind(linkinfoA,linkinfoB,needsave=False)
                            elif self.mode == L.M.unlink_by_node:
                                LinkDataOperation.unbind(linkinfoA,linkinfoB,needsave=False)
                        count2 += 1
                        self.on_progress.emit(Utils.percent_calc(total,(count2 / total2 + count),25,50))
                    count += 1
            elif self.mode in (L.M.group_by_group, L.M.unlink_by_path):
                total, count = len(linkdatali), 0
                r = self.reducer(count, total, self, d)
                reduce(r.reduce_link, linkdatali)
            total, count = len(flatten), 0

            with G.DB.go(G.DB.table_linkinfo) as DB:

                for linkinfo in flatten:
                    temp  = linkinfo.to_DB_record
                    card_id, data = temp["card_id"],temp["data"]
                    DB.replace(card_id=card_id, data=data).commit(need_commit=False)
                    count+=1
                    self.on_progress.emit(Utils.percent_calc(total,count,75,25))

            self.on_quit.emit(self.timestamp)

        class reducer:
            def __init__(self, count, total, worker: "LinkPoolOperation.LinkWorker", d):
                from ..bilink import linkdata_admin
                self.count = count
                self.total = total
                self.worker = worker
                self.d = d
                self.linkdata_admin: "" = linkdata_admin
            def reduce_link(self, groupA: "list[G.objs.LinkDataJSONInfo]", groupB: "list[G.objs.LinkDataJSONInfo]"):
                self.worker.on_progress.emit(Utils.percent_calc(self.total,self.count,25,50))
                L = LinkPoolOperation
                for linkinfoA in groupA:
                    for linkinfoB in groupB:
                        if self.worker.mode == L.M.group_by_group:
                            LinkDataOperation.bind(linkinfoA,linkinfoB,needsave=False)
                        elif self.worker.mode == L.M.unlink_by_path:
                            LinkDataOperation.unbind(linkinfoA,linkinfoB,needsave=False)
                self.count+=1
                return groupB


class ModelOperation:
    @staticmethod
    def get_all():
        data = []
        model = mw.col.models.all_names_and_ids()
        for i in model:
            data.append({"id": i.id, "name": i.name})
        return data


class DeckOperation:
    @staticmethod
    def get_all():
        data = []
        deck = mw.col.decks.all_names_and_ids()
        for i in deck:
            data.append({"id": i.id, "name": i.name})
        return data


class MonkeyPatch:

    @staticmethod
    def mw_closeevent(funcs):
        def wrapper(*args, **kwargs):
            self=args[0]
            event=args[1]
            showInfo("hi!")
            funcs(self,event)
        return wrapper

    @staticmethod
    def Reviewer_nextCard(funcs):
        def wrapper(self:"Reviewer"):
            funcs(self)
            cfg = Config.get()
            if cfg.too_fast_warn.value:
                G.nextCard_interval.append(int(datetime.now().timestamp()*1000))
                threshold = cfg.too_fast_warn_everycard.value
                tooltip(G.nextCard_interval.__str__())
                if len(G.nextCard_interval)>1:#大于1才有阈值讨论的余地
                    last = G.nextCard_interval[-2]
                    now = G.nextCard_interval[-1]
                    # tooltip(str(now-last))
                    if now-last>cfg.too_fast_warn_interval.value:
                        G.nextCard_interval.clear()
                        return
                    else:
                        if len(G.nextCard_interval)>=threshold:
                            showInfo(Translate.过快提示)
                            G.nextCard_interval.clear()

        return wrapper

    @staticmethod
    def Reviewer_showEaseButtons(funcs):
        def freezeAnswerCard(self:Reviewer):
            _answerCard = self._answerCard
            self._answerCard = lambda x:tooltip(Translate.已冻结)
            return _answerCard
        def recoverAnswerCard(self:Reviewer,_answerCard):
            self._answerCard = _answerCard
        def _showEaseButtons(self:Reviewer):
            funcs(self)
            cfg = Config.get()
            if cfg.freeze_review.value:
                interval = cfg.freeze_review_interval.value
                self.bottom.web.eval("""
                buttons = document.querySelectorAll("button[data-ease]")
                buttons.forEach(button=>{button.setAttribute("disabled",true)})
                setTimeout(()=>{buttons.forEach(button=>button.removeAttribute("disabled"))},
                """+str(interval)+""")""")

                self.mw.blockSignals(True)
                tooltip(Translate.已冻结)
                _answerCard = freezeAnswerCard(self)
                QTimer.singleShot(interval,lambda :recoverAnswerCard(self,_answerCard))
                QTimer.singleShot(interval, lambda: tooltip(Translate.已解冻))

        return _showEaseButtons

    @staticmethod
    def BrowserSetupMenus(funcs,after,*args, **kwargs):
        def setupMenus(self:"Browser"):
            funcs(self)
            after(self,*args, **kwargs)

        return setupMenus

    @staticmethod
    def onAppMsgWrapper(self: AnkiQt):
        # self.app.appMsg.connect(self.onAppMsg)
        def handle_AnkiLink(buf):
            # buf加了绝对路径,所以要去掉
            # 有时候需要判断一下

            def handle_opencard(id):
                if CardOperation.exists(id):
                    Dialogs.open_custom_cardwindow(id).activateWindow()
                else:
                    tooltip("card not found")
                pass

            def handle_openbrowser(search):
                BrowserOperation.search(search).activateWindow()
                pass

            def handle_opengview(uuid):
                if GviewOperation.exists(uuid=uuid):
                    data = GviewOperation.load(uuid=uuid)
                    Dialogs.open_grapher(gviewdata=data,mode=GraphMode.view_mode)
                else:
                    tooltip("view not found")
            from .objs import CmdArgs
            cmd_dict = {
                "opencard_id": handle_opencard,
                "openbrowser_search": handle_openbrowser,
                "opengview_id": handle_opengview,
            }

            if buf.startswith("ankilink://"):  # 此时说明刚打开就进来了,没有经过包装,格式取buf[11:-1]
                # showInfo(buf[11:-1])
                cmd = CmdArgs(buf[11:-1].split("="))
            else:
                cmd = CmdArgs(os.path.split(buf)[-1].split("="))
            if cmd.type in cmd_dict:
                cmd_dict[cmd.type](cmd.args)
            else:
                showInfo("未知指令错误/unknown command:" + cmd.type)
            pass

        def onAppMsg(buf: str):
            is_addon = self._isAddon(buf)
            is_link = "ANKILINK:" in buf.upper()
            if self.state == "startup":
                # try again in a second
                self.progress.timer(
                    1000, lambda: self.onAppMsg(buf), False, requiresCollection=False
                )
                return
            elif self.state == "profileManager":
                # can't raise window while in profile manager
                if buf == "raise":
                    return None
                self.pendingImport = buf
                if is_addon:
                    msg = tr.qt_misc_addon_will_be_installed_when_a()
                elif is_link:
                    msg = "在profile窗口下,ankilink功能无法正常使用"
                else:
                    msg = tr.qt_misc_deck_will_be_imported_when_a()
                tooltip(msg)
                return
            if not self.interactiveState() or self.progress.busy():
                # we can't raise the main window while in profile dialog, syncing, etc
                if buf != "raise":
                    showInfo(
                        tr.qt_misc_please_ensure_a_profile_is_open(),
                        parent=None,
                    )
                return None
            # raise window
            if isWin:
                # on windows we can raise the window by minimizing and restoring
                self.showMinimized()
                self.setWindowState(Qt.WindowActive)
                self.showNormal()
            else:
                # on osx we can raise the window. on unity the icon in the tray will just flash.
                self.activateWindow()
                self.raise_()
            if buf == "raise":
                return None

            # import / add-on installation
            if is_addon:
                self.installAddon(buf)
            elif is_link:
                handle_AnkiLink(buf)
            else:
                self.handleImport(buf)

            return None

        return onAppMsg

    class BrowserPreviewer(MultiCardPreviewer):
        _last_card_id = 0
        _parent: Optional[Browser]

        def __init__(
                self, parent: Browser, mw: AnkiQt, on_close: Callable[[], None]
        ) -> None:
            super().__init__(parent=parent, mw=mw, on_close=on_close)
            self.ease_button: "dict[int,QPushButton]" = {}
            self.review_button:"QWidget" = QWidget()
            self.due_info_widget:"QWidget"=QWidget()
            self.bottom_layout=QGridLayout()
            self.bottom_layout_rev = QGridLayout()
            self.bottom_layout_due = QGridLayout()
            self.due_label=QLabel()
            self.last_time_label=QLabel()
            self.next_time_label=QLabel()


        def card(self) -> Optional[Card]:
            if self._parent.singleCard:

                return self._parent.card
            else:
                return None
        def render_card(self) -> None:
            super().render_card()
            self._update_info()
            self.switch_to_due_info_widget()

        def _create_gui(self):
            super()._create_gui()
            self._build_review_buttons()
            self._create_due_info_widget()
            self.bottom_layout_due.addWidget(self.due_info_widget,0,0,1,1)
            self.bottom_layout_rev.addWidget(self.review_button,0,0,1,1)
            self.review_button.hide()
            self.vbox.removeWidget(self.bbox)
            self.bottom_layout_due.addWidget(self.bbox,0,1,1,1)
            self.vbox.addLayout(self.bottom_layout_due)

        def card_changed(self) -> bool:
            c = self.card()
            if not c:
                return True
            else:
                changed = c.id != self._last_card_id
                self._last_card_id = c.id
                return changed

        def _on_prev_card(self) -> None:
            self._parent.onPreviousCard()
            # self._update_info()


        def _on_next_card(self) -> None:
            self._parent.onNextCard()
            # self._update_info()
            # self.switch_to_due_info_widget()

        def _should_enable_prev(self) -> bool:
            return super()._should_enable_prev() or self._parent.has_previous_card()

        def _should_enable_next(self) -> bool:
            return super()._should_enable_next() or self._parent.has_next_card()

        def _render_scheduled(self) -> None:
            super()._render_scheduled()
            self._updateButtons()

        def _on_prev(self) -> None:

            if self._state == "answer" and not self._show_both_sides:
                self._state = "question"
                self.render_card()
            else:
                self._on_prev_card()

        def _on_next(self) -> None:

            if self._state == "question":
                self._state = "answer"
                self.render_card()
            else:
                self._on_next_card()
            Utils.tooltip(self._state)

        def freeze_answer_buttons(self):
            for button in self.ease_button.values():
                button.setEnabled(False)
            tooltip(Translate.已冻结)

        def recover_answer_buttons(self):
            for button in self.ease_button.values():
                button.setEnabled(True)
            tooltip(Translate.已解冻)

        def switch_to_answer_buttons(self):
            self._update_info()
            self.review_button.show()
            self.vbox.removeItem(self.bottom_layout_due)
            self.bottom_layout_rev.addWidget(self.bbox,0,1,1,1)
            self.vbox.addLayout(self.bottom_layout_rev)
            self.due_info_widget.hide()
            cfg = Config.get()
            if cfg.freeze_review.value:
                interval = cfg.freeze_review_interval.value
                self.freeze_answer_buttons()
                QTimer.singleShot(interval,lambda:self.recover_answer_buttons())

        def switch_to_due_info_widget(self):
            self._update_info()
            self.review_button.hide()
            self.vbox.removeItem(self.bottom_layout_rev)
            self.bottom_layout_due.addWidget(self.bbox,0,1,1,1)
            self.vbox.addLayout(self.bottom_layout_due)
            self.due_info_widget.show()

        def _answerCard(self, ease):
            mw = compatible_import.mw
            answer = AnswerInfoInterface

            if self.card().timer_started is None:
                self.card().timer_started = time.time() - 60
            CardOperation.answer_card(self.card(), ease)
            self.switch_to_due_info_widget()
            LinkPoolOperation.both_refresh()
            mw.col.reset()
            G.signals.on_card_answerd.emit(
                answer(platform=self, card_id=self.card().id, option_num=ease))

        def should_review(self):
            today, next_date, last_date = self._fecth_date()
            return next_date <= today

        def _update_info(self):
            self._update_answer_buttons()
            self._update_due_info_widget()

        def _create_due_info_widget(self):
            layout = QGridLayout(self.due_info_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            today, next_date, last_date = self._fecth_date()
            self.inAdvance_button = QPushButton(Translate.学习)
            self.inAdvance_button.clicked.connect(self.switch_to_answer_buttons)
            self.due_label.setText(Translate.可复习 if today >= next_date else Translate.未到期)
            self.last_time_label.setText(Translate.上次复习 + ":" + last_date.__str__())
            self.next_time_label.setText(Translate.下次复习 + ":" + next_date.__str__())
            layout.addWidget(self.due_label, 0, 0, 2, 1)
            layout.addWidget(self.last_time_label, 0, 1, 1, 1)
            layout.addWidget(self.next_time_label, 1, 1, 1, 1)
            layout.addWidget(self.inAdvance_button, 0, 2, 2, 1)
            self.due_info_widget.setLayout(layout)


        def _build_review_buttons(self):
            """生成 again,hard,good,easy 按钮"""
            enum = ["", "again", "hard", "good", "easy"]
            layout = QHBoxLayout(self.review_button)
            layout.setContentsMargins(0, 0, 0, 0)
            sched = compatible_import.mw.col.sched
            mw = compatible_import.mw
            button_num = sched.answerButtons(self.card())
            for i in range(button_num):
                ease = enum[i + 1] + ":" + sched.nextIvlStr(self.card(), i + 1)
                self.ease_button[i + 1] = QPushButton(ease)
                answer = lambda i: lambda: self._answerCard(i + 1)
                self.ease_button[i + 1].clicked.connect(answer(i))
                layout.addWidget(self.ease_button[i + 1])
            self.review_button.setLayout(layout)
            self.review_button.setContentsMargins(0,0,0,0)


        def _update_due_info_widget(self):
            today, next_date, last_date = self._fecth_date()
            self.due_label.setText(Translate.可复习 if today >= next_date else Translate.未到期)
            self.last_time_label.setText(Translate.上次复习+":" + last_date.__str__())
            self.next_time_label.setText(Translate.下次复习+":" + next_date.__str__())
            should_review = next_date <= today
        def _update_answer_buttons(self):
            enum = ["", "again", "hard", "good", "easy"]
            sched = compatible_import.mw.col.sched
            button_num = sched.answerButtons(self.card())
            for i in range(button_num):
                ease = enum[i + 1] + ":" + sched.nextIvlStr(self.card(), i + 1)
                self.ease_button[i + 1].setText(ease)

        def _fecth_date(self):
            mw = compatible_import.mw
            result = mw.col.db.execute(
                f"select id,ivl from revlog where id = (select  max(id) from revlog where cid = {self.card().id})"
            )
            if result:
                last, ivl = result[0]
                last_date = datetime.fromtimestamp(last / 1000)  # (Y,M,D,H,M,S,MS)

                write_to_log_file(f"id={last},ivl={ivl}")
                if ivl >= 0:  # ivl 正表示天为单位,负表示秒为单位
                    next_date = datetime.fromtimestamp(last / 1000 + ivl * 86400)  # (Y,M,D,H,M,S,MS)
                else:
                    next_date = datetime.fromtimestamp(last / 1000 - ivl)
            else:
                ivl = 0
                next_date = datetime.today()  # (Y,M,D,H,M,S,MS)
                last_date = datetime.today()  # (Y,M,D,H,M,S,MS)
            today = datetime.today()  # (Y,M,D,H,M,S,MS)
            return today, next_date, last_date

class Dialogs:

    @staticmethod
    def open_GviewAdmin():
        from ..bilink.dialogs.linkdata_grapher import GViewAdmin
        if isinstance(G.GViewAdmin_window,GViewAdmin):
            G.GViewAdmin_window.activateWindow()
        else:
            G.GViewAdmin_window=GViewAdmin()
            G.GViewAdmin_window.show()

    @staticmethod
    def open_anchor(card_id):
        card_id = str(card_id)
        from ..bilink.dialogs.anchor import AnchorDialog
        from . import G
        if card_id not in G.mw_anchor_window:
            G.mw_anchor_window[card_id] = None
        if G.mw_anchor_window[card_id] is None:
            G.mw_anchor_window[card_id] = AnchorDialog(card_id)
            G.mw_anchor_window[card_id].show()
        else:
            G.mw_anchor_window[card_id].activateWindow()

    @staticmethod
    def open_clipper(pairs_li=None, clipboxlist=None, **kwargs):
        if platform.system() in {"Darwin", "Linux"}:
            tooltip("当前系统暂时不支持PDFprev")
            return
        else:
            from . import G
            from ..clipper2.lib.Clipper import Clipper
        # log.debug(G.mw_win_clipper.__str__())
        if not isinstance(G.mw_win_clipper, Clipper):
            G.mw_win_clipper = Clipper()
            G.mw_win_clipper.start(pairs_li=pairs_li, clipboxlist=clipboxlist)
            G.mw_win_clipper.show()
        else:
            G.mw_win_clipper.start(pairs_li=pairs_li, clipboxlist=clipboxlist)
            # all_objs.mw_win_clipper.show()
            G.mw_win_clipper.activateWindow()
            # print("just activate")

    @staticmethod
    def open_linkpool():
        from . import G
        from ..bilink.dialogs.linkpool import LinkPoolDialog
        if G.mw_linkpool_window is None:
            G.mw_linkpool_window = LinkPoolDialog()
            G.mw_linkpool_window.show()
        else:
            G.mw_linkpool_window.activateWindow()
        pass

    @staticmethod
    def open_PDFprev(pdfuuid, pagenum, FROM):
        if platform.system() in {"Darwin", "Linux"}:
            tooltip("当前系统暂时不支持PDFprev")
            return
        else:
            from ..clipper2.lib.PDFprev import PDFPrevDialog
        # print(FROM)
        if isinstance(FROM, Reviewer):
            card_id = FROM.card.id
            pass
        elif isinstance(FROM, BrowserPreviewer):
            card_id = FROM.card().id
            pass
        elif isinstance(FROM, SingleCardPreviewerMod):
            card_id = FROM.card().id
        else:
            TypeError("未能找到card_id")
        card_id = str(card_id)

        DB = G.DB
        result = DB.go(DB.table_pdfinfo).select(uuid=pdfuuid).return_all().zip_up()[0]
        DB.end()
        pdfname = result.to_pdfinfo_data().pdf_path
        pdfpageuuid = UUID.by_hash(pdfname + str(pagenum))
        if card_id not in G.mw_pdf_prev:
            G.mw_pdf_prev[card_id] = {}
        if pdfpageuuid not in G.mw_pdf_prev[card_id]:
            G.mw_pdf_prev[card_id][pdfpageuuid] = None
        if isinstance(G.mw_pdf_prev[card_id][pdfpageuuid], PDFPrevDialog):
            G.mw_pdf_prev[card_id][pdfpageuuid].activateWindow()
        else:
            ratio = 1
            G.mw_pdf_prev[card_id][pdfpageuuid] = \
                PDFPrevDialog(pdfuuid=pdfuuid, pdfname=pdfname, pagenum=pagenum, pageratio=ratio, card_id=card_id)
            G.mw_pdf_prev[card_id][pdfpageuuid].show()

        pass

    @staticmethod
    def open_custom_cardwindow(card: Union[Card, str, int]) -> 'Optional[SingleCardPreviewerMod]':
        """请注意需要你自己激活窗口 请自己做好卡片存在性检查,这一层不检查 """
        from ..bilink.dialogs.custom_cardwindow import external_card_dialog
        if not isinstance(card, Card):
            card = mw.col.get_card(CardId(int(card)))
        return external_card_dialog(card)
        pass

    @staticmethod
    def open_support():
        from .widgets import SupportDialog
        p = SupportDialog()
        p.exec()

    @staticmethod
    def open_contact():
        QDesktopServices.openUrl(QUrl(G.src.path.groupSite))

    @staticmethod
    def open_link_storage_folder():
        open_file(G.src.path.user)

    @staticmethod
    def open_repository():
        QDesktopServices.openUrl(QUrl(G.src.path.helpSite))

    @staticmethod
    def open_version():
        from ..bilink import dialogs
        p = dialogs.version.VersionDialog()
        p.exec()

    @staticmethod
    def open_tag_chooser(pair_li: "list[G.objs.LinkDataPair]"):
        from . import widgets
        p = widgets.tag_chooser(pair_li)
        p.exec()
        pass

    @staticmethod
    def open_deck_chooser(pair_li: "list[G.objs.LinkDataPair]", view=None):
        from . import widgets

        p = widgets.deck_chooser(pair_li, view)
        p.exec()
        tooltip("完成")

        pass

    @staticmethod
    def open_grapher(pair_li: "list[G.objs.LinkDataPair]"=None, need_activate=True, gviewdata:"GViewData"=None,
                     selected_as_center=True,mode=GraphMode.normal, ):
        from ..bilink.dialogs.linkdata_grapher import Grapher
        if mode == GraphMode.normal:
            if isinstance(G.mw_grapher, Grapher):
                G.mw_grapher.load_node(pair_li, selected_as_center=selected_as_center)
                if need_activate:
                    G.mw_grapher.activateWindow()
            else:
                G.mw_grapher = Grapher(pair_li)
                G.mw_grapher.show()
        elif mode == GraphMode.view_mode:
            if (gviewdata.uuid not in G.mw_gview) or (not isinstance(G.mw_gview[gviewdata.uuid],Grapher)):
                G.mw_gview[gviewdata.uuid]=Grapher(pair_li=pair_li,mode=mode,gviewdata=gviewdata)
                G.mw_gview[gviewdata.uuid].show()
            else:
                G.mw_gview[gviewdata.uuid].insert(pair_li)
                # tooltip(f"here G.mw_gview[{gviewdata.uuid}]")
                if need_activate:
                    G.mw_gview[gviewdata.uuid].show()
                    G.mw_gview[gviewdata.uuid].activateWindow()

    @staticmethod
    def open_configuration():
        @dataclasses.dataclass()
        class TabDictItem:
            widget:QWidget = dataclasses.field(default_factory=QWidget)
            layout:QFormLayout = dataclasses.field(default_factory=QFormLayout)
        dialog = QDialog()
        layout = QHBoxLayout()
        tab = QTabWidget()
        cfg = Config.get()

        tab_dict:"dict[Any,TabDictItem]"={}
        for name,value in cfg.get_editable_config().items():
            if value.component == ConfigInterface.Widget.none:
                continue
            if value.tab_at not in tab_dict:
                tab_dict[value.tab_at]:'TabDictItem' = TabDictItem()
            item = Config.make_widget(value)
            tab_dict[value.tab_at].layout.addRow(rosetta(name),item)
        for name,value in tab_dict.items():
            value.widget.setLayout(value.layout)
            tab.addTab(value.widget,name)

        layout.addWidget(tab)
        dialog.setLayout(layout)
        dialog.setWindowIcon(QIcon(G.src.ImgDir.config))
        dialog.setWindowTitle("配置表/configuration")
        dialog.closeEvent=lambda x:Config.save(cfg)
        dialog.exec_()

class AnchorOperation:
    @staticmethod
    def is_empty_then_remove(html_str:"str"):
        bs = BeautifulSoup(html_str,"html.parser")
        roots = bs.select(f"#{G.addonName}")
        tags = bs.select(f"#{G.addonName} .container_body_L1")
        if len(roots)>0:
            root:"BeautifulSoup" = roots[0]
        else:
            return bs.__str__()
        if len(tags)>0 and len(list(tags[0].childGenerator()))==0:
            root.extract()
        return bs.__str__()


class UUID:
    @staticmethod
    def by_random(length=8):
        myid = str(uuid.uuid4())[0:length]
        return myid

    @staticmethod
    def by_hash(s):
        return str(uuid.uuid3(uuid.NAMESPACE_URL, s))


def button_icon_clicked_switch(button: QToolButton, old: list, new: list, callback: "callable" = None):
    if button.text() == old[0]:
        button.setText(new[0])
        button.setIcon(QIcon(new[1]))
    else:
        button.setText(old[0])
        button.setIcon(QIcon(old[1]))
    if callback:
        callback(button.text())


def logger(logname=None, level=None, allhandler=None):
    if G.ISDEBUG:
        if logname is None:
            logname = "hjp_clipper"
        if level is None:
            level = logging.DEBUG
        printer = logging.getLogger(logname)
        printer.setLevel(level)
        log_dir = G.src.path.logtext

        fmt = "%(asctime)s %(levelname)s %(threadName)s  %(pathname)s\n%(filename)s " \
              "%(lineno)d\n%(funcName)s:\n %(message)s"
        datefmt = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(fmt, datefmt)

        filehandle = logging.FileHandler(log_dir)
        filehandle.setLevel(level)
        filehandle.setFormatter(formatter)

        consolehandle = logging.StreamHandler()
        consolehandle.setLevel(level)
        consolehandle.setFormatter(formatter)
        printer.addHandler(consolehandle)
        printer.addHandler(filehandle)
        return printer
    else:
        return do_nothing


def do_nothing(*args, **kwargs):
    pass


def write_to_log_file(s,need_timestamp=False):
    if G.ISDEBUG:
        f = open(G.src.path.logtext, "a", encoding="utf-8")
        f.write("\n"+((datetime.now().strftime("%Y%m%d%H%M%S")+"\n" )if need_timestamp else "") + s)
        f.close()


def str_shorten(string, length=30) -> str:
    if len(string) <= length:
        return string
    else:
        return string[0:int(length / 2) - 3] + "..." + string[-int(length / 2):]


def HTML_injecttoweb(htmltext, card, kind):
    """在web渲染前,注入html代码,"""
    if kind in [
        "previewQuestion",
        "previewAnswer",
        "reviewQuestion",
        "reviewAnswer"
    ]:
        from .HTMLbutton_render import HTMLbutton_make
        html_string = HTMLbutton_make(htmltext, card)


        return html_string
    else:
        return htmltext


def HTML_clipbox_sync_check(card_id, root):
    # 用于保持同步
    assert type(root) == BeautifulSoup
    assert type(card_id) == str
    DB = G.DB
    clipbox_from_DB_ = DB.go(DB.table_clipbox).select(DB.LIKE("card_id", f"%{card_id}%")).return_all().zip_up()
    clipbox_from_DB = set([clipbox["uuid"] for clipbox in clipbox_from_DB_])
    # 选取 clipbox from field
    fields = "\n".join(mw.col.getCard(CardId(int(card_id))).note().fields)
    clipbox_from_field = set(HTML_clipbox_uuid_get(fields))
    # 多退少补,
    DBadd = clipbox_from_field - clipbox_from_DB
    DBdel = clipbox_from_DB - clipbox_from_field
    # print(
    #     f"card_id={card_id},clipbox_from_DB={clipbox_from_DB}, clipbox_from_field={clipbox_from_field}, DBADD={DBadd}.  DBdel={DBdel}")
    if len(DBadd) > 0:
        # DB.add_card_id(DB.where_maker(IN=True, colname="uuid", vals=DBadd), card_id)
        DB.add_card_id(DB.IN("uuid", *DBadd), card_id)
    if len(DBdel) > 0:
        # DB.del_card_id(DB.where_maker(IN=True, colname="uuid", vals=DBdel), card_id)
        DB.del_card_id(DB.IN("uuid", *DBdel), card_id)
    DB.end()
    pass


def HTML_clipbox_PDF_info_dict_read(root):
    """ 从所给的HTML 中读取 每个clipbox对应的 PDFuuid,以及其名字,和所包含的页码"""
    assert type(root) == BeautifulSoup
    clipbox_from_field = set(HTML_clipbox_uuid_get(root))
    DB = G.DB
    DB.go(DB.table_clipbox).select(DB.IN("uuid", *clipbox_from_field))

    # DB.go(DB.table_clipbox).select(where=DB.where_maker(IN=True, vals=clipbox_from_field, colname="uuid"))
    # print(DB.excute_queue[-1])
    record_li = DB.return_all().zip_up().to_clipbox_data()
    PDF_info_dict = {}  # {uuid:{pagenum:{},pdfname:""}}
    for record in record_li:
        PDFinfo = DB.go(DB.table_pdfinfo).select(uuid=record.pdfuuid).return_all().zip_up()[0].to_pdfinfo_data()
        if PDFinfo.uuid not in PDF_info_dict:
            PDF_info_dict[PDFinfo.uuid] = {"pagenum": set(),  # 页码唯一化
                                           "info": PDFinfo}  # 只提取页码, 大小重新再设定.偏移量也重新设定.
        PDF_info_dict[PDFinfo.uuid]["pagenum"].add(record.pagenum)
    DB.end()
    return PDF_info_dict


def HTML_LeftTopContainer_detail_el_make(root: "BeautifulSoup", summaryname, attr: "dict" = None):
    """这是一个公共的步骤,设计一个details, root 传进来无所谓的, 不会基于他做操作,只是引用了他的基本功能
    details.hjp_bilink .details
        summary
        div
    """
    if attr is None:
        attr = {}
    attrs = {"class": "hjp_bilink details", **(attr.copy())}
    # print(attrs)
    details = root.new_tag("details", attrs=attrs)
    summary = root.new_tag("summary")
    summary.string = summaryname
    div = root.new_tag("div")
    details.append(summary)
    details.append(div)
    return details, div


def HTML_clipbox_uuid_get(html):
    if type(html) == str:
        root = BeautifulSoup(html, "html.parser")
    elif type(html) == BeautifulSoup:
        root = html
    else:
        raise TypeError("无法处理参数类型: {}".format(type(html)))
    imgli = root.find_all("img", src=re.compile("hjp_clipper_\w{8}_.png"))
    clipbox_uuid_li = [re.sub("hjp_clipper_(\w+)_.png", lambda x: x.group(1), img.attrs["src"]) for img in imgli]
    return clipbox_uuid_li


def HTML_clipbox_exists(html, card_id=None):
    """任务:
    1检查clipbox的uuid是否在数据库中存在,如果存在,返回True,不存在返回False,
    2当存在时,检查卡片id是否是clipbox对应card_id,如果不是,则要添加,此卡片
    3搜索本卡片,得到clipbox的uuid,如果有搜到 uuid 但是又不在html解析出的uuid中, 则将数据库中的uuid的card_id删去本卡片的id
    """
    clipbox_uuid_li = HTML_clipbox_uuid_get(html)
    DB = G.DB
    DB.go(DB.table_clipbox)
    # print(clipbox_uuid_li)
    true_or_false_li = [DB.exists(DB.EQ(uuid=uuid)) for uuid in clipbox_uuid_li]
    DB.end()
    return (reduce(lambda x, y: x or y, true_or_false_li, False))


def HTML_LeftTopContainer_make(root: "BeautifulSoup"):
    """
    注意在这一层已经完成了,CSS注入
    传入的是从html文本解析成的beautifulSoup对象
    设计的是webview页面的左上角按钮,包括的内容有:
    anchorname            ->一切的开始
        style             ->样式设计
        div.container_L0  ->按钮所在地
            div.header_L1 ->就是 hjp_bilink 这个名字所在的地方
            div.body_L1   ->就是按钮和折叠栏所在的地方
    一开始会先检查这个anchorname元素是不是已经存在,如果存在则直接读取
    """
    # 寻找 anchorname ,建立 anchor_el,作为总的锚点.
    ID = G.addonName
    # ID = ""
    anchorname = ID if ID != "" else "anchor_container"
    resultli = root.select(f"#{anchorname}")
    if len(resultli) > 0:  # 如果已经存在,就直接取得并返回
        anchor_el: "element.Tag" = resultli[0]
    else:
        anchor_el: "element.Tag" = root.new_tag("div", attrs={"id": anchorname})
        root.insert(1, anchor_el)
        # 设计 style
        cfg=Config.get()
        if cfg.anchor_style_text.value!="":
            style_str = cfg.anchor_style_text.value
        elif cfg.anchor_style_file.value!="" and os.path.exists(cfg.anchor_style_file.value):
            style_str = cfg.anchor_style_file.value
        else:
            style_str = open(G.src.path.anchor_CSS_file[cfg.anchor_style_preset.value], "r", encoding="utf-8").read()
        style = root.new_tag("style")
        style.string = style_str
        anchor_el.append(style)
        # 设计 容器 div.container_L0, div.header_L1和div.body_L1
        L0 = root.new_tag("div", attrs={"class": "container_L0"})
        header_L1 = root.new_tag("div", attrs={"class": "container_header_L1"})
        header_L1.string = G.addonName
        body_L1 = root.new_tag("div", attrs={"class": "container_body_L1"})
        L0.append(header_L1)
        L0.append(body_L1)
        anchor_el.append(L0)
    return anchor_el  # 已经传入了root,因此不必传出.

@dataclasses.dataclass
class DataFROM:
    shortCut=0

class AnkiLinks:
    class Type:
        html = 0
        markdown = 1
        orgmode = 2
        inAnki =3

    @staticmethod
    def copy_card_as(linktype: int=None, pairs_li: 'list[G.objs.LinkDataPair]'=None,FROM=None):
        tooltip(pairs_li.__str__())
        clipboard = QApplication.clipboard()
        header = "ankilink://opencard_id="
        if FROM==DataFROM.shortCut:
            pairs_li = BrowserOperation.get_selected_card()
            linktype = Config.get().default_copylink_mode.value

        def as_html(pairs_li: 'list[G.objs.LinkDataPair]'):
            total = ""
            puretext = ""
            for pair in pairs_li:
                total += f"""<a href="{header}{pair.card_id}">{pair.desc}<a><br>""" + "\n"
                puretext += f"""{header}{pair.card_id}\n"""
            mmdata = QMimeData()
            mmdata.setHtml(total)
            mmdata.setText(puretext)
            clipboard.setMimeData(mmdata)
            # clipboard.setText(total)
            pass
        def as_inAnki(pairs_li: 'list[G.objs.LinkDataPair]'):
            total=""
            def buttonmaker(p:LinkDataPair):
                return f"""<div >|<button class="hjp_bilink ankilink button" onclick="javascript:pycmd('{header}{p.card_id}');">{p.desc}</button>|</div>"""
            for pair in pairs_li:
                total+=buttonmaker(pair)
            clipboard.setText(total)
        def as_markdown(pairs_li: 'list[G.objs.LinkDataPair]'):
            total = ""
            for pair in pairs_li:
                total += f"""[{pair.desc}]({header}{pair.card_id})\n"""
            clipboard.setText(total)
            pass

        def as_orgmode(pairs_li: 'list[G.objs.LinkDataPair]'):
            total = ""
            for pair in pairs_li:
                total += f"""[[{header}{pair.card_id}][{pair.desc}]]\n"""
            clipboard.setText(total)
            pass

        typ = AnkiLinks.Type
        func_dict = {typ.html: as_html,
                     typ.orgmode: as_orgmode,
                     typ.markdown: as_markdown,
                     typ.inAnki:as_inAnki}
        func_dict[linktype](pairs_li)
        if len(pairs_li)>0:
            tooltip(clipboard.text())
        else:
            tooltip(Translate.请选择卡片)

    @staticmethod
    def copy_search_as(linktype: int, browser: "Browser"):
        searchstring = browser.form.searchEdit.currentText()
        tooltip(searchstring)
        clipboard = QApplication.clipboard()
        header = "ankilink://openbrowser_search="
        href = header + quote(searchstring)

        def as_html():
            total = f"""<a href="{href}">{Translate.Anki搜索}:{searchstring}</a>"""
            mmdata = QMimeData()
            mmdata.setHtml(total)
            mmdata.setText(href)
            clipboard.setMimeData(mmdata)
            pass

        def as_markdown():
            total = f"[{Translate.Anki搜索}:{searchstring}]({href})"
            clipboard.setText(total)
            pass

        def as_orgmode():
            total = f"[[{href}][{Translate.Anki搜索}:{searchstring}]]"
            clipboard.setText(total)
            pass

        typ = AnkiLinks.Type
        func_dict = {typ.html: as_html,
                     typ.orgmode: as_orgmode,
                     typ.markdown: as_markdown}
        func_dict[linktype]()
        pass
    @staticmethod
    def copy_gview_as(linktype:int,data:"GViewData"):
        tooltip(data.__str__())
        clipboard = QApplication.clipboard()
        header = "ankilink://opengview_id="
        href = header + quote(data.uuid)

        def as_html():
            total = f"""<a href="{href}">{Translate.Anki视图}:{data.name}</a>"""
            mmdata = QMimeData()
            mmdata.setHtml(total)
            mmdata.setText(href)
            clipboard.setMimeData(mmdata)
            pass
        def as_inAnki():
            total = f"""<div >|<button class="hjp_bilink ankilink button" onclick="javascript:pycmd('{href}');">{Translate.Anki视图}:{data.name}</button>|</div>"""
            mmdata = QMimeData()
            mmdata.setHtml(total)
            mmdata.setText(href)
            # clipboard.setMimeData(mmdata)
            clipboard.setText(total)
        def as_markdown():
            total = f"[{Translate.Anki视图}:{data.name}]({href})"
            clipboard.setText(total)
            pass

        def as_orgmode():
            total = f"[[{href}][{Translate.Anki视图}:{data.name}]]"
            clipboard.setText(total)
            pass




        typ = AnkiLinks.Type
        func_dict = {typ.html: as_html,
                     typ.orgmode: as_orgmode,
                     typ.markdown: as_markdown,
                     typ.inAnki:as_inAnki,}
        func_dict[linktype]()

    @staticmethod
    def get_card_from_clipboard():
        from ..bilink.linkdata_admin import read_card_link_info
        clipboard = QApplication.clipboard()
        cliptext = clipboard.text()
        reg_str=r"(?:ankilink://opencard_id=|\[\[link:)(\d+)"
        pair_li = [read_card_link_info(card_id).self_data for card_id in re.findall(reg_str,cliptext)]
        return pair_li



def copy_intext_links(pairs_li: 'list[G.objs.LinkDataPair]'):
    from .objs import LinkDataPair
    from .language import rosetta as say
    def linkformat(card_id, desc):
        return f"""[[link:{card_id}_{desc}_]]"""

    copylinkLi = [linkformat(pair.card_id, pair.desc) for pair in pairs_li]
    clipstring = "\n".join(copylinkLi)
    if clipstring == "":
        tooltip(f"""{Translate.未选择卡片}""")
    else:
        clipboard = QApplication.clipboard()
        clipboard.setText(clipstring)
        tooltip(f"""{Translate.已复制到剪贴板}：{clipstring}""")
    pass


def PDFprev_close(card_id, pdfpageuuid=None, all=False):
    if platform.system() in {"Darwin", "Linux"}:
        # tooltip("当前系统暂时不支持PDFprev")
        return
    else:
        from . import G
        from ..clipper2.lib.PDFprev import PDFPrevDialog
    if isinstance(card_id, int):
        card_id = str(card_id)
    if card_id not in G.mw_pdf_prev:
        return
    reviewer_still = mw.reviewer.card is not None and mw.reviewer.card.id == int(card_id)
    browser = BrowserOperation.get_browser()  # aqt.mw = self
    previewer_still = browser is not None and browser._previewer is not None \
                      and browser._previewer.card() is not None and browser._previewer.card().id == int(card_id)
    card_window_still = card_id in G.mw_card_window and G.mw_card_window[card_id] is not None
    if reviewer_still or previewer_still or card_window_still:
        return
    if all:
        for pdfpageuuid in G.mw_pdf_prev[card_id].keys():
            if isinstance(G.mw_pdf_prev[card_id][pdfpageuuid], PDFPrevDialog):
                p = G.mw_pdf_prev[card_id][pdfpageuuid]
                p.close()
                # all_objs.mw_pdf_prev[card_id][pdfpageuuid]=None
    else:
        if pdfpageuuid in G.mw_pdf_prev[card_id]:
            p = G.mw_pdf_prev[card_id][pdfpageuuid]
            p.close()
            # all_objs.mw_pdf_prev[card_id][pdfpageuuid] = None


def on_clipper_closed_handle():
    from . import G
    G.mw_win_clipper = None


def event_handle_connect(event_dict):
    for event, handle in event_dict:
        event.connect(handle)
    return event_dict


def event_handle_disconnect(event_dict: "list[list[pyqtSignal,callable]]"):
    for event, handle in event_dict:
        try:
            # print(event.signal)
            event.disconnect(handle)
            # print(f"""{event.__str__()} still has {}  connects""")
        except Exception:
            # print(f"{event.__str__()} do not connect to {handle.__str__()}")
            pass


def open_file(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def version_cmpkey(path):
    from . import objs
    filename = os.path.basename(path)
    v_tuple = re.search(r"(\d+)\.(\d+)\.(\d+)", filename).groups()
    return objs.AddonVersion(v_tuple)


def note_get(card_id):
    from . import objs
    cid = CardOperation.get_correct_id(card_id)
    if card_exists(cid):
        note = mw.col.getCard(cid).note()
    else:
        showInfo(f"{cid} 卡片不存在/card don't exist")
        return None
    return note


def desc_extract(card_id=None, fromField=False):
    """读取卡片的描述,需要卡片id, fromField就是为了避免循环递归, fromField 意思是从卡片的Field提取描述"""
    from . import objs
    from ..bilink import linkdata_admin

    def get_desc_from_field(_note: Note) -> str:
        content = reduce(lambda x, y: x + y, _note.fields)
        _desc = HTML_txtContent_read(content)
        _desc = re.sub(r"\n+", "", _desc)
        _desc = _desc if cfg.length_of_desc.value == 0 else _desc[0:min(cfg.length_of_desc.value, len(_desc))]
        return _desc
    cid = CardOperation.get_correct_id(card_id)
    cfg = Config.get()
    note = note_get(cid)
    desc = ""
    if note is not None:
        if fromField or cfg.desc_sync.value:  # 分成这两段, 是因为一个循环引用.
            desc = get_desc_from_field(note)
            Utils.print(f"fromField={fromField},desc_sync={cfg.desc_sync.value},desc={desc}")
        else:
            desc = linkdata_admin.read_card_link_info(str(cid)).self_data.desc
            Utils.print("desc fromDB ="+desc)
            if desc == "":
                desc = get_desc_from_field(note)
    return desc


def card_exists(card_id):
    from . import objs
    cid = CardOperation.get_correct_id(card_id)
    txt = f"cid:{cid}"
    card_ids = mw.col.find_cards(txt)

    if len(card_ids) == 1:
        return True
    else:
        tooltip("卡片不存在/card not exists:\n"
                "id=" + str(cid))
        return False


def HTML_txtContent_read(html):
    """HTML文本内容的读取,如果没有就尝试找img的src文本,要去掉 intext link内容"""

    from ..bilink.in_text_admin.backlink_reader import BackLinkReader

    cfg = ConfigInterface()
    root = BeautifulSoup(html, "html.parser")
    list(map(lambda x: x.extract(), root.select(".hjp_bilink.ankilink.button")))
    text = root.getText()
    if cfg.delete_intext_link_when_extract_desc.value == 1:
        newtext = text
        replace_str = ""
        intextlinks = BackLinkReader(html_str=text).backlink_get()
        for link in intextlinks:
            span = link["span"]
            replace_str += re.sub("(\])|(\[)", lambda x: "\]" if x.group(0) == "]" else "\[",
                                  text[span[0]:span[1]]) + "|"
        replace_str = replace_str[0:-1]
        text = re.sub(replace_str, "", newtext)
    if not re.search("\S", text):
        a = root.find("img")
        if a is not None:
            text = a.attrs["src"]

    return text


def pair_li_make(card_li: "list[str]"):
    from .objs import LinkDataPair
    d = [LinkDataPair(card_id=card_id, desc=desc_extract(card_id)) for card_id in card_li]
    return d


def data_crashed_report(data):
    from . import G
    path = G.src.path.data_crash_log
    showInfo(f"你的卡片链接信息读取失败,相关的失败数据已经保存到{path},请联系作者\n"
             f"Your card link information failed to read, the related failure data has been saved to{path}, please contact the author")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    caller = sys._getframe(1).f_code.co_name
    filename = sys._getframe(1).f_code.co_filename
    line_number = sys._getframe(1).f_lineno
    data_string = data.__str__()
    info = f"""\n{filename}\n{timestamp} {caller} {line_number}\n{data_string}"""
    if not os.path.exists(path):
        f = open(path, "w", encoding="utf-8")
    else:
        f = open(path, "a", encoding="utf-8")
    f.write(info)


CardId = Compatible.CardId()
log = logger(__name__)


class LOG:
    logger = logger(__name__)
    file_write = write_to_log_file

    @staticmethod
    def file_clear():
        f = open(G.src.path.logtext, "w", encoding="utf-8")
        f.write("")

    @staticmethod
    def exists():
        return os.path.exists(G.src.path.logtext)
