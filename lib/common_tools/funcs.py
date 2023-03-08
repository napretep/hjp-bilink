# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = '$NAME.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2021/7/30 9:09'
"""
import abc
import dataclasses
import logging
import random
import shutil
import sys, platform, subprocess
import tempfile
import urllib.parse
from urllib.parse import quote

import uuid
from collections import Sequence
from datetime import datetime, timedelta
import time, math
# from math import ceil
from typing import Union, Optional, NewType, Callable, List, Iterable, Type, Any
import json
import os
import re
from functools import reduce, cmp_to_key
from .compatible_import import *
from . import baseClass

from anki import notes
from anki.cards import Card
from anki.notes import Note

from bs4 import BeautifulSoup, element
from . import G, compatible_import
from .language import Translate, rosetta

译 = Translate
from .objs import LinkDataPair, LinkDataJSONInfo
from . import objs

if not ISLOCAL:
    from ..bilink.dialogs.custom_cardwindow import SingleCardPreviewer
from .configsModel import ConfigModel, AnswerInfoInterface, GroupReviewDictInterface, GViewData, GraphMode, \
    ConfigModelItem, CustomConfigItemView, BaseConfigModel, GviewConfigModel
from . import widgets

字典键名 = baseClass.枚举命名
枚举_视图结点类型 = baseClass.视图结点类型


def do_nothing(*args, **kwargs):
    pass


def write_to_log_file(s, need_timestamp=False):
    if G.ISDEBUG:
        f = open(G.src.path.logtext, "a", encoding="utf-8")
        f.write("\n" + ((datetime.now().strftime("%Y%m%d%H%M%S") + "\n") if need_timestamp else "") + s)
        f.close()


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


class Map:
    @staticmethod
    def do(li: "iter", func: "callable"):
        return list(map(func, li))


class Filter:
    @staticmethod
    def do(li: "iter", func: "callable"):
        return list(filter(func, li))


class MenuMaker:

    @staticmethod
    def gview_ankilink(menu, data):
        act = [Translate.文内链接, Translate.html链接, Translate.markdown链接, Translate.orgmode链接]
        # f = [lambda: AnkiLinks.copy_gview_as(AnkiLinks.Type.inAnki, data),
        #      lambda: AnkiLinks.copy_gview_as(AnkiLinks.Type.html, data),
        #      lambda: AnkiLinks.copy_gview_as(AnkiLinks.Type.markdown, data),
        #      lambda: AnkiLinks.copy_gview_as(AnkiLinks.Type.orgmode, data), ]
        f = [
                lambda: AnkiLinksCopy2.Open.Gview.from_htmlbutton(data),
                lambda: AnkiLinksCopy2.Open.Gview.from_htmllink(data),
                lambda: AnkiLinksCopy2.Open.Gview.from_md(data),
                lambda: AnkiLinksCopy2.Open.Gview.from_orgmode(data)
        ]
        list(map(lambda x: menu.addAction(act[x]).triggered.connect(f[x]), range(len(f))))
        return menu


class GviewOperation:

    @staticmethod
    def 获取视图配置编号(data: "str|GViewData") -> "str":
        uuid = data if type(data) == str else data.uuid
        DB = G.DB
        DB.go(DB.table_Gview)
        return DB.select(DB.EQ(uuid=uuid)).return_all().zip_up()[0]["config"]

    @staticmethod
    def 设为默认视图(uuid):
        cfg = Config.get()
        cfg.set_default_view.value = uuid
        cfg.save_to_file(G.src.path.userconfig)

    @staticmethod
    def 打开默认视图():
        cfg = Config.get()
        if cfg.set_default_view.value != -1:
            Dialogs.open_view(gviewdata=GviewOperation.load(uuid=cfg.set_default_view.value))
        else:
            showInfo(译.请先设定默认视图)

    @staticmethod
    def 打开默认漫游复习():
        cfg = Config.get()
        if cfg.set_default_view.value != -1:
            GviewOperation.打开默认视图()
            from ..bilink.dialogs.linkdata_grapher import Grapher
            view: Grapher = G.mw_gview[cfg.set_default_view.value]
            view.toolbar.openRoaming()
        else:
            showInfo(译.请先设定默认视图)

    @staticmethod
    def 判断视图已经打开(视图编号):
        """判断且直接返回"""
        from ..bilink.dialogs.linkdata_grapher import Grapher

        if 视图编号 in G.mw_gview and isinstance(G.mw_gview[视图编号], Grapher):
            视图窗口: Grapher = G.mw_gview[视图编号]
            return 视图窗口
        else:
            return None

    @staticmethod
    def 更新卡片到期时间(卡片编号):
        视图数据集 = GviewOperation.找到结点所属视图(卡片编号)
        for 视图数据 in 视图数据集:
            视图窗口 = GviewOperation.判断视图已经打开(视图数据.uuid)
            if 视图窗口:
                视图窗口.data.node_dict[卡片编号].due = GviewOperation.判断结点已到期(视图数据, 卡片编号)

        pass

    @staticmethod
    def 重命名(视图数据: GViewData, 新名字):
        视图数据.name = 新名字
        GviewOperation.save(视图数据)
        # tooltip("改名成功".format(view_name=视图数据.name, name=新名字))

    @staticmethod
    def 获取主要结点编号(视图数据: GViewData):
        return [结点 for 结点 in 视图数据.nodes if 视图数据.nodes[结点].主要结点.值 == True]

    @staticmethod
    def 判断结点已到期(视图数据: GViewData, 结点编号: str):
        现在 = int(time.time())
        类型 = 视图数据.nodes[结点编号].数据类型.值

        if 类型 == 枚举_视图结点类型.卡片:
            _, nextRev = CardOperation.getLastNextRev(结点编号)
            # Utils.print("card_id=",结点编号,"nextRev=",nextRev,)
            # Utils.print(nextRev.timetuple())
            return int(time.mktime(nextRev.timetuple())) <= 现在
        elif 类型 == 枚举_视图结点类型.视图:
            return True
        else:
            raise NotImplementedError()

    @staticmethod
    def 结点上次复习时间(视图数据: GViewData, 结点编号: str):
        """如果是卡片, 则调用 CardOperation.上次复习时间(结点编号)
        否则另外解决
        """
        类型 = 视图数据.nodes[结点编号].数据类型.值
        if 类型 == 枚举_视图结点类型.卡片:
            return CardOperation.getLastNextRev(结点编号)[0]
        elif 类型 == 枚举_视图结点类型.视图:
            return Utils.时间戳转日期(视图数据.meta[字典键名.视图.上次复习])
        else:
            raise NotImplementedError()

    @staticmethod
    def 获取结点出度(视图数据: GViewData, 结点编号: str):
        return len([1 for 边 in 视图数据.edges.keys() if 边.startswith(结点编号)])

    @staticmethod
    def 获取结点入度(视图数据: GViewData, 结点编号: str):
        return len([1 for 边 in 视图数据.edges.keys() if 边.endswith(结点编号)])

    @staticmethod
    def 设定视图结点描述(视图数据: GViewData, 结点编号, 设定内容):
        视图类型 = 视图数据.nodes[结点编号].数据类型.值
        Utils.print(结点编号, 设定内容)
        if 视图类型 == 枚举_视图结点类型.卡片:
            CardOperation.desc_save(结点编号, 设定内容)
            CardOperation.refresh()
        else:
            结点对应视图 = GviewOperation.load(结点编号)
            结点对应视图.name = 设定内容
            GviewOperation.save(结点对应视图)
        if GviewOperation.判断视图已经打开(视图数据.uuid):
            视图数据.nodes.data[结点编号][字典键名.结点.描述] = 设定内容

    @staticmethod
    def 获取视图结点描述(视图数据: "GViewData", 结点编号, 全部内容=False):

        视图类型 = 视图数据.nodes[结点编号].数据类型.值
        if 视图类型 == 枚举_视图结点类型.卡片:
            return CardOperation.desc_extract(结点编号) if not 全部内容 else CardOperation.获取卡片内容与标题(结点编号)
        else:
            return GviewOperation.load(uuid=结点编号).name

        pass

    @staticmethod
    def 获取视图名字(视图编号):
        if not GviewOperation.exists(uuid=视图编号):
            raise ValueError(f"视图:{视图编号}不存在")

        DB = G.DB
        return DB.go(DB.table_Gview).select(DB.EQ(uuid=视图编号)).return_all().zip_up()[0]["name"]

    @staticmethod
    def 列出已打开的视图():
        from ..bilink.dialogs.linkdata_grapher import Grapher
        return [键 for 键 in G.mw_gview.keys() if isinstance(G.mw_gview[键], Grapher)]

    @staticmethod
    def 更新缓存(视图: "str|GViewData" = None):
        """这个东西, 更新的是一个表, 这个表的每个记录对应一个视图索引,
        记录的第一列是视图索引, 第二列是视图中全部卡片描述的并集, 用于搜索关键词定位视图
        流程, 如果存在数据表, 则drop table, 然后生成新的插
        """
        from .objs import Logic
        DB = G.DB
        if 视图:
            if type(视图) == str:
                数据 = GviewOperation.load(uuid=视图)
                编号 = 视图
            else:
                数据 = 视图
                编号 = 视图.uuid
            缓存内容 = "\n".join(GviewOperation.获取视图结点描述(数据, 索引, 全部内容=True) for 索引 in 数据.nodes.keys())
            DB.go(DB.table_Gview)

            DB.update(values=Logic.LET(**{字典键名.视图.视图卡片内容缓存: 缓存内容}),
                      where=Logic.EQ(uuid=编号)
                      ).commit()

        else:

            # DB.go(DB.table_Gview_cache)
            Utils.tooltip("gview cache begin to rebuild")
            DB.表删除(DB.table_Gview_cache)

            视图数据表 = GviewOperation.load_all_as_dict()
            视图缓存字典 = []
            计数 = 0
            for 数据 in 视图数据表.values():
                结点索引表 = list(数据.nodes.keys())
                视图缓存字典.append([数据.uuid, ""])

                for 结点索引 in 结点索引表:

                    if ISLOCALDEBUG:
                        描述 = "debug"
                    else:
                        描述 = CardOperation.获取卡片内容与标题(结点索引) if 数据.nodes[结点索引][字典键名.结点.数据类型] == 枚举_视图结点类型.卡片 \
                            else 视图数据表[结点索引].name

                    视图缓存字典[-1][1] += 描述 + "\n"
                视图缓存字典[-1][1] = "'" + 视图缓存字典[-1][1] + "'"
            DB.go(DB.table_Gview_cache).批量插入(视图缓存字典)

        Utils.tooltip("gview cache rebuild end")

    @staticmethod
    def 刷新所有已打开视图的配置():
        from ..bilink.dialogs.linkdata_grapher import Grapher
        for 视图编号, 视图窗口 in G.mw_gview.items():
            if isinstance(视图窗口, Grapher):
                视图窗口.data.gviewdata.config_model = GviewConfigOperation.从数据库读(视图窗口.data.gviewdata.config)

    @staticmethod
    def fuzzy_search(search_string: str):
        """在GRAPH_VIEW , GRAPH_VIEW_CACHE 两个表中做模糊搜索, 将用户的空格替换成通配符"""
        # 关键词正则 = re.sub(r"\s", ".*", search_string)
        关键词正则 = re.sub(r"\s", "%", search_string)
        DB, Logic = G.DB, objs.Logic

        DB.go(DB.table_Gview)
        DB.excute_queue.append(f"""select * from GRAPH_VIEW_TABLE where 
        name like '%{关键词正则}%' 
        or uuid like '%{关键词正则}%' 
        or card_content_cache like '%{关键词正则}%' """)
        匹配的视图集 = [data.to_GviewData() for data in DB.return_all().zip_up().to_gview_record()]

        return 匹配的视图集
        pass

    @staticmethod
    def save(data: GViewData = None, data_li: "Iterable[GViewData]" = None, exclude: "list[str]" = None):
        """"""
        Logic = objs.Logic
        if data:
            # Utils.print(data,need_logFile=True)
            prepare_data = data.to_DB_format()
            # Utils.print(prepare_data,need_logFile=True)
            if exclude is not None:
                [prepare_data.pop(item) for item in exclude]
            DB = G.DB.go(G.DB.table_Gview)

            if DB.exists(Logic.EQ(uuid=data.uuid)):
                DB.update(values=Logic.LET(**prepare_data), where=Logic.EQ(uuid=data.uuid)).commit()
            else:
                DB.insert(**prepare_data).commit()
            return
        elif data_li:
            DB = G.DB.go(G.DB.table_Gview)
            for data in data_li:
                prepare_data = data.to_DB_format()
                if exclude is not None:
                    [prepare_data.pop(item) for item in exclude]
                if DB.exists(Logic.EQ(uuid=data.uuid)):
                    DB.update(values=Logic.LET(**prepare_data), where=Logic.EQ(uuid=data.uuid)).commit()
                else:
                    DB.insert(**prepare_data).commit()
            return

    @staticmethod
    def exists(data: GViewData = None, name=None, uuid=None):
        DB = G.DB
        DB.go(DB.table_Gview)
        exists = False
        if data:
            exists = DB.exists(DB.EQ(uuid=data.uuid))
        elif name:
            exists = DB.exists(DB.EQ(name=name))
        elif uuid:
            exists = DB.exists(DB.EQ(uuid=uuid))
        return exists

    @staticmethod
    def load(uuid=None, gviewdata: "GViewData" = None):
        """"""
        # print("uuid=",uuid)
        data = None
        if GviewOperation.exists(uuid=uuid):
            DB = G.DB
            DB.go(DB.table_Gview)
            data = DB.select(DB.EQ(uuid=uuid)).return_all().zip_up().to_gview_record()[0].to_GviewData()

        elif gviewdata is not None:
            DB = G.DB
            DB.go(DB.table_Gview)
            data = DB.select(DB.EQ(uuid=gviewdata.uuid)).return_all().zip_up().to_gview_record()[0].to_GviewData()

        # elif pairli is not None:
        #     data = GviewOperation.find_by_card(pairli)
        if data is None:
            raise ValueError(f"未知的uuid={uuid},或gviewdata={gviewdata}")
        return data

    @staticmethod
    def load_all() -> 'List[GViewData]':
        DB = G.DB
        DB.go(DB.table_Gview)
        DB.excute_queue.append(DB.sqlstr_RECORD_SELECT_ALL.format(tablename=DB.tab_name))
        records = [记录.to_GviewData() for 记录 in DB.return_all().zip_up().to_gview_record()]
        return records

    @staticmethod
    def load_all_as_dict() -> "dict[str,GViewData]":
        DB = G.DB
        DB.go(DB.table_Gview)
        DB.excute_queue.append(DB.sqlstr_RECORD_SELECT_ALL.format(tablename=DB.tab_name))
        记录表 = DB.return_all().zip_up().to_gview_record()
        结果 = {}
        [结果.__setitem__(记录.uuid, 记录.to_GviewData()) for 记录 in 记录表]
        return 结果

    @staticmethod
    def 读取全部id():
        DB = G.DB
        DB.go(DB.table_Gview)
        DB.excute_queue.append(DB.sqlstr_RECORD_SELECT_ALL.format(tablename=DB.tab_name))
        return [记录.uuid for 记录 in DB.return_all().zip_up().to_gview_record()]

    @staticmethod
    def 找到结点所属视图(结点编号):
        结点编号 = 结点编号.card_id if isinstance(结点编号, LinkDataPair) else 结点编号
        DB = G.DB
        视图记录集 = DB.go(DB.table_Gview).select(DB.LIKE("nodes", 结点编号)).return_all().zip_up().to_gview_record()
        return [视图记录.to_GviewData() for 视图记录 in 视图记录集]

    @staticmethod
    def find_by_card(pairli: 'list[LinkDataPair|str]') -> 'set[GViewData]':
        """找到卡片所属的gview记录,还要去掉重复的, 比如两张卡在同一个视图中, 只取一次 """
        DB = G.DB
        DB.go(DB.table_Gview)

        # def pair_to_gview(pair):
        #     card_id = pair.card_id if isinstance(pair,LinkDataPair) else pair
        #     DB.go(DB.table_Gview)
        #     datas = DB.select(DB.LIKE("nodes", card_id)).return_all(Utils.print).zip_up().to_gview_record()
        #     return set(map( lambda data: data.to_GviewData(), datas))

        all_records = list(map(lambda x: set(GviewOperation.找到结点所属视图(x)), pairli))
        final_givew = reduce(lambda x, y: x & y, all_records) if len(all_records) > 0 else set()

        return final_givew

    @staticmethod
    def delete(uuid: str = None, uuid_li: "Iterable[str]" = None):
        """"""
        from ..bilink.dialogs.linkdata_grapher import Grapher
        DB = G.DB

        def 彻底删除(视图标识):

            if 视图标识 in G.mw_gview and isinstance(G.mw_gview[视图标识], Grapher):
                视图窗口: Grapher = G.mw_gview[视图标识]
                视图窗口.close()
            config = GviewOperation.load(视图标识).config
            if config:
                GviewConfigOperation.从数据库删除(config)
            DB.go(DB.table_Gview)
            DB.delete(where=DB.LET(uuid=视图标识)).commit()

        if uuid:
            彻底删除(uuid)
        elif uuid_li:
            for uuid in uuid_li:
                彻底删除(uuid)
        return

    @staticmethod
    def get_correct_view_name_input(placeholder=""):
        def view_name_check(name: str, placeholder="") -> bool:
            if name == "" or re.search(r"\s", name) or re.search("::::", name) \
                    or re.search("\s", "".join(name.split("::"))) or "".join(name.split("::")) == "":
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
                submitted = False
                break
            if view_name_check(viewName, placeholder):
                break
        return (viewName, submitted)

    @staticmethod
    def create(nodes=None, edges=None, name="", need_save=True, need_open=True):
        if name == "":
            name, submitted = GviewOperation.get_correct_view_name_input()
        else:
            submitted = True
        if not submitted:
            return None
        uuid = UUID.by_random()
        data = GViewData(uuid=uuid, name=name, nodes=nodes if nodes else {}, edges=edges if edges else {})
        # 去检查一下scene变大时,item的scene坐标是否会改变
        if need_save:
            GviewOperation.save(data)
        if need_open:
            Dialogs.open_view(gviewdata=data)
        if G.GViewAdmin_window:
            from ..bilink.dialogs.linkdata_grapher import GViewAdmin
            win: GViewAdmin = G.GViewAdmin_window
            win.init_data()
        return data

    @staticmethod
    def create_from_pair(cid_li: 'list[str|LinkDataPair]', name=""):
        nodes = {}
        for cid in cid_li:
            if isinstance(cid, LinkDataPair):
                cid = cid.card_id
            nodes[cid] = GviewOperation.依参数确定视图结点数据类型模板(编号=cid)
        GviewOperation.create(nodes=nodes, edges={}, name=name)

    @staticmethod
    def choose_insert(pairs_li: 'list[G.objs.LinkDataPair]' = None):
        all_gview = GviewOperation.load_all()
        check: dict[str, GViewData] = {}
        list(map(lambda data: check.__setitem__(data.name, data), all_gview))
        # name_li = list()
        viewname, okPressed = QInputDialog.getItem(None, "Get gview", "", set(check.keys()), 0, False)
        if not okPressed:
            return None
        Dialogs.open_grapher(pair_li=pairs_li, gviewdata=check[viewname], mode=GraphMode.view_mode)
        return check[viewname]

    @staticmethod
    def getDueCount(gview):
        """用于统计未复习数量"""
        from .configsModel import GViewData
        g: "GViewData" = gview

        now = now = datetime.now()
        return sum(1 for i in Filter.do(Map.do([索引 for 索引 in g.nodes.keys() if CardOperation.exists(索引)],
                                               lambda x: CardOperation.getLastNextRev(x)),
                                        lambda due: due[1] <= now))

    @staticmethod
    def 默认元信息模板(数据=None):
        默认值 = {
                字典键名.视图.创建时间: int(time.time()),
                字典键名.视图.上次访问: int(time.time()),
                字典键名.视图.上次编辑: int(time.time()),
                字典键名.视图.上次复习: int(time.time()),
                字典键名.视图.访问次数: 0
        }
        return Utils.字典缺省值填充器(默认值, 数据)

    @staticmethod
    def 默认视图边数据模板(数据=None):
        默认值 = {
                字典键名.边.名称: ""
        }
        return Utils.字典缺省值填充器(默认值, 数据)

    @staticmethod
    def 依参数确定视图结点数据类型模板(结点类型=枚举_视图结点类型.卡片, 数据=None, 编号=None):
        from . import models

        _ = 字典键名
        模型 = models.类型_视图结点模型()
        默认值模板 = {}
        类型对照 = {}
        for 名字 in 模型.__dict__:
            if isinstance(模型.__dict__[名字], models.类型_视图结点属性项):
                属性: models.类型_视图结点属性项 = 模型.__dict__[名字]
                if 属性.从上级读数据:
                    默认值模板[属性.字段名] = 属性.默认值
                    类型对照[属性.字段名] = 属性.值类型
        新值 = Utils.字典缺省值填充器(默认值模板, 数据, 类型对照)
        if 编号:
            新值[_.结点.描述] = CardOperation.desc_extract(编号) if 结点类型 == 枚举_视图结点类型.卡片 else GviewOperation.获取视图名字(编号)
        新值[_.结点.数据类型] = 结点类型
        # 新值[_.结点.描述] = GviewOperation.获取视图结点描述()
        return 新值


class Utils(object):
    @dataclasses.dataclass
    class MenuType:
        ankilink = 0

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

    # @staticmethod
    # def 主动备份():
    #     path,ok = QFileDialog.getExistingDirectory()

    @staticmethod
    def 正则合法性(值):
        try:
            re.compile(值)
            return True
        except:
            return False

    @staticmethod
    def make_backup_file_name(filename, path=""):
        file = "backup_" + datetime.now().strftime("%Y%m%d%H%M%S") + "_" + os.path.split(filename)[-1]
        if not path:
            return os.path.join(*os.path.split(filename)[:-1], file)
        else:
            return os.path.join(path, file)

    @staticmethod
    def percent_calc(total, count, begin, ratio):
        return math.ceil(count / total * ratio) + begin

    @staticmethod
    def emptystr(s):
        return not re.match(r"\S", s)

    @staticmethod
    def tooltip(s):
        if G.ISLOCALDEBUG:
            Utils.print(s)
        else:
            tooltip(s)

    @staticmethod
    def showInfo(s):
        if G.ISDEBUG:
            showInfo(s)

    @staticmethod
    def rect_center_pos(rect: 'Union[QRectF,QRect]'):
        return QPointF(rect.x() + rect.width() / 2, rect.y() + rect.height() / 2)

    # @staticmethod
    # def output():

    @staticmethod
    def print(*args, need_timestamp=True, need_logFile=True, **kwargs):

        if G.ISDEBUG:
            caller = sys._getframe(1).f_code.co_name
            caller2 = sys._getframe(2).f_code.co_name
            if need_timestamp:
                ts = (datetime.now().strftime("%Y%m%d%H%M%S"))
            else:
                ts = ""
            if need_logFile:
                f = open(G.src.path.logtext, "a", encoding="utf-8")
                print(f"{ts}|{caller2}>>{caller}:\n", *args, **kwargs, file=f)
            else:
                print(f"{ts}|{caller2}>>{caller}:\n", *args, **kwargs)

    @staticmethod
    def 字典默认键值对(默认值, 键名, 对应值字典, 类型对照: "dict" = None):

        if not 对应值字典 or not 键名 in 对应值字典:
            return 默认值
        else:
            if 类型对照:
                if type(对应值字典[键名]) in 字典键名.值类型.字典[类型对照[键名]]:
                    return 对应值字典[键名]
                else:
                    return 默认值
            else:
                return 对应值字典[键名]
        # if not 对应值 or 键名 not in 对应值:
        #     return 默认值
        # elif 类型对照 and type(对应值) in 字典键名.值类型.字典[类型对照[键名]]:
        #     return 对应值
        #
        #
        # return 默认值 if not 对应值 or 键名 not in 对应值 else 对应值[键名]

    @staticmethod
    def 字典缺省值填充器(默认值字典: dict, 对应值字典: "Optional[dict]" = None, 类型对照=None):
        新值 = {}
        for 键, 值 in 默认值字典.items():
            新值[键] = Utils.字典默认键值对(值, 键, 对应值字典, 类型对照)
        return 新值

    @staticmethod
    def 时间戳转日期(时间戳):
        return datetime.fromtimestamp(时间戳)

    @staticmethod
    def 日期转时间戳(日期):
        """
        日期为: YYYY-MM-DD格式
        """
        return int(time.mktime(time.strptime(日期, "%Y-%m-%d")))

    @staticmethod
    def 大文本提示框(文本, 取消模态=False, 尺寸=(600, 400)):
        _ = 字典键名.砖
        # 组合 = {_.框: QHBoxLayout(), _.子: [{_.件: QLabel()}]}
        # 组合[_.子][0][_.件].setText(Utils.html默认格式(文本))
        # 组合[_.子][0][_.件].setWordWrap(True)
        # 组合[_.子][0][_.件].setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        组合 = {_.框: QHBoxLayout(), _.子: [{_.件: QTextBrowser()}]}
        组合[_.子][0][_.件].setHtml(Utils.html默认格式(文本))
        对话框: QDialog = 组件定制.组件组合(组合, QDialog())
        if 取消模态:
            对话框.setModal(False)
            对话框.setWindowModality(Qt.NonModal)
        对话框.resize(*尺寸)
        对话框.exec()
        pass

    @staticmethod
    def html默认格式(内容):
        文本2 = "<p>" + 内容.replace("\n", "<br>") + "</p>"
        return """
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="UTF-8">
        <title></title>
        <style>
        </style>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Microsoft/vscode/extensions/markdown-language-features/media/markdown.css">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Microsoft/vscode/extensions/markdown-language-features/media/highlight.css">
        <style>
        body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe WPC', 'Segoe UI', system-ui, 'Ubuntu', 'Droid Sans', sans-serif;
        font-size: 17px;
        line-height: 1.6;
        }
        </style>
        <style>
        .task-list-item { list-style-type: none; } .task-list-item-checkbox { margin-left: -20px; vertical-align: middle; }
        </style>
        </head>
        <body class="vscode-body vscode-light">
        """ + 文本2 + """
        </body>
        </html>
                """

    class 时间处理:

        @staticmethod
        def 日偏移(日期=None, 偏移量: int = 0):

            """
            可用的指标: days
            返回时间戳"""
            if 日期 is None:
                日期 = datetime.today().date()
            偏移时间 = 日期 + timedelta(days=偏移量)
            时间戳 = int(time.mktime(偏移时间.timetuple()))
            return 时间戳

        @staticmethod
        def 月偏移(日期=None, 偏移量=0):
            if 日期 is None:
                日期 = datetime.today().date()
            日期年份 = 日期.timetuple().tm_year
            日期月份 = 日期.timetuple().tm_mon
            所求月份 = 12 if (日期月份 + 偏移量) % 12 == 0 else (日期月份 + 偏移量) % 12
            所求年份 = math.ceil((日期月份 + 偏移量) / 12) - 1 + 日期年份
            时间戳 = int(time.mktime(datetime(所求年份, 所求月份, 1).timetuple()))
            return 时间戳

        @staticmethod
        def 周偏移(指标=0):
            pass

        @staticmethod
        def 今日():
            return Utils.时间处理.日偏移()

        @staticmethod
        def 昨日():
            return Utils.时间处理.日偏移(None, -1)

        @staticmethod
        def 三天前():
            return Utils.时间处理.日偏移(None, -3)

        @staticmethod
        def 本周():
            今天周几 = datetime.today().timetuple().tm_wday
            return Utils.时间处理.日偏移(None, -今天周几)

        @staticmethod
        def 上周():
            今天周几 = datetime.today().timetuple().tm_wday
            return Utils.时间处理.日偏移(None, -今天周几 - 7)

        @staticmethod
        def 本月():
            return Utils.时间处理.月偏移(None, 0)

        @staticmethod
        def 一个月前():
            return Utils.时间处理.月偏移(None, -1)

        @staticmethod
        def 三个月前():
            """本月,上月,上上月
            3 2 1 12 11
            """
            return Utils.时间处理.月偏移(None, -3)

        @staticmethod
        def 六个月前():
            return Utils.时间处理.月偏移(None, -6)
            # 现在 = time.localtime()
            # time.mktime((现在.tm_year,现在.tm_mon,现在.tm_mday-现在.tm_wday,0,0,0,0,0,0))

    class 版本:

        @dataclasses.dataclass
        class 模型:
            version: "str"
            installed_at: "int" = int(time.time())

        @staticmethod
        def 版本冲突():
            本地版地址 = G.src.path.local_version
            网络版地址 = G.src.path.web_version
            当前插件地址 = G.src.path.root
            if Utils.版本.本地版被启用() and Utils.版本.网络版被启用() and 当前插件地址 == 本地版地址:
                showInfo(译.检测到同时启用了本地版与网络版插件)
                return True
            return False
        @staticmethod
        def 网络版被启用():
            网络版地址 = G.src.path.web_version
            if not os.path.exists(网络版地址):
                return False
            else:
                return json.load(open(os.path.join(网络版地址, "meta.json")))["disabled"] == False
            pass

        @staticmethod
        def 本地版被启用():
            本地版地址 = G.src.path.web_version
            if not os.path.exists(本地版地址):
                return False
            else:
                return json.load(open(os.path.join(本地版地址, "meta.json")))["disabled"] == False
            pass
            pass

        @staticmethod
        def 检查():
            版本路径 = G.src.path.current_version
            当前版本 = G.src.ADDON_VERSION
            if not os.path.exists(版本路径):
                Utils.版本.发出提醒()
                Utils.版本.创建版本文件()
            else:
                版本数据 = Utils.版本.读取版本文件()[-1]
                if 版本数据["version"] != 当前版本:
                    Utils.版本.发出提醒()
                    Utils.版本.添加版本()

        @staticmethod
        def 发出提醒():
            code = QMessageBox.information(None, 译.新版本介绍, 译.是否查看更新日志, QMessageBox_StandardButton.Yes | QMessageBox_StandardButton.No)
            if code == QMessageBox_StandardButton.Yes:
                Utils.版本.打开网址()

        @staticmethod
        def 打开网址():
            QDesktopServices.openUrl(QUrl("https://vu2emlw0ia.feishu.cn/docx/GCl6djBtiouRumxbbB4cbfnHn4c"))
            pass

        @staticmethod
        def 创建版本文件():
            版本路径 = G.src.path.current_version
            当前版本 = G.src.ADDON_VERSION
            Utils.版本.保存版本文件([Utils.版本.模型(当前版本).__dict__])

        @staticmethod
        def 添加版本():
            版本路径 = G.src.path.current_version
            当前版本 = G.src.ADDON_VERSION
            if not os.path.exists(版本路径):
                Utils.版本.创建版本文件()
            else:
                版本表 = Utils.版本.读取版本文件()
                版本表.append(Utils.版本.模型(当前版本).__dict__)
                Utils.版本.保存版本文件(版本表)

        @staticmethod
        def 保存版本文件(对象):
            版本路径 = G.src.path.current_version
            json.dump(对象, open(版本路径, "w", encoding="utf-8"))

        @staticmethod
        def 读取版本文件():
            版本路径 = G.src.path.current_version
            return sorted(json.load(open(版本路径, "r", encoding="utf-8")), key=lambda x: x["installed_at"])


class 组件定制:

    @staticmethod
    def 组件组合(组件树数据: "dict", 容器: "QWidget" = None) -> "QWidget|QDialog":
        if not 容器: 容器 = QWidget()
        基 = G.objs.Bricks
        布局, 组件, 子代, 占据 = 基.四元组

        def 子组合(组件树: "dict"):
            if 布局 in 组件树:
                the_layout: "QHBoxLayout|QVBoxLayout|QGridLayout" = 组件树[布局]
                the_layout.setContentsMargins(0, 0, 0, 0)
                for 孩子 in 组件树[子代]:
                    子组件 = 子组合(孩子)
                    if 布局 in 子组件:
                        the_layout.addLayout(子组件[布局])
                    else:
                        if isinstance(子组件[组件], QWidget):
                            the_layout.addWidget(子组件[组件], stretch=子组件[占据] if 占据 in 子组件 else 0)
                        else:
                            the_layout.addLayout(子组件[组件], stretch=子组件[占据] if 占据 in 子组件 else 0)

            return 组件树

        容器.setLayout(子组合(组件树数据)[布局])

        return 容器

    @staticmethod
    def 表格(单行选中=True, 不可修改=True):
        组件 = QTableView()
        if 单行选中:
            组件.setSelectionMode(QAbstractItemView.SingleSelection)
            组件.setSelectionBehavior(QAbstractItemView.SelectRows)
        if 不可修改:
            组件.setEditTriggers(QAbstractItemView.NoEditTriggers)
        组件.horizontalHeader().setStretchLastSection(True)
        return 组件

    @staticmethod
    def 模型(行标签: "list[str]" = None):
        组件 = QStandardItemModel()
        if 行标签:
            组件.setHorizontalHeaderLabels(行标签)
        return 组件

    @staticmethod
    def 单行输入框(占位符=None):
        组件 = QLineEdit()
        if 占位符:
            组件.setPlaceholderText(占位符)
        return 组件

    @staticmethod
    def 对话窗口(标题=None, 图标=None, 最大宽度=None, closeEvent=None, 尺寸=None, 宽度=None):
        组件 = QDialog()
        if 标题:
            组件.setWindowTitle(标题)
        if 图标:
            组件.setWindowIcon(图标)
        if 最大宽度:
            组件.setMaximumWidth(最大宽度)
        if closeEvent:
            组件.closeEvent = closeEvent
        if 尺寸:
            组件.resize(*尺寸)
        # 组件.adjustSize()

        return 组件

    @staticmethod
    def 文本框(文本="", 开启自动换行=True):
        组件 = QLabel(文本)
        组件.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        if 开启自动换行:
            组件.setWordWrap(True)
        return 组件

    @staticmethod
    def 按钮(图标地址=None, 文本=None, 触发函数=None):
        组件 = QPushButton()
        if 图标地址:
            组件.setIcon(QIcon(图标地址))
        if 文本:
            组件.setText(文本)
        if 触发函数:
            组件.clicked.connect(触发函数)
        return 组件

    @staticmethod
    def 长文本获取(预置内容=None, 标题=None, 获取回调: Callable[[str], Any] = None):
        布局, 组件, 子代 = 0, 1, 2
        result = []
        对话框布局 = {
                布局: QVBoxLayout(), 子代: [
                        {组件: QTextEdit(预置内容)},
                        {组件: QPushButton(QIcon(G.src.ImgDir.correct), "")}
                ]
        }
        对话框: "QDialog" = 组件定制.组件组合(对话框布局, 组件定制.对话窗口(标题))
        对话框布局[子代][1][组件].clicked.connect(lambda: [result.append(对话框布局[子代][0][组件].toPlainText()), 对话框.close()])

        对话框.exec()
        return result

    @staticmethod
    def 按钮_修改(文字="", 图标地址=G.src.ImgDir.rename):
        # 组件 = QPushButton(QIcon(图标地址),文字)

        return 组件定制.按钮(图标地址, 文字)

    @staticmethod
    def 按钮_提示(文字="", 图标地址=G.src.ImgDir.info, 触发函数=None):
        return 组件定制.按钮(图标地址, 文字, 触发函数)

    @staticmethod
    def 按钮_确认(文字="", 图标地址=G.src.ImgDir.correct, 触发函数=None):
        return 组件定制.按钮(图标地址, 文字, 触发函数)


#
# # 2023年2月15日23:42:11 砍掉 group_review功能, 全部相关代码被注释掉.
# # class GroupReview(object):
# #     """这是一套性能优化方案, GroupReview由于每次回答都要去数据库查询一遍,因此我们想了一招来新缓存
#     1,监听卡片的变化,
#     """
#
#     @staticmethod
#     def begin():
#         """入口,要从配置读东西,保存到某地,现在看来保存到G是最合适的,还需要设计数据结构"""
#         if Config.get().group_review.value == False:
#             return
#         GroupReview.build()
#         G.GroupReview_timer.timeout.connect(GroupReview.update)
#         G.GroupReview_timer.start(G.src.groupreview_update_interval)
#
#     @staticmethod
#     def build():
#         G.GroupReview_dict = GroupReviewDictInterface()
#         searchs: "list[str]" = Config.get().group_review_search_string.value
#         for search in searchs:
#             if search == "" or not re.search(r"\S", search):
#                 continue
#             if search.lower().startswith("gviewid"):
#                 if GviewOperation.exists(uuid=search[len("gviewid"):]):
#                     cids = Map.do(GviewOperation.load(search[len("gviewid"):]).nodes.keys(), lambda card_id: int(card_id))
#                 else:
#                     showInfo(f"{search} 不存在, 请删除\n can't find {search} , please delete it")
#                     cids = []
#             else:
#                 for_due = "(is:new OR is:due)" if Config.get().group_review_just_due_card.value else ""
#                 global_str = f"({Config.get().group_review_global_condition.value})"
#                 cids = mw.col.find_cards(f"({search}) {for_due} {global_str if global_str != '()' else ''}")
#             list(map(lambda cid: G.GroupReview_dict.card_group_insert(cid, search), cids))
#             list(map(lambda cid: G.GroupReview_dict.search_group_insert(cid, search), cids))
#         G.GroupReview_dict.build_union_search()
#         G.GroupReview_dict.update_version()
#
#     @staticmethod
#     def update():
#         """从配置表加载查询条件,然后去搜索,组织,并更新到数据库
#         这个函数需要定期执行,要给一些优化,
#         这里是重点对象, 首先执行一次联合查询, 然后检查原本在的是否消失, 原本不在的是否新增
#         https://blog.csdn.net/qq_34130509/article/details/89473503
#         """
#         if Config.get().group_review.value == False:
#             return
#
#         def search_result_not_changed():
#             """在这里,我们检查有没有必要更新"""
#             new_cids = set(mw.col.find_cards(G.GroupReview_dict.union_search))
#             old_cids = G.GroupReview_dict.card_group.keys()
#             need_add_card = new_cids - old_cids
#             need_del_card = old_cids - new_cids
#             return len(need_add_card) == 0 and len(need_del_card) == 0
#
#         # 临时文件没有变化则退出
#         if len(G.GroupReview_tempfile) == 0:
#             return
#         # 临时文件有变化,且临时文件cid不属于集合,则检查原集合是否有改动,无改动则退出
#         not_belong_to_card_group = len(G.GroupReview_tempfile & G.GroupReview_dict.card_group.keys()) == 0
#         if not_belong_to_card_group and search_result_not_changed():
#             G.GroupReview_tempfile.clear()
#             return
#         # 其他的筛选条件太难选了.到这里就直接建立吧
#         GroupReview.build()
#         G.GroupReview_tempfile.clear()
#
#     @staticmethod
#     def modified_card_record(note: "Note"):
#         """将卡片写到一个全局变量,作为集合"""
#         if not Config.get().group_review.value:
#             return
#         try:
#             G.GroupReview_tempfile |= set(note.card_ids())
#         except Exception as e:
#             Utils.print(e)
#             return
#
#     @staticmethod
#     def save_search_condition_to_config(browser: "Browser"):
#         """把搜索栏的内容拷贝下来粘贴到配置表"""
#         curr_string = browser.form.searchEdit.currentText()
#         if curr_string == "" or not re.search(r"\S", curr_string):
#             tooltip("不接受空格与空值<br>null string or empty string is not allowed")
#             return
#         GroupReview.addReviewCondition(curr_string)
#
#     @staticmethod
#     def saveGViewAsGroupReviewCondition(gviewId: "str"):
#         GroupReview.addReviewCondition("gviewid:" + gviewId)
#
#     @staticmethod
#     def addReviewCondition(condition):
#         c = Config.get()
#         setv = set(c.group_review_search_string.value)
#         setv.add(condition)
#         c.group_review_search_string.value = list(setv)
#         Config.save(c)
#         G.signals.on_group_review_search_string_changed.emit()
#         tooltip("已添加到群组复习条件列表: " + condition)
#

class BaseConfig(metaclass=abc.ABCMeta):
    """一切配置表的基类
    TODO 把Config中可以抽象的功能提升到这里来
    """

    @staticmethod
    def get_validate(item: "ConfigModelItem"):

        w = ConfigModel.Widget
        d = {  # 不写在这的必须要有自己的validate
                w.spin     : lambda x, itemSelf: type(x) == int and itemSelf.limit[0] <= x <= itemSelf.limit[1],
                w.radio    : lambda x, itemSelf: type(x) == bool,
                w.line     : lambda x, itemSelf: type(x) == str,
                w.label    : lambda x, itemSelf: type(x) == str,
                w.text     : lambda x, itemSelf: type(x) == str,
                w.combo    : lambda x, itemSelf: x in itemSelf.limit,
                w.customize: lambda x, itemSelf: True
        }

        if item.validate(item.value, item) is None:
            # write_to_log_file(str(item.validate(item.value, item)))
            return d[item.component]
        else:
            return item.validate

    @staticmethod
    def makeConfigRow(配置项名, 配置项: "ConfigModelItem", 上级: "baseClass.Standard.配置表容器"):
        """这里制作配置表中的每一项"""
        value, validate, widgetType = 配置项.value, 配置项.validate, 配置项.component
        typ = ConfigModel.Widget
        tipbutton = QToolButton()
        tipbutton.setIcon(QIcon(G.src.ImgDir.help))
        tipbutton.clicked.connect(lambda: Utils.大文本提示框("<br>".join(配置项.instruction)))
        container = QWidget(parent=上级)
        layout = QHBoxLayout()
        w = None
        if widgetType == typ.spin:
            w = QSpinBox(container)
            w.setRange(配置项.limit[0], 配置项.limit[1])
            w.setValue(value)
            w.valueChanged.connect(lambda x: 配置项.setValue(x))
            配置项.设值到组件 = lambda 值: w.setValue(值)
        elif widgetType == typ.line:
            w = QLineEdit()
            w.setText(value)
            w.textChanged.connect(lambda: 配置项.setValue(w.text()))
            配置项.设值到组件 = lambda 值: w.setText(值)
        elif widgetType == typ.combo:
            w = QComboBox(container)
            list(map(lambda x: w.addItem(x.name, x.value), 配置项.limit))
            w.setCurrentIndex(w.findData(value))
            w.currentIndexChanged.connect(lambda x: 配置项.setValue(w.currentData(role=Qt.UserRole)))
            配置项.设值到组件 = lambda 值: w.setCurrentIndex(w.findData(值))
        elif widgetType == typ.radio:
            w = QRadioButton(container)
            w.setChecked(value)
            w.clicked.connect(lambda: 配置项.setValue(w.isChecked()))
            配置项.设值到组件 = lambda 值: w.setChecked(值)
        elif widgetType == typ.label:
            w = QLabel(container)
            w.setText(配置项.display(value))
            配置项.设值到组件 = lambda 值: w.setText(值)
        elif widgetType == typ.text:
            w = QTextEdit(container)
            w.setContentsMargins(0, 0, 0, 0)
            w.setText(value)
            配置项.设值到组件 = lambda 值: w.setText(值)
        elif widgetType == typ.customize:
            x2 = 配置项.customizeComponent()(配置项, 上级)  # 这个地方的警告去不掉, 很烦人.
            配置项.设值到组件 = lambda 值: x2.SetupData(值)
            w = x2.View
        else:
            raise ValueError(f"配置项:{配置项名},未知组件方案")
        配置项.widget = w
        layout.addWidget(w)
        layout.addWidget(tipbutton)
        container.setLayout(layout)
        return container

    @staticmethod
    def makeConfigDialog(调用者, 数据: "BaseConfigModel", 关闭时回调: "Callable[[BaseConfigModel],None]" = None):
        """
        关闭时回调
        TODO:这里的内容要整理到Config的父类中
        onclose 接受一个高阶函数: Callable[cfg,Callable[]] 这个高阶函数的参数是本函数的第一个参数cfg
        """

        # from .configsModel import BaseConfigModel
        # print(f"in makeConfigDialog data={数据}")
        @dataclasses.dataclass()
        class 分页字典项:
            widget: QWidget = dataclasses.field(default_factory=QWidget)
            layout: QFormLayout = dataclasses.field(default_factory=QFormLayout)

        容器 = baseClass.Standard.配置表容器(数据, 调用者=调用者)

        总布局 = QVBoxLayout()
        分栏 = QTabWidget()

        分栏字典: "dict[Any,分页字典项]" = {}
        for 名, 值 in 数据.get_editable_config().items():
            if 值.component == ConfigModel.Widget.none:
                continue
            if 值.tab_at not in 分栏字典:
                分栏字典[值.tab_at]: '分页字典项' = 分页字典项()
            item = BaseConfig.makeConfigRow(名, 值, 容器)
            分栏字典[值.tab_at].layout.addRow(rosetta(名), item)
        for 名, 值 in 分栏字典.items():
            值.widget.setLayout(值.layout)
            分栏.addTab(值.widget, 名)
        滚动组件 = QScrollArea(容器)
        滚动组件.setWidget(分栏)
        滚动组件.setContentsMargins(0, 0, 0, 0)
        滚动组件.setMinimumHeight(500)
        滚动组件.setWidgetResizable(True)
        滚动组件.setAlignment(Qt.AlignCenter)
        总布局.addWidget(滚动组件, stretch=1)
        容器.setLayout(总布局)
        # 容器.resize(int(分栏.width() * 1.1), 500)
        容器.setContentsMargins(0, 0, 0, 0)
        容器.setWindowIcon(QIcon(G.src.ImgDir.config))
        容器.setWindowTitle("配置表/configuration")
        if 关闭时回调:
            容器.rejected.connect(lambda: 关闭时回调(数据))

        return 容器


class IntroductionOperation:
    pass


class GviewConfigOperation(BaseConfig):

    @staticmethod
    def 获取结点角色数据源(gview_uuid=None, gview_data: "GViewData" = None) -> "list[str]":

        if gview_uuid:
            data = GviewOperation.load(gview_uuid)
        else:
            data = gview_data
        if data.config:
            from ast import literal_eval
            role_enum = literal_eval(objs.Record.GviewConfig.readModelFromDB(data.config).data.node_role_list.value)
            return role_enum
        else:
            return []

    @staticmethod
    def 获取结点角色名(视图数据: GViewData, 结点编号, 配置数据: "GviewConfig" = None):
        角色选中序号表 = 视图数据.nodes[结点编号].角色.值
        角色列表 = eval((GviewConfigOperation.从数据库读(视图数据.config) if not 配置数据 else 配置数据).data.node_role_list.value)
        return [角色列表[角色序号] for 角色序号 in 角色选中序号表 if 角色序号 in range(0, len(角色列表))]

    @staticmethod
    def 漫游路径生成之深度优先遍历(视图数据: GViewData, 结点队列: "list[str]", 起点: "list[str]"):
        Utils.print("深度优先排序开始")
        栈 = []
        结点集 = set(结点队列)
        已访问 = []
        边集 = 视图数据.edges.keys()
        while 结点集:
            if not 栈:
                栈.append(结点集.pop() if not 起点 else 起点.pop(0))
            while 栈:
                结点 = 栈.pop()
                已访问.append(结点)
                结点为起点的边集 = [边 for 边 in 边集 if 边.startswith(结点)]
                for 边 in 结点为起点的边集:
                    终点 = 边.split(",")[1]
                    if 终点 not in 已访问 and 终点 not in 栈:
                        栈.append(终点)
            结点集 -= set(已访问)
        return 已访问
        pass

    @staticmethod
    def 漫游路径生成之广度优先遍历(视图数据: GViewData, 结点队列: "list[str]", 起点: "list[str]"):
        队 = []
        结点集 = set(结点队列)
        已访问 = []
        边集 = 视图数据.edges.keys()
        while 结点集:
            if not 队:
                队.insert(0, 结点集.pop() if not 起点 else 起点.pop(0))
            while 队:
                结点 = 队.pop()
                已访问.append(结点)
                结点为起点的边集 = [边 for 边 in 边集 if 边.startswith(结点)]
                for 边 in 结点为起点的边集:
                    终点 = 边.split(",")[1]
                    if 终点 not in 已访问 and 终点 not in 队:
                        队.insert(0, 终点)

            结点集 -= set(已访问)
        return 已访问
        pass

    @staticmethod
    def 漫游路径生成之多级排序(前一项, 后一项, 视图数据: GViewData, 排序表: "List[Iterable[str,str]]"):
        """默认升序排序,默认的比较是 前一项>后一项"""
        前一项结点数据, 后一项结点数据 = 视图数据.nodes[前一项], 视图数据.nodes[后一项]
        _ = 字典键名
        for 排序字段, 升降序 in 排序表:
            if 前一项结点数据[排序字段].值 == 后一项结点数据[排序字段].值:
                continue
            else:
                return (前一项结点数据[排序字段].值 - 后一项结点数据[排序字段].值) * (1 if 升降序 == _.上升 else -1)
        return 0
        pass

    @staticmethod
    def 漫游路径生成之加权排序(前一项, 后一项, 视图数据: GViewData, 排序公式):
        return eval(排序公式, *GviewConfigOperation.获取eval可用变量与函数(视图数据, 前一项)) - eval(排序公式, *GviewConfigOperation.获取eval可用变量与函数(视图数据, 后一项))

    @staticmethod
    def 漫游路径生成(视图数据: GViewData, 配置数据: objs.Record.GviewConfig, 队列: "list[str]",选中队列=None):
        _ = 字典键名.路径生成模式

        if not 视图数据.config:
            raise ValueError('config is None')
        生成模式 = 配置数据.data.roaming_path_mode.value
        if 生成模式 == _.随机排序:
            random.shuffle(队列)
            return 队列
        elif 生成模式 == _.多级排序:
            待选表, 选中序号 = 配置数据.data.cascading_sort.value
            if 选中序号 >= len(待选表):
                选中序号 = -1
                配置数据.data.cascading_sort.value[1] = -1

            排序表: "List[Iterable[str,str]]" = eval(待选表[选中序号]) if len(待选表) > 选中序号 >= 0 else baseClass.漫游预设.默认多级排序规则
            队列.sort(key=cmp_to_key(lambda x, y: GviewConfigOperation.漫游路径生成之多级排序(x, y, 视图数据, 排序表)))
            return 队列
        elif 生成模式 == _.加权排序:
            待选表, 选中序号 = 配置数据.data.weighted_sort.value
            if 选中序号 >= len(待选表):
                选中序号 = -1
                配置数据.data.weighted_sort.value[1] = -1

            公式 = 待选表[选中序号] if len(待选表) > 选中序号 >= 0 else baseClass.漫游预设.默认加权排序规则
            队列.sort(key=cmp_to_key(lambda x, y: GviewConfigOperation.漫游路径生成之加权排序(x, y, 视图数据, 公式)), reverse=True)
            return 队列
        else:
            图排序模式 = 配置数据.data.graph_sort.value
            入度零结点 = [结点编号 for 结点编号 in 队列 if 视图数据.nodes[结点编号].入度.值==0]
            开始结点 = 入度零结点 if 入度零结点 else [random.choice(队列)]
            if 配置数据.data.roamingStart.value == 字典键名.视图配置.roamingStart.手动选择卡片开始:
                可能的开始结点 = [结点编号 for 结点编号 in 队列 if 视图数据.nodes[结点编号].漫游起点.值]
                if len(可能的开始结点) > 0:
                    开始结点 = 可能的开始结点+开始结点
                if 选中队列:
                    开始结点 = 选中队列+开始结点
                Utils.print("开始结点={开始结点}".format(开始结点=开始结点))
            if 图排序模式 == 字典键名.视图配置.图排序模式.广度优先遍历:
                return GviewConfigOperation.漫游路径生成之广度优先遍历(视图数据, 队列, 开始结点)
            else:
                return GviewConfigOperation.漫游路径生成之深度优先遍历(视图数据, 队列, 开始结点)

    @staticmethod
    def 满足过滤条件(视图数据: GViewData, 结点编号: "str", 配置数据: objs.Record.GviewConfig):
        """传到这里的参数, 必须满足视图数据.config存在"""
        if not 视图数据.config:
            raise ValueError('config is None')
        列表, 选项 = 配置数据.data.roaming_node_filter.value

        if 选项 >= len(列表):
            配置数据.data.roaming_node_filter.value[1] = 选项 = -1

        结点数据 = 视图数据.nodes[结点编号]
        if 结点数据.必须复习.值:
            return True
        elif not 结点数据.需要复习.值:
            return False
        elif 选项 == -1:
            默认过滤条件 = baseClass.漫游预设.默认过滤规则
            全局, 局部 = GviewConfigOperation.获取eval可用变量与函数(视图数据, 结点编号)
            return eval(默认过滤条件, 全局, 局部)
        else:
            return eval(列表[选项], *GviewConfigOperation.获取eval可用变量与函数(视图数据, 结点编号))
        pass

    @staticmethod
    def 获取eval可用变量与函数的说明(指定变量类型=None):
        from . import models

        说明 = f"<h1>{译.可用变量与函数}</h1>"

        结点属性模型 = models.类型_视图结点模型()
        视图属性模型 = models.类型_视图本身模型()

        _ = 字典键名
        for 属性名 in 结点属性模型.获取可访变量(指定变量类型).keys():
            说明 += fr"<p><b>{属性名}</b>,{结点属性模型[属性名].变量使用的解释()}</p>"
        for 属性名 in 视图属性模型.获取可访变量(指定变量类型).keys():
            说明 += fr"<p><b>{属性名}</b>,{视图属性模型[属性名].变量使用的解释()}</p>"
        说明 += f"<p><b>{_.视图配置.结点角色表}</b>,mean:{译.角色待选列表},type:list,example:['apple','banana']</p>"
        说明 += f"<p><b>time_xxxx</b>,{译.所有time开头的变量都是时间戳}:{', '.join([_.时间.今日, _.时间.昨日, _.时间.上周, _.时间.本周, _.时间.一个月前, _.时间.本月, _.时间.三天前, _.时间.三个月前, _.时间.六个月前])}</p>"
        说明 += f"<p><b>{_.时间.转时间戳}</b>,example:to_timestamp('2023-2-18')->1676649600</p>"
        说明 += f"<p><b>supported python module:</b> math,random,re</p>"
        return BeautifulSoup(说明, "html.parser").__str__()

    @staticmethod
    def 获取eval可用函数():
        _ = 字典键名.时间
        return {
                _.转时间戳: Utils.日期转时间戳,
                _.今日  : Utils.时间处理.今日(),
                _.昨日  : Utils.时间处理.昨日(),
                _.上周  : Utils.时间处理.上周(),
                _.本周  : Utils.时间处理.本周(),
                _.一个月前: Utils.时间处理.一个月前(),
                _.本月  : Utils.时间处理.本月(),
                _.三天前 : Utils.时间处理.三天前(),
                _.三个月前: Utils.时间处理.三个月前(),
                _.六个月前: Utils.时间处理.六个月前(),
        }

    @staticmethod
    def 获取eval可用字面量(指定变量类型=None):
        from . import models
        return {**models.类型_视图本身模型().获取可访字面量(指定变量类型=指定变量类型), **models.类型_视图结点模型().获取可访字面量(指定变量类型=指定变量类型)}
        pass

    @staticmethod
    def 获取eval可用变量与函数(视图数据: GViewData = None, 结点索引=None, 指定变量类型=None):
        """"""
        from . import models
        _ = baseClass.枚举命名
        new_globals = globals().copy()
        结点变量 = (models.类型_视图结点模型().获取可访变量(指定变量类型=指定变量类型) if not 视图数据 else 视图数据.nodes[结点索引].获取可访变量(指定变量类型=指定变量类型))
        视图变量 = (models.类型_视图本身模型().获取可访变量(指定变量类型=指定变量类型) if not 视图数据 else 视图数据.meta_helper.获取可访变量(指定变量类型=指定变量类型))
        配置变量 = eval(GviewConfigOperation.从数据库读(视图数据.config).data.node_role_list.value) if 视图数据 and 视图数据.config else []
        函数变量 = GviewConfigOperation.获取eval可用函数()
        变量对儿 = [new_globals,
                {
                        **结点变量,
                        **视图变量,
                        **函数变量,
                        _.视图配置.结点角色表: 配置变量
                }
                ]
        return 变量对儿

    @staticmethod
    def 从数据库读(标识):
        return objs.Record.GviewConfig.readModelFromDB(标识)

    @staticmethod
    def 从数据库删除(标识: str):
        if type(标识) != str:
            raise ValueError("类型不匹配")
        DB = G.DB
        DB.go(DB.table_GviewConfig)
        DB.excute_queue.append(f"delete from GRAPH_VIEW_CONFIG where uuid='{标识}'")
        DB.commit(lambda x: Utils.print(x, need_logFile=True))
        # G.DB.go(G.DB.table_GviewConfig).delete(objs.Logic.EQ(uuid=f"'{标识}'")).commit(lambda x:Utils.print(x,need_logFile=True))

    @staticmethod
    def 存在(标识):
        if not 标识:
            return False
        DB = G.DB
        return DB.go(DB.table_GviewConfig).exists(DB.EQ(uuid=标识))

    @staticmethod
    def 指定视图配置(视图记录: "GViewData|str", 新配置记录: "objs.Record.GviewConfig|str|None" = None, need_save=True):

        def 删除前配置中的当前视图():
            前配置记录 = GviewConfigOperation.从数据库读(视图记录.config)
            应用前配置的视图表: "list[str]" = 前配置记录.data.appliedGview.value
            # Utils.print(f"former model applied config table, before append={应用前配置的视图表}", need_logFile=True)
            if 视图记录.uuid in 应用前配置的视图表:
                应用前配置的视图表.remove(视图记录.uuid)
                if len(应用前配置的视图表) == 0:
                    # Utils.print(f"应用前配置的视图表={应用前配置的视图表},下面要删除这个配置了", need_logFile=True)
                    GviewConfigOperation.从数据库删除(前配置记录.uuid)
                else:
                    前配置记录.data.appliedGview.setValue(应用前配置的视图表)
                    前配置记录.saveModelToDB()
            # Utils.print(f"former model applied config table, after append={应用前配置的视图表}", need_logFile=True)

        def 将当前视图添加到现配置的支配表中():
            应用配置视图表: "list[str]" = 新配置记录.data.appliedGview.value
            # Utils.print(f"new model uuid={新配置记录.uuid}, appliedGview before append =  {应用配置视图表}", need_logFile=True)

            if 视图记录.uuid not in 应用配置视图表:
                应用配置视图表.append(视图记录.uuid)
                新配置记录.data.appliedGview.setValue(应用配置视图表)
            视图记录.config = 新配置记录.uuid
            # GviewOperation.save(视图记录)
            新配置记录.data.元信息.确定保存到数据库 = True
            新配置记录.saveModelToDB()
            # Utils.print(f"new model uuid={新配置记录.uuid}, appliedGview after append =  {应用配置视图表}, gview.config = {视图记录.config}", need_logFile=True)

        if type(视图记录) == str:
            视图记录 = GviewOperation.load(视图记录)

        if 新配置记录 is None:
            新配置记录 = objs.Record.GviewConfig()
        elif type(新配置记录) == str:
            新配置记录 = objs.Record.GviewConfig.readModelFromDB(新配置记录)

        if 视图记录.config and objs.Record.GviewConfig.静态_存在于数据库中(视图记录.config):
            删除前配置中的当前视图()

        将当前视图添加到现配置的支配表中()
        if need_save:
            GviewOperation.save(视图记录)
        Utils.print("assign view over ", need_logFile=True)

    @staticmethod
    def 移除视图配置(视图标识: "str", 配置标识: "str"):
        视图模型 = GviewOperation.load(uuid=视图标识)
        视图模型.config = ""
        GviewOperation.save(视图模型)

    @staticmethod
    def 据关键词同时搜索视图与配置数据库表(关键词: "str") -> "list[tuple[str,str,str]]":
        """返回一个列表,里面是[类型,名称,uuid]三元组
        """

        G.DB.go(G.DB.table_GviewConfig).excute_queue.append(f"""
        select "{译.视图}",name,uuid from GRAPH_VIEW_TABLE  where name like "%{关键词}%" and config != ""
        union 
        select "{译.配置}",name,uuid from GRAPH_VIEW_CONFIG where name like "%{关键词}%"
        order by name
        """)
        result = G.DB.commit()
        return list(result)

    pass


class Config(BaseConfig):
    """TODO 这里需要抽象出一个父类, 实现widget继承"""

    @staticmethod
    def read(cfg: ConfigModel, data: "dict"):
        for key, value in data.items():
            if key in cfg.get_editable_config():
                item: "ConfigModelItem" = cfg[key]
                # if not validate_dict[item.component](value,item):
                if not Config.get_validate(item)(value, item):
                    showInfo(f"{key}={value}<br>is invalid, overwritten")
                    # write_to_log_file(f"{key}={value}\n"+str(Config.get_validate(item)(value,item)),need_timestamp=True)
                    continue
                cfg[key].value = value

    @staticmethod
    def get() -> ConfigModel:
        """静态方法,直接调用即可"""
        if G.CONFIG is None:
            template = ConfigModel()
            if os.path.exists(G.src.path.userconfig):
                file_str = open(G.src.path.userconfig, "r", encoding="utf-8").read()
            else:
                file_str = template.to_json_string()
            try:
                data = json.loads(file_str)
                Config.read(template, data)
                G.CONFIG = template
            except:
                backfile = Utils.make_backup_file_name(G.src.path.userconfig)
                if os.path.exists(G.src.path.userconfig):
                    shutil.copy(G.src.path.userconfig, backfile)
                    showInfo(f"config file load failed, backup and overwrite")
                Config.save(template)

        return G.CONFIG

    @staticmethod
    def save(config: ConfigModel = None, path=None):
        # showInfo("Config.save")
        if path is None: path = G.src.path.userconfig
        if config is None: config = ConfigModel()
        template = ConfigModel()
        Config.read(template, config.get_dict())
        template.save_to_file(path)
        G.CONFIG = template


class GrapherOperation:

    @staticmethod
    def 判断视图已经打开():
        from .graphical_bilinker import VisualBilinker
        if isinstance(G.mw_grapher, VisualBilinker):
            bilinker: VisualBilinker = G.mw_grapher
            return bilinker
        else:
            return None

    @staticmethod
    def refresh():
        from ..bilink.dialogs.linkdata_grapher import Grapher
        if isinstance(G.mw_grapher, Grapher):
            G.mw_grapher.on_card_updated.emit(None)
        for gviewName in G.mw_gview.keys():
            if isinstance(G.mw_gview[gviewName], Grapher):
                G.mw_gview[gviewName].on_card_updated.emit(None)

    @staticmethod
    def updateDue(card_id: str):
        """当在reviewer中复习了卡片后, 在相关的领域内也要更新对应的Due"""
        from ..bilink.dialogs.linkdata_grapher import Grapher

        if isinstance(G.mw_grapher, Grapher):
            if card_id in G.mw_grapher.data.node_dict.keys():
                G.mw_grapher.data.updateNodeDue(card_id)

        for gviewName in G.mw_gview.keys():
            if isinstance(G.mw_gview[gviewName], Grapher):
                if card_id in G.mw_gview[gviewName].data.node_dict.keys():
                    G.mw_gview[gviewName].data.updateNodeDue(card_id)

        # return sum(filter(g.data.node_dict.keys()))


class GlobalLinkDataOperation:
    """针对链接数据库的操作,
    这里的LinkDataOperation.bind/unbind和LinkPoolOperation中的link/unlink是类似但不同,不冲突.
    因为那是一个link池里的操作,而这不是, 这是一个普通的链接操作
    """

    @staticmethod
    def read_from_db(card_id):
        from ..bilink.linkdata_admin import read_card_link_info
        return read_card_link_info(card_id)

    @staticmethod
    def write_to_db(card_id, data):
        from ..bilink.linkdata_admin import write_card_link_info
        return write_card_link_info(card_id, data)

    @staticmethod
    def update_desc_to_db(pair: "LinkDataPair"):
        """仅根据pair的desc信息更新,别的不做"""
        data = GlobalLinkDataOperation.read_from_db(pair.card_id)
        data.self_data.desc = pair._desc
        data.self_data.get_desc_from = G.objs.LinkDescFrom.DB
        data.save_to_DB()
        if pair.get_desc_from == G.objs.LinkDescFrom.Field:
            tooltip(Translate.描述已修改但是___, period=6000)

    @staticmethod
    def bind(card_idA: 'Union[str,LinkDataJSONInfo]', card_idB: 'Union[str,LinkDataJSONInfo]', needsave=True):
        """needsave关闭后,需要自己进行save"""
        if isinstance(card_idA, LinkDataJSONInfo) and isinstance(card_idB, LinkDataJSONInfo):
            cardA, cardB = card_idA, card_idB
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
    def unbind(card_idA: 'Union[str,LinkDataJSONInfo]', card_idB: 'Union[str,LinkDataJSONInfo]', needsave=True):
        """needsave关闭后,需要自己进行save"""
        from ..bilink import linkdata_admin

        cardA = card_idA if isinstance(card_idA, LinkDataJSONInfo) else linkdata_admin.read_card_link_info(card_idA)
        cardB = card_idB if isinstance(card_idB, LinkDataJSONInfo) else linkdata_admin.read_card_link_info(card_idB)

        if cardB.self_data in cardA.link_list:
            cardA.remove_link(cardB.self_data)
            if needsave: cardA.save_to_DB()
        if cardA.self_data in cardB.link_list:
            cardB.remove_link(cardA.self_data)
            if needsave: cardB.save_to_DB()

    @staticmethod
    def backup(cfg: "ConfigModel", now=None):
        if not now: now = datetime.now().timestamp()
        db_file = G.src.path.DB_file
        path = cfg.auto_backup_path.value
        backup_name = Utils.make_backup_file_name(db_file, path)
        shutil.copy(db_file, backup_name)
        cfg.last_backup_time.value = now
        cfg.save_to_file(G.src.path.userconfig)

    @staticmethod
    def need_backup(cfg: "ConfigModel", now) -> bool:
        if not cfg.auto_backup.value:
            return False
        last = cfg.last_backup_time.value
        if (now - last) / 3600 < cfg.auto_backup_interval.value:
            return False
        return True


class CardTemplateOperation:
    @staticmethod
    def GetModelFromId(Id: int):
        if G.ISLOCALDEBUG:
            return None
        return mw.col.models.get(Id)

    @staticmethod
    def GetNameFromId(Id: int):
        return CardTemplateOperation.GetModelFromId(Id)[""]

    @staticmethod
    def GetAllTemplates():
        if G.ISLOCALDEBUG:
            return []
        return mw.col.models.all()


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


class ReviewerOperation:
    @staticmethod
    def time_up_buzzer(card: "Card", starttime):
        def buzzer(starttime, card: "Card"):
            if starttime == G.cardChangedTime and mw.state == "review" and card.id == mw.reviewer.card.id:
                if Config.get().time_up_skip_click.value:
                    ReviewerOperation.time_up_auto_action(card)
                    tooltip(f"{Config.get().time_up_buzzer.value} {rosetta('秒')} {rosetta('时间到')}")
                    return
                d = widgets.message_box_for_time_up(Config.get().time_up_buzzer.value)
                if d == Translate.默认操作:
                    ReviewerOperation.time_up_auto_action(card)
                    return
                elif d == Translate.重新计时:
                    starttime = G.cardChangedTime = time.time()
                    timegap = Config.get().time_up_buzzer.value
                    QTimer.singleShot(timegap * 1000, lambda: buzzer(starttime, card))
                else:
                    return

        timegap = Config.get().time_up_buzzer.value
        QTimer.singleShot(timegap * 1000, lambda: buzzer(starttime, card))

    @staticmethod
    def time_up_auto_action(card: "Card"):
        def pick_date():
            value, ok = QInputDialog.getInt(None, "time_up_auto_action", "请输入推迟天数", 0)
            if not ok:
                value = 0
            return value
            pass

        actcode = Config.get().time_up_auto_action.value
        if actcode == 0: return
        actions = {}
        list(map(lambda k: actions.__setitem__(k, lambda card: CardOperation.answer_card(card, k)), range(1, 5)))
        list(map(lambda kv: actions.__setitem__(kv[1], lambda card: CardOperation.delay_card(card, kv[1])), [(5, 1), (6, 3), (7, 7), (8, 30)]))
        actions[9] = lambda _card: CardOperation.delay_card(_card, pick_date())
        actions[10] = lambda _card: mw.reviewer._showAnswer()
        actions[actcode](card)

    @staticmethod
    def refresh():
        pass


class BrowserOperation:
    @staticmethod
    def search(s) -> "Browser":
        """注意,如果你是自动搜索,需要自己激活窗口"""
        if ISLOCALDEBUG:
            return
        browser: "Browser" = BrowserOperation.get_browser()
        # if browser is not None:
        if not isinstance(browser, Browser):
            browser: "Browser" = dialogs.open("Browser", mw)

        browser.search_for(s)
        return browser

    @staticmethod
    def refresh():
        browser: "Browser" = BrowserOperation.get_browser()
        if isinstance(browser, Browser):
            # if dialogs._dialogs["Browser"][1] is not None:
            browser.sidebar.refresh()
            browser.model.reset()
            browser.editor.setNote(None)

    @staticmethod
    def get_browser(OPEN=False):
        browser: "Browser" = dialogs._dialogs["Browser"][1]
        if not isinstance(browser, Browser) and OPEN:
            browser = dialogs.open("Browser")
        # browser.forget_cards
        return browser

    @staticmethod
    def get_selected_card():
        browser = BrowserOperation.get_browser(OPEN=True)
        card_ids = browser.selected_cards()
        result = [LinkDataPair(str(card_id), CardOperation.desc_extract(card_id)) for card_id in card_ids]
        return result


class EditorOperation:
    @staticmethod
    def make_PDFlink(editor: "Editor"):
        """复制文件路径,或者file协议链接,或者打开对话框后再粘贴"""
        clipboard = QApplication.clipboard()
        text = clipboard.text()

        dialog = widgets.Dialog_PDFUrlTool()
        dialog.widgets[Translate.pdf路径].setText(text)
        dialog.widgets[Translate.pdf默认显示页码].setChecked(Config.get().PDFLink_show_pagenum.value)
        config = PDFLink.GetPathInfoFromPreset(text)
        if config is not None:
            dialog.widgets[Translate.pdf名字].setText(config[1])
            dialog.widgets[Translate.pdf默认显示页码].setChecked(config[3])
            dialog.widgets[Translate.pdf样式].setText(config[2])

        dialog.exec()
        # if dialog.needpaste:tooltip("neeapaste")
        if dialog.needpaste: editor.onPaste()
        return text


class CustomProtocol:
    # 自定义url协议,其他的都是固定的,需要获取anki的安装路径

    @staticmethod
    def set():
        root = QSettings("HKEY_CLASSES_ROOT", QSettings.Format.NativeFormat)
        root.beginGroup("ankilink")
        root.setValue("Default", "URL:Ankilink")
        root.setValue("URL Protocol", "")
        root.endGroup()
        command = QSettings(r"HKEY_CLASSES_ROOT\anki.ankiaddon\shell\open\command", QSettings.Format.NativeFormat)
        shell_open_command = QSettings(r"HKEY_CLASSES_ROOT\ankilink\shell\open\command", QSettings.Format.NativeFormat)
        shell_open_command.setValue(r"Default", command.value("Default"))

    @staticmethod
    def exists():
        setting = QSettings(r"HKEY_CLASSES_ROOT\ankilink", QSettings.Format.NativeFormat)
        return len(setting.childGroups()) > 0


class CardOperation:

    @staticmethod
    def 描述更新(card_id):
        最新描述 = CardOperation.desc_extract(card_id)
        含card_id视图集 = GviewOperation.find_by_card([card_id])
        for 视图数据 in 含card_id视图集:
            视图窗口 = GviewOperation.判断视图已经打开(视图数据.uuid)
            if 视图窗口:
                视图窗口.data.gviewdata.设置结点属性(card_id, 字典键名.结点.描述, 最新描述)
        图形助手窗口 = GrapherOperation.判断视图已经打开()
        if 图形助手窗口 and card_id in 图形助手窗口.data.node_dict:
            图元 = 图形助手窗口.data.node_dict[card_id]
            图元.desc = 最新描述

    @staticmethod
    def 判断卡片被独立窗口预览(card_id):
        结果 = None
        from ..bilink.dialogs.custom_cardwindow import SingleCardPreviewer
        if card_id in G.mw_card_window and isinstance(G.mw_card_window[card_id], SingleCardPreviewer):
            结果: SingleCardPreviewer = G.mw_card_window[card_id]
        return 结果

    @staticmethod
    def 删除不存在的结点(结点编号集: "list[str]"):
        Gview = GviewOperation
        Card = CardOperation
        DB = G.DB
        DB.go(DB.table_linkinfo)
        for 结点编号 in 结点编号集:
            视图数据集 = Gview.找到结点所属视图(结点编号)
            for 视图数据 in 视图数据集:
                视图窗口 = Gview.判断视图已经打开(视图数据.uuid)
                if 视图窗口 is not None:
                    视图窗口.remove_node(结点编号)
                    视图窗口.data.node_edge_packup()
            bilinker = GrapherOperation.判断视图已经打开()
            if bilinker and 结点编号 in bilinker.data.node_dict:
                bilinker.remove_node(结点编号)
            if 结点编号.isdigit():
                卡片独立窗口 = Card.判断卡片被独立窗口预览(结点编号)
                if 卡片独立窗口:
                    卡片独立窗口.close()
                # if DB.exists(DB.EQ(card_id=结点编号)):
                #     全局链接数据 = DB.select()
                # 数字类型的必然是卡片, 是卡片就要考虑他有没有全局链接数据

                pass
                # if DB.exists(DB.EQ(card_id))
                # 全局链接数据 = DB.select(DB.EQ())
                # for 文外链接 in 全局链接数据.link_list:
                #     GlobalLinkDataOperation.unbind(结点编号,文外链接.card_id)

    # @staticmethod
    # def group_review(answer: AnswerInfoInterface):
    #     """用来同步复习卡片"""
    #
    #     if Config.get().group_review.value == False:
    #         return
    #     if answer.card_id not in G.GroupReview_dict.card_group:
    #         return
    #     if Config.get().group_review_comfirm_dialog.value:
    #         go_on = QMessageBox.information(None, "group_review", Translate.群组复习提示, QMessageBox.Yes | QMessageBox.No)
    #         if go_on == QMessageBox.No:
    #             return
    #     searchs = G.GroupReview_dict.card_group[answer.card_id]
    #
    #     sched = compatible_import.mw.col.sched
    #     reportstring = ""
    #     for search in searchs:
    #         cids = G.GroupReview_dict.search_group[search]
    #         for cid in cids:
    #             card = mw.col.get_card(CardId(cid))
    #             button_num = sched.answerButtons(card)
    #             ease = answer.option_num if button_num >= answer.option_num else button_num
    #             if card.timer_started is None: card.timer_started = time.time() - 60
    #             CardOperation.answer_card(card, ease)
    #             reportstring += str(cid) + ":" + CardOperation.desc_extract(cid) + "<br>"
    #     mw.col.reset()
    #     reportstring += "以上卡片已经同步复习<br>cards above has beend sync reviewed"
    #     tooltip(reportstring, period=5000)

    # @staticmethod
    # def 上次复习时间(card_id):
    # CardOperation.GetCard(card_id).load()

    @staticmethod
    def delay_card(card, delay_num):
        print(f"delay={delay_num}")
        mw.col.sched.set_due_date([card.id], str(delay_num))
        # card.due=card.due+delay_num
        # mw.col.flush
        card.flush()
        # print("refresh")
        CardOperation.refresh()
        pass

    @staticmethod
    def answer_card(card, ease):
        sched = mw.col.sched
        count = 10
        for i in range(count):
            Utils.print(f"try answer_card time={i}")
            try:
                sched.answerCard(card, ease)
                break
            except:
                time.sleep(0.2)
                continue
        GrapherOperation.updateDue(f"{card.id}")
        GviewOperation.更新卡片到期时间(f"{card.id}")

    @staticmethod
    def create(model_id: "int" = None, deck_id: "int" = None, failed_callback: "Callable" = None):
        if ISLOCALDEBUG:
            return "1234567890"
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
    def refresh(card_id=None):
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

        browser: "Browser" = BrowserOperation.get_browser()
        if browser is not None and browser._previewer is not None:
            prev_refresh(browser._previewer)
        if mw.state == "review":
            mw.reviewer._refresh_needed = RefreshNeeded.NOTE_TEXT
            mw.reviewer.refresh_if_needed()  # 这个功能时好时坏,没法判断.

        for k, v in G.mw_card_window.items():
            if v is not None:
                prev_refresh(v)
        GrapherOperation.refresh()
        # GviewOperation.刷新()
        # from ..bilink.dialogs.linkdata_grapher import Grapher

        # print("card refreshed")

    @staticmethod
    def exists(id):
        return card_exists(id)

    @staticmethod
    def note_get(id):
        return note_get(id)

    @staticmethod
    def 获取卡片内容与标题(card_id):
        note: "Note" = CardOperation.note_get(card_id)
        卡片内容 = "\n".join(note.fields)
        卡片标题 = GlobalLinkDataOperation.read_from_db(card_id).self_data.desc
        return 卡片标题 + "\n" + 卡片内容

    @staticmethod
    def desc_extract(card_id, fromField=False):
        """读取逻辑,
        0 判断是否强制从卡片字段中提取
            0.1 是 则直接提取
            0.2 不是 再往下看.
        1 从数据库了解是否要auto update,
            1.1 不auto则读取数据库
            1.2 auto 则读取卡片本身
                1.2.1 从预设了解是否有预定的读取方案
                    1.2.1.1 若有预定的方案则根据预定方案读取
                    1.2.1.2 无预定方案, 则根据默认的方案读取.
       """
        cfg = Config.get()
        from . import models
        def get_desc_from_field(ins: "models.类型_模型_描述提取规则", note) -> str:
            if ins.字段.值 == -1:
                StrReadyToExtract = "".join(note.fields)
            else:
                StrReadyToExtract = note.fields[ins.字段.值]
            step1_desc = HTML.TextContentRead(StrReadyToExtract)
            Utils.print(step1_desc)
            step2_desc = step1_desc if ins.长度.值 == 0 else step1_desc[0:int(ins.长度.值)]
            if ins.正则 != "":
                search = re.search(ins.正则, step2_desc)
                if search is None:
                    tooltip("根据设置中预留的正则表达式, 没有找到描述")
                else:
                    step2_desc = search.group()
            return step2_desc

        from . import objs

        ins = CardOperation.InstructionOfExtractDesc(card_id)

        note: "Note" = CardOperation.note_get(card_id)
        if fromField:  # 若强制指定了要从字段中读取, 则抛弃以下讨论, 直接返回结果.
            # 确定字段
            return get_desc_from_field(ins, note)
        else:
            datainfo = GlobalLinkDataOperation.read_from_db(card_id)
            if datainfo.self_data.get_desc_from == objs.LinkDescFrom.DB:
                # print("--------=--=-=-=-=       desc  from DB       ")
                return datainfo.self_data._desc
            else:
                if ins.同步.值:
                    # 确定字段
                    return get_desc_from_field(ins, note)
                else:
                    datainfo.self_data.get_desc_from = objs.LinkDescFrom.DB
                    datainfo.save_to_DB()
                    return datainfo.self_data._desc

    @staticmethod
    def desc_save(card_id, desc):
        GlobalLinkDataOperation.update_desc_to_db(LinkDataPair(card_id, desc))

    @staticmethod
    def InstructionOfExtractDesc(card_id):
        from . import models
        cfg = Config.get()
        空规则 = models.类型_模型_描述提取规则()
        全部描述提取规则 = [models.类型_模型_描述提取规则(规则) for 规则 in cfg.descExtractTable.value]
        卡片信息 = mw.col.get_card(int(card_id))
        牌组编号 = 卡片信息.did
        模板编号 = 卡片信息.note().mid
        标签集:"set[str]" = set(卡片信息.note().tags)
        选中规则 = 空规则
        for 规则 in 全部描述提取规则:
            规则的标签集:"set[str]" = set(规则.标签.值)
            # 三个东西全部满足, 说明这条规则对上了, 就可以用,
            满足牌组 = 规则.牌组.值 == -1 or 牌组编号 == 规则.牌组.值 or 牌组编号 in [子[1] for 子 in mw.col.decks.children(规则.牌组.值)]
            满足模板 = (规则.模板.值 == -1 or 模板编号 == 规则.模板.值 )
            满足标签 = (len(规则.标签.值)==0 or 标签集 & 规则的标签集 != set() or len([规则标签 for 规则标签 in 规则的标签集 if len([标签 for 标签 in 标签集 if 标签.startswith(规则标签)])>0 ])>0 )
            if 满足牌组 and 满足模板 and 满足标签:
                选中规则 = 规则
                break
        return 选中规则
        # from . import objs
        # cfg = Config.get()
        # specialModelIdLi = [desc[0] for desc in cfg.descExtractTable.value]
        # modelId = CardOperation.note_get(card_id).mid
        # returnData = []
        # if modelId in specialModelIdLi:
        #     idx = specialModelIdLi.index(modelId)
        #     returnData = cfg.descExtractTable.value[idx]
        # elif -1 in specialModelIdLi:
        #     idx = specialModelIdLi.index(-1)
        #     returnData = cfg.descExtractTable.value[idx]
        # else:
        #     returnData = [-1, -1, cfg.length_of_desc.value, "", cfg.desc_sync.value]
        # return objs.descExtractTable(*returnData)

    @staticmethod
    def get_correct_id(card_id):
        from . import objs
        if isinstance(card_id, objs.LinkDataPair):  # 有可能把pair传进来的
            cid = card_id.int_card_id
        elif isinstance(card_id, Card):
            cid = card_id.id
        elif isinstance(card_id, str):
            cid = int(card_id)
        elif type(card_id) == int:
            cid = card_id
        else:
            raise TypeError("参数类型不支持:" + card_id.__str__())
        return cid

    @staticmethod
    def GetCard(card_id_):
        card_id = CardOperation.get_correct_id(card_id_)
        if pointVersion() > 46:
            return mw.col.get_card(card_id)
        else:
            return mw.col.getCard(card_id)

    @staticmethod
    def clipbox_insert_field(clipuuid, timestamp=None):
        """用于插入clipbox到指定的卡片字段,如果这个字段存在这个clipbox则不做操作"""
        if ISLOCALDEBUG:
            return
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
    def getLastNextRev(card_id):
        """获取上次复习与下次复习时间"""
        result = mw.col.db.execute(
                # 从 数据库表revlog 中获取 上次回顾时间, 下次间隔, 推算出下次回顾的时间, 之所以直接从数据库提取是因为anki的接口做的很不清楚, 无法判断一个卡片是否可复习
                # 比如他的 card.due 值是时间戳, 表示到期时间, 但 也有一些到期时间比如746,1817480这种显然就不是时间戳
                f"select id,ivl from revlog where id = (select  max(id) from revlog where cid = {card_id})"
        )
        if result:
            last, ivl = result[0]
            last_date = datetime.fromtimestamp(last / 1000)  # (Y,M,D,H,M,S,MS)
            if ivl >= 0:  # ivl 正表示天为单位,负表示秒为单位
                next_date = datetime.fromtimestamp(last / 1000 + ivl * 86400)  # (Y,M,D,H,M,S,MS)
            else:
                next_date = datetime.fromtimestamp(last / 1000 - ivl)  # 此时的 ivl保存为负值,因此要减去
        else:
            # 没有记录表示新卡片, 直接给他设个1970年就完事
            next_date = datetime.fromtimestamp(0)  # (Y,M,D,H,M,S,MS)
            last_date = datetime.fromtimestamp(0)  # (Y,M,D,H,M,S,MS)
        # today = datetime.today()  # (Y,M,D,H,M,S,MS)
        # Utils.print(last_date, next_date)
        return last_date, next_date


class Media:
    """"""

    @staticmethod
    def clipbox_png_save(clipuuid):
        if platform.system() in {"Darwin", "Linux"}:
            tooltip("当前系统暂时不支持该功能")
            return
        else:
            from ..clipper2.exports import fitz
        if ISLOCALDEBUG:
            mediafolder = r"D:\png"
        else:
            mediafolder = os.path.join(mw.pm.profileFolder(), "collection.media")
        DB = G.DB
        clipbox_ = DB.go(DB.table_clipbox).select(uuid=clipuuid).return_all().zip_up()[0]
        clipbox = G.objs.ClipboxRecord(**clipbox_)
        pdfinfo_ = DB.go(DB.table_pdfinfo).select(uuid=clipbox.pdfuuid).return_all().zip_up()[0]
        pdfinfo = G.objs.PDFinfoRecord(**pdfinfo_)
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
        if ISLOCALDEBUG:
            return
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
    def insert(pair_li: "list[G.objs.LinkDataPair]" = None, mode=1, need_show=True, FROM=None):
        if FROM == DataFROM.shortCut:
            pair_li = BrowserOperation.get_selected_card()
            if len(pair_li) == 0:
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
    def link(mode=4, pair_li: "Optional[list[G.objs.LinkDataPair]]" = None, FROM=None):
        if FROM == DataFROM.shortCut:
            pair_li = BrowserOperation.get_selected_card()
            if len(pair_li) == 0:
                tooltip(Translate.请选择卡片)
                return
            mode = Config.get().default_link_mode.value

        def on_quit_handle(timestamp):
            cfg = Config.get()
            if cfg.open_browser_after_link.value == 1:
                if cfg.add_link_tag.value == 1:
                    BrowserOperation.search(f"""tag:hjp-bilink::timestamp::{timestamp}""").activateWindow()
                else:
                    s = ""
                    for pair in pair_li:
                        s += f"cid:{pair.card_id} or "
                    BrowserOperation.search(s[0:-4]).activateWindow()
            G.mw_progresser.close()
            G.mw_universal_worker.allevent.unbind()
            LinkPoolOperation.both_refresh()

        from . import widgets
        if pair_li is not None:
            LinkPoolOperation.insert(pair_li, mode=LinkPoolOperation.M.before_clean, need_show=False)
        G.mw_progresser = widgets.UniversalProgresser()  # 实例化一个进度条
        G.mw_universal_worker = LinkPoolOperation.LinkWorker(mode=mode)  # 实例化一个子线程
        G.mw_universal_worker.allevent = G.objs.AllEventAdmin([  # 给子线程的不同情况提供回调函数
                [G.mw_universal_worker.on_quit, on_quit_handle],  # 完成时回调
                [G.mw_universal_worker.on_progress, G.mw_progresser.value_set],  # 进度回调
        ]).bind()
        G.mw_universal_worker.start()

    @staticmethod
    def unlink(mode=6, pair_li: "Optional[list[G.objs.LinkDataPair]]" = None, FROM=None):
        if FROM == DataFROM.shortCut:
            pair_li = BrowserOperation.get_selected_card()
            if len(pair_li) == 0:
                tooltip(Translate.请选择卡片)
                return
            mode = Config.get().default_unlink_mode.value
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
            flatten: "list[LinkDataJSONInfo]" = reduce(lambda x, y: x + y, linkdatali, [])
            total, count = len(flatten), 0
            DB = G.DB
            # 先加tag

            for pair in flatten:
                pair.add_tag(d.addTag)
                if cfg.add_link_tag.value:
                    pair.add_timestamp_tag(self.timestamp)
                count += 1
                self.on_progress.emit(Utils.percent_calc(total, count, 0, 25))

            # 根据不同的模式进行不同的操作
            if self.mode in {L.M.complete_map, L.M.unlink_by_node}:
                total, count = len(flatten), 0
                for linkinfoA in flatten:
                    total2, count2 = len(flatten), 0
                    for linkinfoB in flatten:
                        if linkinfoB.self_data.card_id != linkinfoA.self_data.card_id:
                            if self.mode == L.M.complete_map:
                                GlobalLinkDataOperation.bind(linkinfoA, linkinfoB, needsave=False)
                            elif self.mode == L.M.unlink_by_node:
                                GlobalLinkDataOperation.unbind(linkinfoA, linkinfoB, needsave=False)
                        count2 += 1
                        self.on_progress.emit(Utils.percent_calc(total, (count2 / total2 + count), 25, 50))
                    count += 1
            elif self.mode in (L.M.group_by_group, L.M.unlink_by_path):
                total, count = len(linkdatali), 0
                r = self.reducer(count, total, self, d)
                reduce(r.reduce_link, linkdatali)
            total, count = len(flatten), 0
            DB.go(DB.table_linkinfo)
            for linkinfo in flatten:
                # temp = linkinfo.to_DB_record
                linkinfo.save_to_DB()
                # card_id, data = temp["card_id"], temp["data"]
                # DB.replace(card_id=card_id, data=data).commit(need_commit=False)
                count += 1
                self.on_progress.emit(Utils.percent_calc(total, count, 75, 25))

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
                self.worker.on_progress.emit(Utils.percent_calc(self.total, self.count, 25, 50))
                L = LinkPoolOperation
                for linkinfoA in groupA:
                    for linkinfoB in groupB:
                        if self.worker.mode == L.M.group_by_group:
                            GlobalLinkDataOperation.bind(linkinfoA, linkinfoB, needsave=False)
                        elif self.worker.mode == L.M.unlink_by_path:
                            GlobalLinkDataOperation.unbind(linkinfoA, linkinfoB, needsave=False)
                self.count += 1
                return groupB


class 卡片模板操作:
    @staticmethod
    def 获取模板名(模板编号, 缺省值: "str" = None):
        if 模板编号 > 0:
            return mw.col.models.get(模板编号)["name"]
        else:
            return 缺省值


class 牌组操作:
    @staticmethod
    def 获取牌组名(模板编号, 缺省值: "str" = None):
        if 模板编号 > 0:
            return mw.col.decks.name(模板编号)
        else:
            return 缺省值


class 卡片字段操作:
    @staticmethod
    def 获取字段名(模板编号, 字段编号, 缺省值: "str" = None):
        字段名列表 = []
        if 模板编号 > 0:
            模板 = mw.col.models.get(模板编号)
            字段名列表 = mw.col.models.field_names(模板)
            if len(字段名列表) > 字段编号 >= 0:
                return 字段名列表[字段编号]
            else:
                return 缺省值
        else:
            return 缺省值


class ModelOperation:
    @staticmethod
    def get_all():
        data = []
        if ISLOCALDEBUG:
            data = [{"id": 123456, "name": "hello"}]
            return data
        model = mw.col.models.all_names_and_ids()
        for i in model:
            data.append({"id": i.id, "name": i.name})
        return data


class DeckOperation:
    @staticmethod
    def get_all():
        data = []
        if ISLOCALDEBUG:
            data = [{"id": 123456, "name": "hello"}]
            return data

        deck = mw.col.decks.all_names_and_ids()
        for i in deck:
            data.append({"id": i.id, "name": i.name})
        return data


class MonkeyPatch:

    @staticmethod
    def AddCards_closeEvent(funcs):
        from aqt.addcards import AddCards
        def 包装器(self: "AddCards", evt: "QCloseEvent"):
            G.常量_当前等待新增卡片的视图索引 = None
            funcs(self, evt)
            pass

        return 包装器
        pass

    @staticmethod
    def mw_closeevent(funcs):
        def wrapper(*args, **kwargs):
            self = args[0]
            event = args[1]
            showInfo("hi!")
            funcs(self, event)

        return wrapper

    @staticmethod
    def Reviewer_nextCard(funcs):
        def wrapper(self: "Reviewer"):
            funcs(self)
            cfg = Config.get()
            if cfg.too_fast_warn.value:
                G.nextCard_interval.append(int(datetime.now().timestamp() * 1000))
                threshold = cfg.too_fast_warn_everycard.value
                tooltip(G.nextCard_interval.__str__())
                if len(G.nextCard_interval) > 1:  # 大于1才有阈值讨论的余地
                    last = G.nextCard_interval[-2]
                    now = G.nextCard_interval[-1]
                    # tooltip(str(now-last))
                    if now - last > cfg.too_fast_warn_interval.value:
                        G.nextCard_interval.clear()
                        return
                    else:
                        if len(G.nextCard_interval) >= threshold:
                            showInfo(Translate.过快提示)
                            G.nextCard_interval.clear()

        return wrapper

    @staticmethod
    def Reviewer_showEaseButtons(funcs):
        def freezeAnswerCard(self: Reviewer):
            _answerCard = self._answerCard
            self._answerCard = lambda x: tooltip(Translate.已冻结)
            return _answerCard

        def recoverAnswerCard(self: Reviewer, _answerCard):
            self._answerCard = _answerCard

        def _showEaseButtons(self: Reviewer):
            funcs(self)
            cfg = Config.get()
            if cfg.freeze_review.value:
                interval = cfg.freeze_review_interval.value
                self.bottom.web.eval("""
                buttons = document.querySelectorAll("button[data-ease]")
                buttons.forEach(button=>{button.setAttribute("disabled",true)})
                setTimeout(()=>{buttons.forEach(button=>button.removeAttribute("disabled"))},
                """ + str(interval) + """)""")

                self.mw.blockSignals(True)
                tooltip(Translate.已冻结)
                _answerCard = freezeAnswerCard(self)
                QTimer.singleShot(interval, lambda: recoverAnswerCard(self, _answerCard))
                QTimer.singleShot(interval, lambda: tooltip(Translate.已解冻))

        return _showEaseButtons

    @staticmethod
    def BrowserSetupMenus(funcs, after, *args, **kwargs):
        def setupMenus(self: "Browser"):
            funcs(self)
            after(self, *args, **kwargs)

        return setupMenus

    @staticmethod
    def onAppMsgWrapper(self: "AnkiQt"):
        # self.app.appMsg.connect(self.onAppMsg)
        """"""

        def handle_AnkiLink(buf):
            # buf加了绝对路径,所以要去掉
            # 有时候需要判断一下
            tooltip(buf)

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
                    Dialogs.open_grapher(gviewdata=data, mode=GraphMode.view_mode)
                else:
                    tooltip("view not found")

            from .objs import CmdArgs
            ankilink = G.src.ankilink
            Utils.LOG.file_write(buf, True)
            cmd_dict = {
                    # 下面的是1版命令格式
                    f"{ankilink.Cmd.opencard}"                           : handle_opencard,
                    f"{ankilink.Cmd.openbrowser_search}"                 : handle_openbrowser,
                    f"{ankilink.Cmd.opengview}"                          : handle_opengview,
                    # 下面的是2版命令格式
                    f"{ankilink.Cmd.open}?{ankilink.Key.card}"           : handle_opencard,
                    f"{ankilink.Cmd.open}?{ankilink.Key.gview}"          : handle_opengview,
                    f"{ankilink.Cmd.open}?{ankilink.Key.browser_search}" : handle_openbrowser,
                    # ANKI关闭时的模式
                    f"{ankilink.Cmd.open}/?{ankilink.Key.card}"          : handle_opencard,
                    f"{ankilink.Cmd.open}/?{ankilink.Key.gview}"         : handle_opengview,
                    f"{ankilink.Cmd.open}/?{ankilink.Key.browser_search}": handle_openbrowser,
            }

            if buf.startswith(f"{G.src.ankilink.protocol}://"):  # 此时说明刚打开就进来了,没有经过包装,格式取buf[11:-1]
                cmd = CmdArgs(buf[11:].split("="))
            else:
                cmd = CmdArgs(buf.split(f"{G.src.ankilink.protocol}:\\")[-1].replace("\\", "").split("="))

            if cmd.type in cmd_dict:
                # showInfo(cmd.args)
                cmd_dict[cmd.type](cmd.args)

            else:
                showInfo("打开状态下, 未知指令/unknown command:  <br>" + cmd.type)
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

    if not ISLOCALDEBUG:
        class BrowserPreviewer(MultiCardPreviewer):
            _last_card_id = 0
            _parent: Optional["Browser"]

            def __init__(
                    self, parent: "Browser", mw: "AnkiQt", on_close: Callable[[], None]
            ) -> None:
                super().__init__(parent=parent, mw=mw, on_close=on_close)
                self.bottom_layout = QGridLayout()
                self.bottom_layout_all = QGridLayout()
                self.reviewWidget = widgets.ReviewButtonForCardPreviewer(self, self.bottom_layout_all)

            def card(self) -> Optional[Card]:
                if self._parent.singleCard:
                    return self._parent.card
                else:
                    return None

            def render_card(self) -> None:
                super().render_card()

            def _create_gui(self):
                super()._create_gui()
                self.vbox.removeWidget(self.bbox)
                self.bottom_layout_all.addWidget(self.bbox, 0, 1, 1, 1)
                self.vbox.addLayout(self.bottom_layout_all)

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

            def _on_next_card(self) -> None:
                self._parent.onNextCard()

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
                QTimer.singleShot(100, lambda: self.reviewWidget.update_info())

            def _on_next(self) -> None:
                if self._state == "question":
                    self._state = "answer"
                    self.render_card()
                else:
                    self._on_next_card()
                QTimer.singleShot(100, lambda: self.reviewWidget.update_info())

    else:
        class BrowserPreviewer:
            def __init__(self):
                raise Exception("not support in this env")


class Dialogs:
    """打开对话框的函数,而不是对话框本身"""

    @staticmethod
    def open_GviewAdmin():
        from ..bilink.dialogs.linkdata_grapher import GViewAdmin
        if isinstance(G.GViewAdmin_window, GViewAdmin):
            G.GViewAdmin_window.activateWindow()
        else:
            G.GViewAdmin_window = GViewAdmin()
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
    def open_inrtoDoc():
        Utils.版本.打开网址()
        # from ..bilink import dialogs
        # p = dialogs.version.VersionDialog()
        # p.show()

    @staticmethod
    def open_tag_chooser(pair_li: "list[G.objs.LinkDataPair]"):
        from . import widgets
        p = widgets.tag_chooser_for_cards(pair_li)
        p.exec()
        pass

    @staticmethod
    def open_deck_chooser(pair_li: "list[G.objs.LinkDataPair]", view=None):
        from . import widgets

        p = widgets.deck_chooser_for_changecard(pair_li, view)
        p.exec()
        tooltip("完成")

        pass

    @staticmethod
    def open_view(gviewdata: "GViewData" = None, need_activate=True):
        Dialogs.open_grapher(gviewdata=gviewdata, mode=GraphMode.view_mode)

    @staticmethod
    def open_grapher(pair_li: "list[G.objs.LinkDataPair|str]" = None, need_activate=True, gviewdata: "GViewData" = None,
                     selected_as_center=True, mode=GraphMode.normal, ):
        from ..bilink.dialogs.linkdata_grapher import Grapher
        if mode == GraphMode.normal:
            from .graphical_bilinker import VisualBilinker
            if isinstance(G.mw_grapher, VisualBilinker):
                G.mw_grapher.load_node(pair_li, selected_as_center=selected_as_center)
                if need_activate:
                    G.mw_grapher.activateWindow()
            else:
                G.mw_grapher = VisualBilinker(pair_li)
                G.mw_grapher.show()
        elif mode == GraphMode.view_mode:
            if (gviewdata.uuid not in G.mw_gview) or (not isinstance(G.mw_gview[gviewdata.uuid], Grapher)):
                G.mw_gview[gviewdata.uuid] = Grapher(mode=mode, gviewdata=gviewdata)
                G.mw_gview[gviewdata.uuid].load_node(pair_li)
                G.mw_gview[gviewdata.uuid].show()
            else:
                G.mw_gview[gviewdata.uuid].load_node(pair_li)
                # tooltip(f"here G.mw_gview[{gviewdata.uuid}]")
                if need_activate:
                    G.mw_gview[gviewdata.uuid].show()
                    G.mw_gview[gviewdata.uuid].activateWindow()
        elif mode == GraphMode.debug_mode:
            Grapher(pair_li=pair_li, mode=mode, gviewdata=gviewdata).show()

    @staticmethod
    def open_configuration():
        """ 这里的内容要整理到Config的父类中"""
        dialog = Config.makeConfigDialog(None, Config.get(),
                                         # 关闭时回调=None)
                                         lambda 数据: Config.save(数据))  # save的参数是经过修正的cfg

        dialog.exec()

    @staticmethod
    def open_clipper(pairs_li=None, clipboxlist=None, **kwargs):
        if platform.system() in {"Darwin", "Linux"}:
            tooltip("当前系统暂时不支持PDFprev")
            return
        elif Utils.isQt6():
            tooltip("暂时不支持QT6")
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
        elif isinstance(FROM, SingleCardPreviewer):
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


class AnchorOperation:
    @staticmethod
    def if_empty_then_remove(html_str: "str"):
        bs = BeautifulSoup(html_str, "html.parser")
        roots = bs.select(f"#{G.addonName}")
        tags = bs.select(f"#{G.addonName} .container_body_L1")
        if len(roots) > 0:
            root: "BeautifulSoup" = roots[0]
        else:
            return bs.__str__()
        if len(tags) > 0 and len(list(tags[0].childGenerator())) == 0:
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


class HTML:
    @staticmethod
    def file_protocol_support(html_string):
        root = BeautifulSoup(html_string, "html.parser")
        href_is_file_li: "List[element.Tag]" = root.select('[href^="file://"]')
        style = root.new_tag("style", attrs={"class": G.src.pdfurl_style_class_name})
        style.string = f".{G.src.pdfurl_class_name}{{{Config.get().PDFLink_style.value}}}"
        root.insert(1, style)
        if len(href_is_file_li) > 0:
            for href in href_is_file_li:
                filestr = href["href"]
                href["onclick"] = f"""javascript:pycmd("{filestr}")"""
                href["href"] = ""
                href["class"] = G.src.pdfurl_class_name
        return root.__str__()

    @staticmethod
    def TextContentRead(html):
        return HTML_txtContent_read(html)

    @staticmethod
    def injectToWeb(htmltext, card, kind):
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

    @staticmethod
    def cardHTMLShadowDom(innerHTML: "str", HostId="", insertSelector="#qa", insertPlace="afterBegin"):
        if HostId == "":
            HostId = G.src.addon_name + "_host"
        innerHTML2 = innerHTML
        script = BeautifulSoup(f"""<script> 
        (()=>{{
         const Host = document.createElement("div");
         const root = Host.attachShadow({{mode:"open"}});
         const qa=document.body.querySelector("{insertSelector}")
         Host.id = "{HostId}";
         Host.style.zIndex = "999999";
         qa.insertAdjacentElement("{insertPlace}",Host)
         root.innerHTML=`{innerHTML2}`
         }})()
         </script>""", "html.parser")
        return script

    @staticmethod
    def LeftTopContainer_make(root: "BeautifulSoup"):
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
            cfg = Config.get()
            if cfg.anchor_style_text.value != "":
                style_str = cfg.anchor_style_text.value
            elif cfg.anchor_style_file.value != "" and os.path.exists(cfg.anchor_style_file.value):
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

    @staticmethod
    def clipbox_exists(html, card_id=None):
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

        return (reduce(lambda x, y: x or y, true_or_false_li, False))

    @staticmethod
    def InTextButtonDeal(html_string):
        from ..bilink.in_text_admin.backlink_reader import BackLinkReader
        buttonli = BackLinkReader(html_str=html_string).backlink_get()
        if len(buttonli) > 0:
            finalstring = html_string[0:buttonli[0]["span"][0]]
            for i in range(len(buttonli) - 1):
                prevEnd, nextBegin = buttonli[i]["span"][1], buttonli[i + 1]["span"][0]
                finalstring += HTML.InTextButtonMake(buttonli[i]) + html_string[prevEnd:nextBegin]
            finalstring += HTML.InTextButtonMake(buttonli[-1]) + html_string[buttonli[-1]["span"][1]:]
        else:
            finalstring = html_string
        return finalstring

    @staticmethod
    def InTextButtonMake(data):

        card_id = data["card_id"]
        desc = data["desc"]
        h = BeautifulSoup("", "html.parser")
        b = h.new_tag("button", attrs={"card_id": card_id, "class": "hjp-bilink anchor intext button",
                                       "onclick": f"""javascript:pycmd('hjp-bilink-cid:{card_id}');"""})
        b.string = desc
        return b.__str__()


def button_icon_clicked_switch(button: QToolButton, old: list, new: list, callback: "callable" = None):
    if button.text() == old[0]:
        button.setText(new[0])
        button.setIcon(QIcon(new[1]))
    else:
        button.setText(old[0])
        button.setIcon(QIcon(old[1]))
    if callback:
        callback(button.text())


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
    clipbox_from_DB_ = DB.go(DB.table_clipbox).select(DB.LIKE("card_id", card_id)).return_all().zip_up()
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
                                           "info"   : PDFinfo}  # 只提取页码, 大小重新再设定.偏移量也重新设定.
        PDF_info_dict[PDFinfo.uuid]["pagenum"].add(record.pagenum)

    return PDF_info_dict


def HTML_LeftTopContainer_detail_el_make(root: "BeautifulSoup", summaryname, attr: "dict" = None):
    """这是一个公共的步骤,设计一个details, root 传进来无所谓的, 不会基于他做操作,只是引用了他的基本功能
    details.hjp_bilink .details
        summary
        div
    """
    if attr is None:
        attr = {}
    attrs = attr.copy()
    if "class" in attrs:
        attrs["class"] += " hjp_bilink details"
    else:
        attrs["class"] = "hjp_bilink details"
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
        cfg = Config.get()
        if cfg.anchor_style_text.value != "":
            style_str = cfg.anchor_style_text.value
        elif cfg.anchor_style_file.value != "" and os.path.exists(cfg.anchor_style_file.value):
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
    shortCut = 0


class AnkiLinksCopy2:
    """新版的链接
    格式f: {ankilink}://command?key=value
    警告: 这个版本无法正常运行
    """
    protocol = f"{G.src.ankilink.protocol}"

    class Open:
        command = G.src.ankilink.cmd.open

        class Card:
            """"""
            key = G.src.ankilink.Key.card

            @staticmethod
            def from_htmllink(pairs_li: 'list[G.objs.LinkDataPair]'):
                """"""
                AnkiLinksCopy2.Open.Card._gen_link(pairs_li, AnkiLinksCopy2.LinkType.htmllink)

            @staticmethod
            def from_htmlbutton(pairs_li: 'list[G.objs.LinkDataPair]'):
                AnkiLinksCopy2.Open.Card._gen_link(pairs_li, AnkiLinksCopy2.LinkType.htmlbutton)

            @staticmethod
            def from_markdown(pairs_li: 'list[G.objs.LinkDataPair]'):
                AnkiLinksCopy2.Open.Card._gen_link(pairs_li, AnkiLinksCopy2.LinkType.markdown)

            @staticmethod
            def from_orgmode(pairs_li: 'list[G.objs.LinkDataPair]'):
                AnkiLinksCopy2.Open.Card._gen_link(pairs_li, AnkiLinksCopy2.LinkType.orgmode)

            @staticmethod
            def _gen_link(pairs_li: 'list[G.objs.LinkDataPair]', mode):
                clipboard = QApplication.clipboard()
                mmdata = QMimeData()
                A = AnkiLinksCopy2
                B = AnkiLinksCopy2.Open
                C = AnkiLinksCopy2.Open.Card
                header = f"{A.protocol}://{B.command}?{C.key}="
                puretext = ""
                total = ""
                if mode == A.LinkType.htmllink:
                    for pair in pairs_li:
                        total += f"""<a href="{header}{pair.card_id}">{pair.desc}<a><br>""" + "\n"
                        puretext += f"""{header}{pair.card_id}\n"""
                    mmdata.setHtml(total)
                    mmdata.setText(puretext)
                    clipboard.setMimeData(mmdata)
                    tooltip(puretext)
                    return
                elif mode == A.LinkType.htmlbutton:
                    def buttonmaker(p: LinkDataPair):
                        return f"""<div >|<button class="hjp_bilink ankilink button" onclick="javascript:pycmd('{header}{p.card_id}');">{p.desc}</button>|</div>"""

                    for pair in pairs_li:
                        total += buttonmaker(pair)
                    clipboard.setText(total)
                elif mode == A.LinkType.markdown:
                    for pair in pairs_li:
                        total += f"""[{pair.desc}]({header}{pair.card_id})\n"""
                    clipboard.setText(total)
                elif mode == A.LinkType.orgmode:
                    for pair in pairs_li:
                        total += f"""[[{header}{pair.card_id}][{pair.desc}]]\n"""
                    clipboard.setText(total)
                tooltip(total)

        class BrowserSearch:
            """"""
            key = G.src.ankilink.Key.browser_search

            @staticmethod
            def from_htmllink(browser: "Browser"):
                """"""
                AnkiLinksCopy2.Open.BrowserSearch._gen_link(browser, AnkiLinksCopy2.LinkType.htmllink)

            # @staticmethod
            # def from_htmlbutton(browser: "Browser"):
            #     """"""
            #     AnkiLinksCopy2.Open.BrowserSearch.gen_link(browser, AnkiLinksCopy2.LinkType.htmlbutton)

            @staticmethod
            def from_md(browser: "Browser"):
                """"""
                AnkiLinksCopy2.Open.BrowserSearch._gen_link(browser, AnkiLinksCopy2.LinkType.markdown)

            @staticmethod
            def from_orgmode(browser: "Browser"):
                """"""
                AnkiLinksCopy2.Open.BrowserSearch._gen_link(browser, AnkiLinksCopy2.LinkType.orgmode)

            @staticmethod
            def _gen_link(browser: "Browser", mode):
                """"""
                mmdata = QMimeData()
                clipboard = QApplication.clipboard()
                A = AnkiLinksCopy2
                B = AnkiLinksCopy2.Open
                C = AnkiLinksCopy2.Open.BrowserSearch
                searchstring = browser.form.searchEdit.currentText()
                tooltip(searchstring)
                header = f"{A.protocol}://{B.command}?{C.key}="
                href = header + quote(searchstring)

                func_dict = {
                        A.LinkType.htmllink: lambda: f"""<a href="{href}">{Translate.Anki搜索}:{searchstring}</a>""",

                        A.LinkType.orgmode : lambda: f"[[{href}][{Translate.Anki搜索}:{searchstring}]]",
                        A.LinkType.markdown: lambda: f"[{Translate.Anki搜索}:{searchstring}]({href})",
                }
                if mode == A.LinkType.htmllink:
                    mmdata.setText(href)
                    mmdata.setHtml(func_dict[mode]())
                    clipboard.setMimeData(mmdata)
                else:
                    clipboard.setText(func_dict[mode]())
                tooltip(href)

        class Gview:
            """"""
            key = G.src.ankilink.Key.gview

            @staticmethod
            def from_htmllink(data: "GViewData"):
                """"""
                AnkiLinksCopy2.Open.Gview._gen_link(data, AnkiLinksCopy2.LinkType.htmllink)

            @staticmethod
            def from_htmlbutton(data: "GViewData"):
                """"""
                AnkiLinksCopy2.Open.Gview._gen_link(data, AnkiLinksCopy2.LinkType.htmlbutton)

            @staticmethod
            def from_md(data: "GViewData"):
                """"""
                AnkiLinksCopy2.Open.Gview._gen_link(data, AnkiLinksCopy2.LinkType.markdown)

            @staticmethod
            def from_orgmode(data: "GViewData"):
                """"""
                AnkiLinksCopy2.Open.Gview._gen_link(data, AnkiLinksCopy2.LinkType.orgmode)

            @staticmethod
            def _gen_link(data: "GViewData", mode):
                mmdata = QMimeData()
                clipboard = QApplication.clipboard()
                A = AnkiLinksCopy2
                B = AnkiLinksCopy2.Open
                C = AnkiLinksCopy2.Open.Gview
                header = f"{A.protocol}://{B.command}?{C.key}="
                href = header + quote(data.uuid)

                func_dict = {
                        A.LinkType.htmllink  : lambda: f"""<a href="{href}">{Translate.Anki搜索}:{data.name}</a>""",
                        A.LinkType.orgmode   : lambda: f"[[{href}][{Translate.Anki搜索}:{data.name}]]",
                        A.LinkType.markdown  : lambda: f"[{Translate.Anki搜索}:{data.name}]({href})",
                        A.LinkType.htmlbutton: lambda: f"""<div >|<button class="hjp_bilink ankilink button" onclick="javascript:pycmd('{href}');">{Translate.Anki视图}:{data.name}</button>|</div>"""
                }
                if mode == A.LinkType.htmllink:
                    mmdata.setText(href)
                    mmdata.setHtml(func_dict[mode]())
                    clipboard.setMimeData(mmdata)
                else:
                    clipboard.setText(func_dict[mode]())
                tooltip(href)

    class LinkType:
        inAnki = 0
        htmlbutton = 1
        htmllink = 2
        markdown = 3
        orgmode = 4


class AnkiLinks:
    """这个版本已经废弃,仅用来兼容
    AnkiLinksCopy2存在无法运行的问题
    """

    class Type:
        html = 0
        markdown = 1
        orgmode = 2
        inAnki = 3

    @staticmethod
    def copy_card_as(linktype: int = None, pairs_li: 'list[G.objs.LinkDataPair]' = None, FROM=None):
        tooltip(pairs_li.__str__())
        clipboard = QApplication.clipboard()
        header = f"{G.src.ankilink.protocol}://opencard_id="
        if FROM == DataFROM.shortCut:
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
            total = ""

            def buttonmaker(p: LinkDataPair):
                return f"""<div >|<button class="hjp_bilink ankilink button" onclick="javascript:pycmd('{header}{p.card_id}');">{p.desc}</button>|</div>"""

            for pair in pairs_li:
                total += buttonmaker(pair)
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
        func_dict = {typ.html    : as_html,
                     typ.orgmode : as_orgmode,
                     typ.markdown: as_markdown,
                     typ.inAnki  : as_inAnki}
        func_dict[linktype](pairs_li)
        if len(pairs_li) > 0:
            tooltip(clipboard.text())
        else:
            tooltip(Translate.请选择卡片)

    @staticmethod
    def copy_search_as(linktype: int, browser: "Browser"):
        searchstring = browser.form.searchEdit.currentText()
        tooltip(searchstring)
        clipboard = QApplication.clipboard()
        header = f"{G.src.ankilink.protocol}://openbrowser_search="
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
        func_dict = {typ.html    : as_html,
                     typ.orgmode : as_orgmode,
                     typ.markdown: as_markdown}
        func_dict[linktype]()
        pass

    @staticmethod
    def copy_gview_as(linktype: int, data: "GViewData"):
        tooltip(data.__str__())
        clipboard = QApplication.clipboard()
        header = f"{G.src.ankilink.protocol}://opengview_id="
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
        func_dict = {typ.html    : as_html,
                     typ.orgmode : as_orgmode,
                     typ.markdown: as_markdown,
                     typ.inAnki  : as_inAnki, }
        func_dict[linktype]()

    @staticmethod
    def get_card_from_clipboard():
        from ..bilink.linkdata_admin import read_card_link_info
        clipboard = QApplication.clipboard()
        cliptext = clipboard.text()
        reg_str = fr"(?:{G.src.ankilink.protocol}://opencard_id=|\[\[link:)(\d+)"
        pair_li = [read_card_link_info(card_id).self_data for card_id in re.findall(reg_str, cliptext)]
        return pair_li


class PDFLink:
    @staticmethod
    def FindIndexOfPathInPreset(url: "str"):
        booklist = Config.get().PDFLink_presets.value  # [["PDFpath", "name", "style", "showPage"]...]
        a = [url == bookunit[0] for bookunit in booklist]
        if True in a:
            return a.index(True)
        else:
            return -1

    @staticmethod
    def GetPathInfoFromPreset(url):
        booklist = Config.get().PDFLink_presets.value  # [["PDFpath", "name", "style", "showPage"]...]
        index: "int" = PDFLink.FindIndexOfPathInPreset(url)
        if index != -1:
            return booklist[index]
        else:
            return None


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
        note = CardOperation.GetCard(cid).note()
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
            # Utils.print(f"fromField={fromField},desc_sync={cfg.desc_sync.value},desc={desc}")
        else:
            desc = linkdata_admin.read_card_link_info(str(cid)).self_data.desc
            # Utils.print("desc fromDB =" + desc)
            if desc == "":
                desc = get_desc_from_field(note)
    return desc


def card_exists(card_id):
    from . import objs
    if isinstance(card_id, str) and not card_id.isdigit():
        return False
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

    cfg = ConfigModel()
    root = BeautifulSoup(html, "html.parser")
    list(map(lambda x: x.extract(), root.select(".hjp_bilink.ankilink.button")))
    text = root.getText()
    if cfg.delete_intext_link_when_extract_desc.value:
        newtext = text
        replace_str = ""
        intextlinks = BackLinkReader(html_str=text).backlink_get()
        for link in intextlinks:
            span = link["span"]
            replace_str += re.sub("(\])|(\[)", lambda x: "\]" if x.group(0) == "]" else "\[",
                                  text[span[0]:span[1]]) + "|"
        replace_str = replace_str[0:-1]
        text = re.sub(replace_str.replace("\\", "\\\\"), "", newtext)
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


class Geometry:
    @staticmethod
    def MakeArrowForLine(line: "QLineF"):
        v = line.unitVector()
        v.setLength(30)
        v.translate(QPointF(line.dx() * 2 / 5, line.dy() * 2 / 5))

        n = v.normalVector()
        n.setLength(n.length() * 0.3)
        n2 = n.normalVector().normalVector()

        p1 = v.p2()
        p2 = n.p2()
        p3 = n2.p2()
        return QPolygonF([p1, p2, p3])

    @staticmethod
    def IntersectPointByLineAndRect(line: "QLineF", polygon: "QRectF"):
        intersectPoint = QPointF()
        edges = [
                QLineF(polygon.topLeft(), polygon.topRight()),
                QLineF(polygon.topLeft(), polygon.bottomLeft()),
                QLineF(polygon.bottomRight(), polygon.bottomLeft()),
                QLineF(polygon.bottomRight(), polygon.topRight()),
        ]
        # edges = Map.do(range(4),lambda i:QLineF(polygon.at(i),polygon.at((i+1)%4)))
        # print(f"edges={edges},\nLine={line}")
        for edge in edges:
            intersectsType, pointAt = line.intersects(edge)

            if intersectsType == QLineF.IntersectionType.BoundedIntersection:
                return intersectPoint
        return None


CardId = Compatible.CardId()
log = logger(__name__)
