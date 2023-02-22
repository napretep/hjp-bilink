# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = '$NAME.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2021/7/30 9:09'
"""
import abc
import collections
import json
import re,sys
import sqlite3
from datetime import datetime
from abc import ABC
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Union
from urllib.parse import unquote
from .compatible_import import *
logtext = r"C:\Users\Administrator\AppData\Roaming\Anki2\addons21\hjp-bilink\log.txt"
class Utils(object):
    @staticmethod
    def print(*args, need_timestamp=True, need_logFile=True, **kwargs):

            caller = sys._getframe(1).f_code.co_name
            caller2 = sys._getframe(2).f_code.co_name
            if need_timestamp:
                ts = (datetime.now().strftime("%Y%m%d%H%M%S"))
            else:
                ts = ""
            if need_logFile:
                f = open(logtext, "a", encoding="utf-8")
                print(f"{ts}|{caller2}>>{caller}:\n", *args, **kwargs, file=f)
            else:
                print(f"{ts}|{caller2}>>{caller}:\n", *args, **kwargs)


@dataclass
class descExtractTable:
    templateId:"int"
    fieldId:"int"
    length:"int"
    regex:"str"
    sync:"bool"

class NONE:
    @staticmethod
    def activateWindow()->False:
        return False

@dataclass
class CmdArgs:
    type:"str"
    args:"str"
    def __init__(self,cmdargsli:"list[str,str]"):
        """需要在这里分辨不同版本的参数
        0版:command=args
        1版:command?key=args
        """
        self.args=unquote(cmdargsli[1])
        self.type=cmdargsli[0].lower()


@dataclass
class Date:
    year:"int"
    month:"int"
    day:"int"
    hour:"int"
    minute:"int"
    second:"int"
    millisecond:"int"

    def __eq__(self, other:"Date"):
        return other.year==self.year and other.month==self.month and other.day==self.day\
            and other.hour == self.hour and other.minute == self.minute and other.second == self.second \
            and other.millisecond == self.millisecond

    def __le__(self, other:"Date"):
        if other.year>self.year:
            return True
        elif other.year==self.year and other.month>self.month:
            return True
        elif other.year==self.year and other.month==self.month and other.day>self.day:
            return True
        elif other.year==self.year and other.month==self.month and other.day==self.day \
            and other.hour>self.hour :
            return True
        elif other.year==self.year and other.month==self.month and other.day==self.day \
            and other.hour==self.hour and other.minute>self.minute :
            return True
        elif other.year==self.year and other.month==self.month and other.day==self.day \
            and other.hour==self.hour and other.minute==self.minute and other.second>self.second :
            return True
        elif other.year==self.year and other.month==self.month and other.day==self.day \
            and other.hour==self.hour and other.minute==self.minute and other.second==self.second\
            and other.millisecond>self.millisecond:
            return True
        else:
            return False

class Struct:
    @dataclass
    class TreeNode:
        """这是一个树的标准结点,有自己和孩子两部分数据"""
        item: "QStandardItem"
        children: "dict[str,Struct.TreeNode]"


class AddonVersion:
    def __init__(self, v_tuple: "iter"):
        self.v = v_tuple

    def __lt__(self, other):
        if self.v[0] != other.v[0]:
            return self.v[0] < other.v[0]
        elif self.v[1] != other.v[1]:
            return self.v[1] < other.v[1]
        else:
            return self.v[2] < other.v[2]


@dataclass
class LinkPoolModel:
    """链接池读取出来后要用这个包装一下, 可以简单使用"""
    IdDescPairs: "list[list[LinkDataPair]]"
    addTag: "str"

    def __init__(self, fromjson: "dict[str,Union[list[list[dict]],str]]" = None,
                 frompairli: "list[LinkDataPair]" = None):
        if fromjson:
            self.IdDescPairs = [[LinkDataPair(**pair) for pair in group] for group in fromjson["IdDescPairs"]]
            self.addTag = fromjson["addTag"]
        elif frompairli:
            self.IdDescPairs = [[pair] for pair in frompairli]
            self.addTag = ""

    def todict(self):
        d = {}
        d["IdDescPairs"] = [[pair.todict() for pair in group] for group in self.IdDescPairs]
        d["addTag"] = self.addTag
        return d

    def tolinkdata(self):
        from ..bilink import linkdata_admin
        return [ [ linkdata_admin.read_card_link_info(pair.card_id) for pair in group]for group in self.IdDescPairs]

    def flatten(self):
        """降维, 把group去掉, 通常用于complete_map的需要"""
        d = []
        for group in self.IdDescPairs:
            for pair in group:
                d.append(pair)
        return d

@dataclass
class LinkDescFrom:
    DB:int=0
    Field:int=1

@dataclass
class LinkDataPair:
    """LinkDataJSONInfo 的子部件, 也可以独立使用
    访问desc时,等价于访问 funcs.CardOperation.desc_extract(self.card_id)
    _desc保存着来自DB的数据内容, 但需要复杂的规则,来确定是否读取DB的内容
    """
    card_id: "str"
    _desc: "str" = "" #由于引入了新的设定, desc的获取不一定是来自数据库,而是实时与卡片内容保持一致, 所以需要一个中间层来处理问题.

    dir: "str" = "→"
    get_desc_from:int=LinkDescFrom.DB

    def __init__(self,card_id="",desc="",dir="→",get_desc_from=LinkDescFrom.DB):
        self.card_id=card_id
        self._desc=desc
        self.dir=dir
        self.get_desc_from=get_desc_from

    @property
    def desc(self):
        from . import funcs
        # if self.get_desc_from == LinkDescFrom.DB:
        # if  sys._getframe(1).f_code.co_name != "desc_extract":
        #     raise PermissionError("只能通过CardOperation.desc_extract访问本属性")

        return  funcs.CardOperation.desc_extract(self.card_id)
        # return funcs.CardOperation.desc_extract(self.card_id)


    @desc.setter
    def desc(self,value):
        self._desc=value
        # self.get_desc_from=LinkDescFrom.DB

    @property
    def int_card_id(self):
        return int(self.card_id)

    def to_self_dict(self):
        return {"card_id":self.card_id, "desc":self._desc,"dir":self.dir,"get_desc_from":self.get_desc_from}

    def todict(self)->'dict[str,str]':
        return {"card_id":self.card_id, "desc":self.desc,"dir":self.dir}

    # def update_desc(self):
    #     """是从卡片中更新描述"""
    #     from . import funcs
    #     self.desc = funcs.CardOperation.desc_extract(self.card_id)

    def __eq__(self, other: "LinkDataPair"):
        return self.card_id == other.card_id


@dataclass
class LinkDataNode:  # 在root和group中的结点列表
    """LinkDataJSONInfo 的子部件"""
    card_id: "str" = ""
    nodeuuid: "str" = ""

    def __init__(self, card_id="", nodeuuid="", **kwargs):
        self.card_id = card_id
        self.nodeuuid = nodeuuid

    def todict(self):
        d = {}
        if self.card_id != "":
            d["card_id"] = self.card_id
        if self.nodeuuid != "":
            d["nodeuuid"] = self.nodeuuid
        return d

    def __contains__(self, item):
        return item in self.__dict__

    def __eq__(self, other):
        if type(other) == type(self):
            return other.card_id == self.card_id and other.nodeuuid == self.nodeuuid
        else:
            return other.card_id == self.card_id


@dataclass
class LinkDataGroup:  # group对象
    """LinkDataJSONInfo 的子部件"""
    name: "str" = ""
    children: "list[LinkDataNode]" = None

    def todict(self):
        d = {"name": self.name, "children": [child.todict() for child in self.children]}
        return d


@dataclass
class LinkDataJSONInfo:
    """
    这个东西, 他是中转站, 当你从DB读取出JSON数据, 需要到这里来加工一下, 变得更好用一些.
    要保证数据的同步性
        {
    "backlink": [], #backlink只用储存card_id, backlink 是文内链接校对用的
    "version": 2, #将来会用
    "link_list": [ #链接列表,也就是所有有关的卡片
        {
            "card_id": "1333355241723",
            "desc": "intellect",
            "dir": "\u2192"
        }
    ],
    "self_data": { #自身的数据
        "card_id": "1333355241734",
        "desc": "",
        "get_desc_from":0, #此项为version3 版本添加, 0表示desc取自json,1表示desc取自card,即同步更新,默认不同步
    },
    "root": [ #根节点, 是anchor的第一层
            {"card_id": "1333355241723"},
            {"nodeuuid":"xsasafzxc"}
        ],
    "node": { #在root中查找到键名为nodename时,在这里找他的列表,
            "xsasafzxc":{
                "name":"new_group",
                "children":[{"card_id":"1620468291507"},{"card_id":"1620468290938"}, {"card_id":"1620468289832"}]
            }
        }
    }

    """
    backlink: "list[str]"
    version: "int"
    link_list: "list[LinkDataPair]"
    self_data: "LinkDataPair"
    root: "list[LinkDataNode]"
    node: "dict[str,LinkDataGroup]"
    non_root_card:"list[LinkDataNode]"
    link_dict: "dict[str,LinkDataPair]" = None

    def __init__(self, record: "dict"):
        """一般只用在DB中读取, DB读取先经过zip_up得到字典,字典的第一个键是card_id,第二个键是data"""
        from . import funcs
        self._src_data = record
        self.non_root_card=[]
        if not isinstance(record["data"], dict):
            try:
                d = json.loads(record["data"])
                # showInfo("LinkDataJSONInfo.__init__:try"+json.dumps(d))
            except:
                from ..bilink.linkdata_admin import get_template, write_card_link_info
                from . import funcs
                d = get_template(record["card_id"], desc="card with error")
                funcs.data_crashed_report(record)
                write_card_link_info(d["self_data"]["card_id"], d["data"])
        else:
            d = record["data"]
        self.backlink = d["backlink"]
        self.node = {}
        # 兼容性更新, 将 原来的 nodename 改为 nodeuuid, 并且更改version 1 的组织形式
        if d["version"] == 1:
            # if __name__ == "__main__":
            #     from lib.common_tools import funcs
            # else:
            #     from . import funcs
            nodename_nodeuuid_map = {}
            for nodename, nodelist in d["node"].items():
                nodeuuid = funcs.UUID.by_random()
                nodename_nodeuuid_map[nodename] = nodeuuid
                self.node[nodeuuid] = LinkDataGroup(name=nodename, children=[LinkDataNode(**node) for node in nodelist])

            self.root = [LinkDataNode(card_id=link["card_id"] if "card_id" in link else ""
                                      , nodeuuid=nodename_nodeuuid_map[link["nodename"]] if "nodename" in link else ""
                                      ) for link in d["root"]]
        else:
            for groupuuid, groupinfo in d["node"].items(): #把group结点拿出来赋值
                self.node[groupuuid] = LinkDataGroup(name=groupinfo["name"],
                                                     children=[LinkDataNode(**node) for node in groupinfo["children"]])
                self.non_root_card+=list(filter(lambda x:x.card_id!="",self.node[groupuuid].children))
            self.root = [LinkDataNode(**link) for link in d["root"]]
        self.link_list = [LinkDataPair(**link) for link in d["link_list"] if funcs.CardOperation.exists(link["card_id"])]
        self.self_data = LinkDataPair(**d["self_data"])
        self.link_dict = {}
        for pair in self.link_list:
            self.link_dict[pair.card_id] = pair
            if pair not in self.non_root_card and pair not in self.root:
                self.root.append(LinkDataNode(card_id=pair.card_id))
        for pair in self.root:
            if pair.card_id!="" and pair.card_id not in self.link_dict:
                self.root.remove(pair)
        self.version = 2

    def todict(self):
        f = {"card_id": self.self_data.card_id}
        d = {}
        d["backlink"] = self.backlink
        d["version"] = self.version
        d["link_list"]: "list[dict[str,Any]]" = []
        for pair in self.link_list:
            d["link_list"].append(pair.todict())
        d["self_data"] = self.self_data.to_self_dict()
        d["root"] = []
        for node in self.root:
            d["root"].append(node.todict())
        d["node"] = {}
        for groupuuid, groupli in self.node.items():
            d["node"][groupuuid] = groupli.todict()
        d["link_dict"] = {}
        for k, v in self.link_dict.items():
            d["link_dict"][k] = v.todict()
        f["data"] = d
        return f

    @property
    def to_DB_record(self):
        s = json.dumps(self.todict()["data"],ensure_ascii=False)
        d = {"card_id": self.self_data.card_id, "data": s}
        return d

    def save_to_DB(self):
        from ..bilink import linkdata_admin
        from .G import DB
        # data,card_id = self.to_DB_record["data"],self.to_DB_record["card_id"]
        # DB.go(DB.table_linkinfo).update(DB.LET(data=data),where=DB.EQ(card_id=card_id)).commit()

        linkdata_admin.write_card_link_info(**self.to_DB_record)

    def __contains__(self, item):
        """card_id 是否在 link_list中"""
        d = [pair.card_id for pair in self.link_list]
        return item in d

    def append_link(self, pair:LinkDataPair):
        self.link_list.append(pair)
        self.root.append(LinkDataNode(card_id=pair.card_id))

    def remove_link(self, pair: LinkDataPair):
        if pair in self.link_list:
            self.link_list.remove(pair)
        if pair in self.root:
            self.root.remove(LinkDataNode(card_id=pair.card_id))
        for uuid, groupli in self.node.items():
            if pair in groupli.children:
                groupli.children.remove(LinkDataNode(card_id=pair.card_id))

    def add_tag(self, tag):
        from . import funcs
        CardId = funcs.Compatible.CardId()
        card = mw.col.getCard(CardId(int(self.self_data.card_id)))
        note = card.note()
        note.add_tag(tag)
        note.flush()

    def add_timestamp_tag(self, timestamp):
        self.add_tag(f"""hjp-bilink::timestamp::{timestamp}""")




# class NoRepeatShortcut(QShortcut):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.setAutoRepeat(False)


class AllEventAdmin(object):
    # from . import funcs

    def __init__(self, event_list):
        self.event_dict:"list" = event_list

    def bind(self):
        from . import funcs
        event_dict = funcs.event_handle_connect(self.event_dict)
        # AllEvents.update(event_dict)
        # print(len(AllEvents))
        return self

    def unbind(self, classname=""):
        from . import funcs
        funcs.event_handle_disconnect(self.event_dict)
        if not classname == "":
            # print(f"{classname} all events unbind")
            pass
        return self


class Logic:
    class BOX:
        """仅用作传输,不作别的处理, BOX之间可以用 and,or,not,+等运算符 连续拼接字符串, 采用安全的参数输入方法"""

        def __init__(self, string, values):
            self.string: str = string
            self.values: list = values

        def __and__(self, other: "DB_admin.BOX"):
            string = f""" ( {self.string} ) AND ({other.string}) """
            values = self.values + other.values
            return DB_admin.BOX(string, values)

        def __or__(self, other: "DB_admin.BOX"):
            string = f""" ( {self.string} ) OR ({other.string}) """
            values = self.values + other.values
            return DB_admin.BOX(string, values)

        def __invert__(self):
            string = f""" NOT ({self.string})"""
            values = self.values
            return DB_admin.BOX(string, values)

        def __add__(self, other: "DB_admin.BOX"):
            string = f"""( {self.string} ) {other.string}"""
            values = self.values + other.values
            return DB_admin.BOX(string, values)

    @staticmethod
    def IN(colname, *value):
        """
        *value: 多个值
        """
        Q = ("?," * len(value))[:-1]
        string = colname + f" IN ({Q}) "
        return Logic.BOX(string, list(value))

    @staticmethod
    def LIKE(colname, value):
        """需要自己加%进行模糊匹配"""
        value = re.sub(r"\s", "%", value)
        return Logic.BOX(colname + " LIKE (?) ", ["%"+value+"%"]) # 不要加冒号

    @staticmethod
    def REGEX(colname,value):
        return Logic.BOX(colname + " REGEXP (?) ", ["'" + value + "'"])

    @staticmethod
    def EQ(LOGIC="AND", **kwargs):
        string = ""
        values = []
        for k, v in kwargs.items():
            string += f" {k}=? {LOGIC} "
            values.append(v)
        string = re.sub(f"{LOGIC}\s+$", "", string)
        return Logic.BOX(string, values)

    @staticmethod
    def LIMIT(count, offset=0):
        value = []
        string = f"LIMIT {count} OFFSET {offset}"
        return Logic.BOX(string, value)

    @staticmethod
    def LET(**kwargs):
        """
        a=?,b=?,c=?
        确保插入的都是数据库字段, 不然就等着报错吧!,
        LET与EQ的区别:
            LET得到的形式是string: a=?,b=?,c=?, value:[av,bv,cv], 主要用来赋值
            EQ的形式是: string: a=av and b=bv ... 主要用来比较
        """
        string = ",".join([k + "=? " for k in list(kwargs.keys())])
        value = list(kwargs.values())
        return Logic.BOX(string, value)


class DB_admin(object):
    """ # dict_TABLE_Field={
    #     "uuid":"varchar(8) primary key not null unique",
    #     "x":"float not null",
    #     "y":"float not null",
    #     "w":""
    # }
    # all_fields=[#用来确保字段对齐
    #     "x","y","w","h","QA","text_","textQA","card_id","pagenum","ratio","pdfname","pageshift"
    # ]
    数据库操作流程: 1 执行go选择一张表,2 执行select或类似的语句,组成SQL,3commit或return_all执行取得结果,
    其中 2组成SQL的时候会插入队列, 再在3中弹出队列执行,
    执行时会判断你传入的是list还是str, 如果是前者,则认为list的第二个元素是待插入值,第一个元素是字符串,其中的问号是占位符
    数据库取回的结果, 是二维表, results[][], 第一个索引指定行, 第二个索引指定列
    """
    table_clipbox = 0
    table_pdfinfo = 1
    table_linkinfo = 2
    table_Gview=3
    table_GviewCard=4
    table_GviewConfig=5
    table_Gview_cache=6

    sqlstr_TABLE_CREATE = """create table if not exists {tablename} ({fields})"""
    sqlstr_TABLE_DROP = """DROP TABLE IF EXISTS {表名}"""
    sqlstr_TABLE_PRAGMA = """PRAGMA table_info({tablename})"""
    sqlstr_TABLE_ALTER = """alter table {tablename} add column {colname} {define}"""
    SQL_移除表字段 = """alter table {表名} drop column {字段名}"""
    sqlstr_TABLE_EXIST = """select count(*) from sqlite_master where type="table" and name ="{tablename}" """
    sqlstr_RECORD_COUNT = """select count(*) from {tablename} where {where} """
    sqlstr_RECORD_SELECT = """select * from {tablename} where {where} """
    sqlstr_RECORD_SELECT_ALL = """select * from {tablename} """
    sqlstr_RECORD_UPDATE = """update {tablename} set {values} where {where}"""
    sqlstr_RECORD_DELETE = """delete from {tablename} where {where} """
    sqlstr_RECORD_INSERT = """insert into {tablename} ({cols}) values ({vals}) """
    sqlstr_RECORD_REPLACE = """ replace into {tablename} ({cols}) values ({vals})"""
    ################################下面是查询语句设计########################

    # class BOX:
    #     """仅用作传输,不作别的处理, BOX之间可以用 and,or,not,+等运算符 连续拼接字符串, 采用安全的参数输入方法"""
    #
    #     def __init__(self, string, values):
    #         self.string: str = string
    #         self.values: list = values
    #
    #     def __and__(self, other: "DB_admin.BOX"):
    #         string = f""" ( {self.string} ) AND ({other.string}) """
    #         values = self.values + other.values
    #         return DB_admin.BOX(string, values)
    #
    #     def __or__(self, other: "DB_admin.BOX"):
    #         string = f""" ( {self.string} ) OR ({other.string}) """
    #         values = self.values + other.values
    #         return DB_admin.BOX(string, values)
    #
    #     def __invert__(self):
    #         string = f""" NOT ({self.string})"""
    #         values = self.values
    #         return DB_admin.BOX(string, values)
    #
    #     def __add__(self, other: "DB_admin.BOX"):
    #         string = f"""( {self.string} ) {other.string}"""
    #         values = self.values + other.values
    #         return DB_admin.BOX(string, values)

    BOX=Logic.BOX

    @staticmethod
    def IN(colname, *value):
        """
        *value: 多个值
        """
        return Logic.IN(colname, *value)

    @staticmethod
    def LIKE(colname, value:"str"):
        """需要自己加%进行模糊匹配"""

        return Logic.LIKE(colname , value)
        # return Logic.LIKE(colname + " LIKE (?) ", ["'%" + 新值 + "%'"])

    @staticmethod
    def REGEX(colname, value):
        return Logic.BOX(colname + " REGEXP (?) ", ["'" + value + "'"])

    @staticmethod
    def EQ(LOGIC="AND", **kwargs):
        return Logic.EQ(LOGIC=LOGIC, **kwargs)

    @staticmethod
    def LIMIT(count, offset=0):
        return Logic.LIMIT(count,offset=offset)

    @staticmethod
    def LET(**kwargs):
        """
        a=?,b=?,c=?
        确保插入的都是数据库字段, 不然就等着报错吧!,
        LET与EQ的区别:
            LET得到的形式是string: a=?,b=?,c=?, value:[av,bv,cv], 主要用来赋值
            EQ的形式是: string: a=av and b=bv ... 主要用来比较
        """
        return Logic.LET(**kwargs)

    # @staticmethod
    # def LIKE(colname, value):
    #     """需要自己加%进行模糊匹配"""
    #     return Logic.LIKE(colname,value)
    #
    # @staticmethod
    # def EQ(LOGIC="AND", **kwargs):
    #     string = ""
    #     values = []
    #     for k, v in kwargs.items():
    #         string += f" {k}=? {LOGIC} "
    #         values.append(v)
    #     string = re.sub(f"{LOGIC}\s+$", "", string)
    #     return DB_admin.BOX(string, values)

    # @staticmethod
    # def LIMIT(count, offset=0):
    #     value = []
    #     string = f"LIMIT {count} OFFSET {offset}"
    #     return DB_admin.BOX(string, value)

    # @staticmethod
    # def VALUEEQ(**kwargs):
    #     """确保插入的都是数据库字段, 不然就等着报错吧!,
    #     VALUEEQ与EQ的区别:
    #         VALUEEQ得到的形式是string: a=?,b=?,c=?, value:[av,bv,cv], 主要用来赋值
    #         EQ的形式是: string: a=av and b=bv ... 主要用来比较
    #     """
    #     string = ",".join([k + "=? " for k in list(kwargs.keys())])
    #     value = list(kwargs.values())
    #     return DB_admin.BOX(string, value)

    def __init__(self):
        # self.tab_name = Get._().dir_clipboxTable_name
        if __name__ == "__main__":
            from lib.common_tools.src_admin import SrcAdmin
            pass
        else:
            from .src_admin import SrcAdmin
        self.tab_name = None
        self.db_dir = SrcAdmin.start().path.DB_file
        self.connection:"sqlite3.Connection" = None
        self.cursor:"sqlite3.Cursor" = None
        self.sqlstr_isbussy = False
        self.excute_queue = []  # 队列结构

    def table_fields_align(self):
        """确保字段对齐,如果不对齐,则要增加字段,字段可以增加,一般不重命名和删除"""
        pragma = self.pragma().return_all()
        table_fields = set([i[1] for i in pragma])
        # print(table_fields)
        compare_fields = set(Table.switch[self.curr_tabtype].get_dict().keys())
        # print(compare_fields)
        need_add_fields = list(compare_fields - table_fields)
        需要移除字段 = list(table_fields - compare_fields)
        if need_add_fields:
            # print("update table fields")
            for field in need_add_fields:
                self.alter_add_col(field).commit()
        if 需要移除字段:
            for 字段 in 需要移除字段:
                self.移除字段(字段).commit()


    def pragma(self):
        """返回字段结构"""
        s = self.sqlstr_TABLE_PRAGMA.format(tablename=self.tab_name)
        self.excute_queue.append(s)
        return self

    def alter_add_col(self, colname):
        all_column_names = Table.switch[self.curr_tabtype].get_dict()
        s = self.sqlstr_TABLE_ALTER.format(tablename=self.tab_name, colname=colname,
                                           define=all_column_names[colname])
        self.excute_queue.append(s)
        return self

    def 移除字段(self,字段名):
        s = self.SQL_移除表字段.format(表名=self.tab_name, 字段名=字段名)
        self.excute_queue.append(s)
        return self
        pass
    def go(self, curr_tabtype=None):
        """go是DB开始的入口,end是结束的标志,必须要调用end结束
        curr_tabtype:
            table_clipbox = 0
            table_pdfinfo = 1
            table_linkinfo = 2
            table_Gview=3
        """
        # print(curr_tabtype)
        if not curr_tabtype:
            curr_tabtype = self.table_clipbox
        self.excute_queue = []
        self.result_queue = []
        self.connection = sqlite3.connect(self.db_dir)
        self.connection.create_function("regexp",2,self._regexp)
        self.cursor = self.connection.cursor()
        self.curr_tabtype = curr_tabtype
        # self.tab_name = Table.switch[curr_tabtype][0]
        self.tab_name = Table.switch[curr_tabtype].tablename
        self.table_ifEmpty_create().commit()
        self.table_fields_align()
        return self

    def _regexp(self,expr,item):
        """本函数用于注册SQLlite需要的功能,不对外使用"""
        reg = re.compile(expr)
        return reg.search(item) is not None

    def 表存在(self,表名索引):
        表名 = Table.switch[表名索引].tablename
        self.go(表名索引)
        self.excute_queue.append(self.sqlstr_TABLE_EXIST.format(tablename=表名))
        return len(self.return_all().results)>0

        pass

    def 表删除(self, 表名索引):
        """安全删除, 删除前会检查表是否存在"""
        表名 = Table.switch[表名索引].tablename
        self.go(表名索引)
        self.excute_queue.append(self.sqlstr_TABLE_DROP.format(表名=表名))
        self.commit()
        pass



    def end(self):
        from . import funcs
        funcs.Utils.print("end here")
        if self.connection is not None:
            self.connection.close()

    ########################### use for clipbox ########################
    def del_card_id(self, condition: "DB_admin.BOX", card_id, callback=None):
        """使用的前提是在table_clipbox表中,目的是删掉对应clipbox已经不支持的卡片"""
        records = self.select(condition).return_all().zip_up().to_clipbox_data()
        # uuidli = [item["uuid"] for item in records]
        for r in records:
            card_idlist: "list[str]" = list(filter(lambda x: x.isdecimal(), r.card_id.split(",")))
            if card_id in card_idlist:
                card_idlist.remove(card_id)
            r.card_id = ",".join(card_idlist)
            self.update(where=self.EQ(uuid=r.uuid), values=self.LET(**r.to_dict())).commit(callback=callback)

    def add_card_id(self, condition: "DB_admin.BOX", card_id, callback=None):
        """使用的前提是在table_clipbox表中,目的是增加对应clipbox没有支持的卡片"""
        records = self.select(condition).return_all().zip_up().to_clipbox_data()
        # uuidli = [item["uuid"] for item in records]
        for r in records:
            card_idlist: "list[str]" = list(filter(lambda x: x.isdecimal(), r.card_id.split(",")))
            if card_id not in card_idlist:
                card_idlist.append(card_id)
            r.card_id = ",".join(card_idlist)
            self.update(where=self.EQ(uuid=r.uuid), values=self.LET(**r.to_dict())).commit(callback=callback)
    ########################### use for clipbox ########################


    # 存在性检查,如果为空则创建
    def table_ifEmpty_create(self):
        s = self.create_table()
        self.excute_queue.append(s)
        return self

    def create_table(self):
        # make fields
        # d = Table.switch[self.curr_tabtype][()
        d = Table.switch[self.curr_tabtype].get_dict()
        fields = ""
        for k, v in d.items():
            fields += f"\n{k} {v},"
        fields = fields[:-1]
        s = self.sqlstr_TABLE_CREATE.format(tablename=self.tab_name, fields=fields)
        return s

    def exists(self, box: "Logic.BOX"):
        """平时用这个比较好"""
        from . import funcs
        s = self.sqlstr_RECORD_COUNT.format(tablename=self.tab_name,where=box.string)
        self.excute_queue.append([s, box.values])
        result = self.return_all()
        return result[0][0] > 0 # 第一条记录的第一个字段

    # 存在性检查
    # def exists_check(self, box: "Logic"):
    #     """
    #     原理是 select count(*) from table  where box
    #     这个检查需要提交commit,不建议使用"""
    #     s = self.sqlstr_RECORD_COUNT.format(tablename=self.tab_name, where=box.string)
    #     self.excute_queue.append([s, box.values])
    #     return self

    def valCheck(self, k: "str", v: "str"):
        constrain = Table.switch[self.curr_tabtype].constrain()
        if k in constrain["string"]:
            return f""" "{v}"  """
        else:
            return v

    def where_maker(self, **values):
        # print(values)
        where = ""
        if "IN" in values:
            colname = values["colname"]
            val_li = ",".join([self.valCheck(colname, val) for val in values["vals"]])
            where = f""" {colname} in ({val_li})"""
        elif "LIKE" in values:
            colname = values["colname"]
            vals = values["vals"]
            where = f""" {colname} like "{vals}" """
        else:
            b = values["BOOL"] if "BOOL" in values else " AND "
            all_column_names = Table.switch[self.curr_tabtype].get_dict()
            for k, v in values.items():
                if v is not None and k in all_column_names:
                    where += f""" {k}={self.valCheck(k, v)} {b}"""
            where = re.sub(f"{b}\s*$", "", where)
            if where == "":
                raise ValueError("where is empty!")
        return where

    def value_maker(self, **values):
        """尽管输入 key=value的形式即可"""
        string = ""
        val = []
        all_column_names = Table.switch[self.curr_tabtype].get_dict()
        for k, v in values.items():
            if k in all_column_names:
                string += f""" {k}=? ,"""
                val.append(v)
        if string == "":
            raise ValueError("values is empty!")
        return DB_admin.BOX(string, val)

    def selectAll(self,tablename:"str"):
        self.excute_queue.append(self.sqlstr_RECORD_SELECT_ALL.format(tablename=tablename))
        return self

    def select(self, box: "DB_admin.BOX" = None, **kwargs):
        assert box is not None or len(kwargs) > 0
        if box is None and len(kwargs) > 0:
            box = self.EQ(**kwargs)
        s = self.sqlstr_RECORD_SELECT.format(tablename=self.tab_name, where=box.string)
        self.excute_queue.append([s, box.values])

        return self

    def replace(self,**values):
        cols = ""
        vals = ""
        all_column_names = Table.switch[self.curr_tabtype].get_dict()
        entity = []
        for k, v in values.items():
            if k not in all_column_names:
                continue
            cols += k + ","
            vals += "?,"  # 最后一个逗号要去掉
            entity.append(v)
        s = self.sqlstr_RECORD_REPLACE.format(tablename=self.tab_name, cols=cols[0:-1], vals=vals[0:-1])


        self.excute_queue.append([s, entity])
        return self

    def update(self, values: "Logic.BOX" = None, where: "Logic.BOX" = None):
        """values,where 应该是一个字典, k是字段名,v是字段值"""
        assert values is not None and where is not None
        entity = values.values + where.values
        s = self.sqlstr_RECORD_UPDATE.format(tablename=self.tab_name, values=values.string, where=where.string)
        self.excute_queue.append([s, entity])
        return self

    # def 保存_不存在则新建(self,):

    # 增
    def insert(self, **values):
        """insert 很简单, 不必走 box, 例子: insert(A=a,B=b,C=c)"""
        cols = ""
        vals = ""
        all_column_names = Table.switch[self.curr_tabtype].get_dict()
        entity = []
        for k, v in values.items():
            if k not in all_column_names:
                continue
            cols += k + ","
            vals += "?,"  # 最后一个逗号要去掉
            entity.append(v)
        s = self.sqlstr_RECORD_INSERT.format(tablename=self.tab_name, cols=cols[0:-1], vals=vals[0:-1])
        self.excute_queue.append([s, entity])
        return self


    def delete(self, where: "DB_admin.BOX"):
        s = self.sqlstr_RECORD_DELETE.format(tablename=self.tab_name, where=where.string)
        self.excute_queue.append([s, where.values])
        return self


    def return_all(self, callback=None):
        """select 用这个 """
        s = self.excute_queue.pop(0)
        # print(s)
        if s != "":
            if callback:
                callback(s)
            if type(s) == list:
                result = self.cursor.execute(s[0], s[1]).fetchall()
            else:
                result = self.cursor.execute(s).fetchall()
            all_column_names = Table.switch[self.curr_tabtype].get_dict().keys()
            return DBResults(result, all_column_names, self.curr_tabtype)
    def 批量插入(self,值):
        序列_表字段 = list(Table.switch[self.curr_tabtype].get_dict().keys())
        表名 = Table.switch[self.curr_tabtype].tablename
        占位符 = ",".join("?"*len(序列_表字段))
        SQL命令 = f"INSERT INTO {表名} VALUES({占位符});"
        游标 = self.connection.cursor()
        游标.executemany(SQL命令,值)
        self.connection.commit()

    def 批量执行(self, 参数_命令队列=None):

        SQL队列 = 参数_命令队列 if 参数_命令队列 else self.excute_queue
        while SQL队列:
            命令 = SQL队列.pop(0)
            if type(命令)==list:
                结果 = self.cursor.execute(命令[0], 命令[1])
            else:
                结果 = self.cursor.execute(命令)
        self.connection.commit()

    def commit(self, callback=None,need_commit=True):
        s = self.excute_queue.pop(0)

        if s:
            if callback:
                callback(s.__str__())
            if type(s) == list:
                result = self.cursor.execute(s[0], s[1]) #注意update的时候,字符串对象需要多加一个""
            else:
                if callback:callback("即将执行")
                result = self.cursor.execute(s)
            if need_commit:
                if callback:callback("即将commit")
                self.connection.commit()
            return result

    def __enter__(self):
        self.cursor.execute("begin")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if len(self.excute_queue)>0:
            raise ValueError("你有未执行完的sql语句!")
        self.connection.commit()
        # self.end()



class Table:
    @dataclass
    class BaseFields:
        @property
        def tablename(self):
            return self.__class__.__name__

        def get_dict(self):
            data = collections.OrderedDict()
            [data.__setitem__(name, self.__dict__[name]) for name in self.ordered_fields()]
            return data

        @abc.abstractmethod
        def constrain(self):
            raise NotImplementedError("")

        @abc.abstractmethod
        def ordered_fields(self)->"list[str]":
            raise NotImplementedError("")

        pass
    @dataclass
    class CARD_LINK_INFO(BaseFields):
        card_id: "str" = "varchar primary key not null unique"
        data: "str" = "text not null"
        def constrain(self):
            return  {
        "string": ["data"],
        "number": ["card_id"]
    }

        def ordered_fields(self):
            return ["card_id","data"]

    @dataclass
    class PDF_INFO_TABLE(BaseFields):
        def ordered_fields(self) -> "list[str]":
            return ["uuid","pdf_path","ratio","offset"]
            pass

        uuid: "str" = "varchar primary key not null unique"
        pdf_path: "str" = "varchar not null"
        ratio: "float" = "float not null"
        offset: "int" = "integer not null"
        def constrain(self):
            return  {
        "string": ["uuid", "pdf_path"],
        "number": ["ratio", "offset"]
    }



    @dataclass
    class CLIPBOX_INFO_TABLE(BaseFields):
        def ordered_fields(self) -> "list[str]":
            return ["uuid","x","y","w","h","QA","comment","commentQA","card_id","ratio","pagenum","pdfuuid"]
            pass

        uuid: "str" = "varchar(8) primary key not null unique"
        x: "str" = "float not null"
        y: "str" = "float not null"
        w: "str" = "float not null"
        h: "str" = "float not null"
        QA: "str" = "integer not null"
        comment: "str" = "text"
        commentQA: "str" = "integer not null"
        card_id: "str" = "varchar not null"
        ratio: "str" = "float not null"
        pagenum: "str" = "integer not null"
        pdfuuid: "str" = "varchar not null"
        def constrain(self):
            return {
                    "number": ["commentQA", "QA", "x", "y", "w", "h", "ratio", "pagenum"],
                    "string": ["uuid", "card_id", "comment", "pdfuuid"]
            }
    @dataclass
    class GRAPH_VIEW_TABLE(BaseFields):
        """grapher的固定视图,G代表graph, 目前想到的串有,uuid,name,member_info_json, 需要根据卡片id反查所属view时,查找"""

        def ordered_fields(self) -> "list[str]":
            return ["uuid","name","nodes","edges","config", "view_created_time", "view_last_visit", "view_last_edit",  "view_last_review",
                    "view_visit_count", "card_content_cache"]
            pass

        uuid: "str" = "varchar(8) primary key not null unique"
        name: "str" = "varchar not null"
        nodes:"str" = "text"
        edges:"str" = "text"
        config:"str" = "varchar"
        view_created_time:"str" = "integer"
        view_last_visit:"str"="integer"
        view_last_edit:"str" ="integer"
        view_last_review:"str"="integer"
        view_visit_count:"str"="integer"  # 浏览次数
        card_content_cache:"str" = "text"  # 卡片内容缓存, 用来实现按照卡片内容搜索视图.
        def constrain(self):
            return {
        "string":["uuid","name","nodes","edges","config","card_content_cache"],
        "number":["view_created_time","view_last_edit","view_last_visit","view_visit_count","view_last_review"]
    }
    @dataclass
    class GRAPH_VIEW_CARD_TABLE(BaseFields):  # 这个表没用
        def ordered_fields(self) -> "list[str]":
            return ["card_id","views","default_views"]
        card_id: "str" = "varchar primary key not null unique"
        views: "str" = "text"
        default_views: "str" = "text"
        def constrain(self):
            return {
                "string": ["card_id", "views", "default_views",],
                "number": []
            }

    @dataclass
    class GRAPH_VIEW_CONFIG(BaseFields):
        def ordered_fields(self) -> "list[str]":
            return ["uuid","name","data"]
            pass

        uuid: "str" = "varchar(8) primary key not null unique"
        name: "str" = "varchar not null"
        data:"str" = "text"
        def constrain(self):
            return {
                    "string": ["uuid", "name", "data", ],
                    "number": []
            }

    @dataclass
    class GRAPH_VIEW_CACHE(BaseFields):
        def ordered_fields(self) -> "list[str]":
            return ["uuid","cache"]
            pass

        uuid: "str" = "varchar(8) primary key not null unique"
        cache:"str" = "text"
        def constrain(self):
            return {
                    "string": ["uuid", "cache" ],
                    "number": []
            }

    class Const:
        clipbox = DB_admin.table_clipbox
        pdfinfo = DB_admin.table_pdfinfo
        linkinfo = DB_admin.table_linkinfo
        Gview = DB_admin.table_Gview
        GviewCard = DB_admin.table_GviewCard
        GviewConfig = DB_admin.table_GviewConfig
        GviewCache = DB_admin.table_Gview_cache

    switch = {
        Const.clipbox  : CLIPBOX_INFO_TABLE(),
        Const.pdfinfo  : PDF_INFO_TABLE(),
        Const.linkinfo  : CARD_LINK_INFO(),
        Const.Gview  : GRAPH_VIEW_TABLE(),
        Const.GviewCard  : GRAPH_VIEW_CARD_TABLE(),
        Const.GviewConfig : GRAPH_VIEW_CONFIG(),
        Const.GviewCache:GRAPH_VIEW_CACHE()
    }



class DBResults(object):
    """这个对象只读不写,是DB返回结果的容器的简单包装"""

    def __init__(self, results, all_column_names, curr_tabletype=0):
        self.results: "list" = results
        self.all_column_names = all_column_names
        self.curr_tabletype = curr_tabletype


    def zip_up(self, version=1):
        """zip只包装成字典, 如果要用dataclass ,请返回后自己包装"""
        new_results = self.DBdataLi()

        for row in self.results:
            record = self.DBdata()
            step1 = list(zip(self.all_column_names, row))
            for col in (step1):
                record[col[0]] = col[1]
            new_results.append(record)

        return new_results

    def __getitem__(self, key):
        return self.results[key]

    def __contains__(self, item):
        return item in self.results

    def __len__(self):
        return len(self.results)

    def __iter__(self):
        return self.results.__iter__()

    #############数据库取回的封装######################

    class DBdata(dict):

        def to_clipbox_data(self):
            return ClipboxRecord(**self)

        def to_pdfinfo_data(self):
            return PDFinfoRecord(**self)

        def to_givenformat_data(self, format):
            # showInfo("to_givenformat_data="+json.dumps(self))
            return format(self)

    class DBdataLi(list):
        """给数组附加一些功能"""

        def to_pdfinfo_data(self):
            li = [PDFinfoRecord(**i) for i in self]
            return li

        def to_clipbox_data(self):
            li = [ClipboxRecord(**i) for i in self]
            return li

        def to_gview_record(self):
            """导出的都是字符串,需要自己再转一次"""

            return [GviewRecord(**i) for i in self]

        def to_givenformat_data(self, _format,multiArgs=False):
            """
            multiArgs 的意思是传入的是一个多个key的字典, 而传入的_format接受多个参数,为了key对应参数, 因此要解包
            也可以根据_format需要的参数格式来选择是否要multiArgs
            """
            if multiArgs:
                return [_format(**i) for i in self]
            else:
                return [_format(i) for i in self]



class Record(QObject):
    @dataclass
    class GviewConfig(QObject):
        """要区分 GviewConfig和GviewConfigModel, 前者服务于数据库记录,可以叫做记录, 后者服务于UI模型,就叫模型"""


        def __init__(self,uuid=None, name=None, data=None):
            """这里的读取就是dict"""
            super().__init__()
            from . import  funcs,configsModel
            if uuid is not None and data is None:
                raise ValueError("有 uuid 但没有 data , 你是不是想读取Config? 读取请用 readModelFromDB")
            self.uuid = uuid if uuid else funcs.UUID.by_random()
            self.name = name if name else "graph config"
            self.data = self.initData(json.loads(data)) if data else self.initData({}) # 这个是模型
            # self.信号 =
            self.一致性检查()
            # print(f"initilizing gview config={self} ")
            if self.静态_存在于数据库中(self.uuid):
                self.saveModelToDB()
            # self.确定保存到数据库=True

        def 一致性检查(self):
            """本配置应用表中的视图应与对应视图的配置一致"""
            from . import funcs
            应用该配置的视图表:"list[str]" = self.data.appliedGview.value
            新值 = 应用该配置的视图表.copy()
            for 视图标识 in 应用该配置的视图表:
                视图模型 = funcs.GviewOperation.load(视图标识)
                if 视图模型.config!=self.uuid:
                    新值.remove(视图标识)
            self.data.appliedGview.setValue(新值)


        def initData(self,_data:"dict"):
            _data["uuid"] = self.uuid
            from .configsModel import GviewConfigModel
            template = GviewConfigModel()
            for k,v in _data.items():
                template[k]=v
            return template

        def getDict(self):
            d = self.__dict__.copy()
            d["data"] = json.dumps(self.data.get_dict(),ensure_ascii=False)
            return d

        def saveModelToDB(self):
            if self.data.元信息.确定保存到数据库:
                # self.一致性检查()
                from . import G
                G.DB.go(G.DB.table_GviewConfig)
                self.name = self.data.name.value
                if G.DB.exists(Logic.EQ(uuid=self.uuid)):
                    G.DB.update(values=Logic.LET(**self.getDict()),where=Logic.EQ(uuid=self.uuid)).commit()
                else:
                    G.DB.insert(**self.getDict()).commit()

        def 从数据库中删除(self):
            from . import G
            G.DB.go(G.DB.table_GviewConfig).delete(Logic.EQ(uuid=self.uuid)).commit()

        @staticmethod
        def 静态_存在于数据库中(uuid):
            from . import G
            DB = G.DB.go(G.DB.table_GviewConfig)
            return DB.exists(Logic.EQ(uuid=uuid))

        @staticmethod
        def 静态_含有某视图(视图标识,配置标识):
            配置模型 = Record.GviewConfig.readModelFromDB(配置标识)
            return 视图标识 in 配置模型.data.appliedGview.value

        @staticmethod
        def readModelFromDB(uuid):
            """这里可以当uuid为空表示新建一个配置"""
            if not uuid: raise ValueError(f" '{uuid}' 为非法标识, 请输入合法的标识!")

            from . import G
            DB = G.DB.go(G.DB.table_GviewConfig)
            result: "Record.GviewConfig" = DB.select(Logic.EQ(uuid=uuid)).return_all().zip_up().to_givenformat_data(Record.GviewConfig, multiArgs=True)[0]

            return result

        def __repr__(self):
            return self.data.__repr__()

        def __str__(self):
            return self.data.__str__()

@dataclass
class Pair:
    card_id: "str" = None
    desc: "str" = None

@dataclass
class GviewRecord:
    """视图数据库记录类"""
    uuid:str
    name:str
    nodes:str
    edges:str
    config:str = ""
    meta:"Optional[dict]"=None

    def __init__(self,*args,**kwargs):
        self.uuid = kwargs["uuid"]
        self.name = kwargs["name"]
        self.nodes = kwargs["nodes"]
        self.edges = kwargs["edges"]
        self.config = kwargs["config"]
        self.meta = kwargs


    def to_GviewData(self):
        from .configsModel import GViewData
        return GViewData(uuid=self.uuid,name=self.name,
                         nodes=json.loads(self.nodes),edges=json.loads(self.edges),config=self.config,meta=self.meta
                         )

@dataclass
class PDFinfoRecord:
    uuid: "str"
    pdf_path: "str"
    ratio: "float"
    offset: "int"


@dataclass
class ClipboxRecord:
    uuid: "str"
    x: "float"
    y: "float"
    w: "float"
    h: "float"
    QA: "int"
    commentQA: "int"
    card_id: "str"
    ratio: "float"
    pagenum: "int"
    pdfuuid: "str"
    comment: "str" = ""

    def to_dict(self):
        return self.__dict__.copy()



@dataclass
class Bricks:
    布局=layout=0
    组件=widget=1
    子代=kids=2
    描述=3
    triple = [layout,widget,kids]
    三元组 = [布局,组件,子代]
    四元组 = [布局,组件,子代,描述]

    @staticmethod
    def build(b:"dict"):
        """
        {
            layout:Vbox,
            kids:[
                {
                layout:Hbox,
                kids:[
                    {widget:lineEdit},
                    {widget:button}
                ]
                },
                {
                widget:View
                }
            ]
        }
        """
        layout, widget, kids = Bricks.triple

        kidsStack:"list[dict]"=[b]




@dataclass
class WidgetsBrick:
    def __init__(self,layout=None,widget=None,kids=None):
        self.kids:"list[WidgetsBrick]" = kids if kids else []
        self.layout:"QHBoxLayout|QVBoxLayout|QGridLayout"=layout
        self.widget:"QWidget" = widget
        print(self.kids,type(self.layout) if not self.layout else None,type(self.widget) if not self.widget else None)
        if layout:
            for w in self.kids:
                if w.widget:
                    self.layout.addWidget(w.widget)
                elif w.layout:
                    self.layout.addLayout(w.layout)

if __name__ == "__main__":
    data = """
    {
    "backlink": [],
    "version": 2,
    "link_list": [
        {
            "card_id": "1627437034945",
            "desc": "yeyeyeyeyeyeyeye2"
        },
        {
            "card_id": "1627437000208",
            "desc": "yeyeyeyeyeyeyeye333"
        }
    ],
    "link_dict": {},
    "self_data": {
        "card_id": "123456789",
        "desc": "耶稣他'爹 玩'什么"
    },
    "root": [
        {
            "nodeuuid": "86c916ed"
        },
        {
            "nodeuuid": "123d6855"
        },
        {
            "card_id": "1627437000208"
        }
    ],
    "node": {
        "86c916ed": {
            "name": "new_new_group",
            "children": [
                {
                    "card_id": "1627437034945"
                }
            ]
        },
        "123d6855": {
            "name": "new_group",
            "children": []
        }
    }
}
    """
    card_id = "4"
    record = {"card_id": card_id, "data": data}
    record2 = {"card_id": card_id, "data": "data"}
    # DB = DB_admin()
    # DB.go(DB.table_linkinfo).update2(values=record2,where={"card_id":card_id}).commit2(print)
    # a=DB.select(card_id="2").return_all().zip_up()[0]
    # print(a)
    # DB = DB_admin()
    # DB.go(DB.table_linkinfo)
    # DB.delete(DB.EQ(card_id=card_id)).commit(print)
    # DB.insert(**record).commit(print)
    # x = DB.go(DB.table_linkinfo).select(DB.EQ(card_id=card_id)).return_all(print).zip_up()
    # print(x)
    # # DB.delete(DB.EQ(card_id=card_id)).commit(print)
    # DB.update(values=DB.VALUEEQ(data=record2["data"]), where=DB.EQ(card_id=card_id)).commit(print)
    # x = DB.select(DB.EQ(card_id=card_id)).return_all().zip_up()
    # print(x)

    # x=DB.go(DB.table_clipbox).select2(
    #      (DB.EQ(pdfuuid="fbe0cb0e-8eba-39e9-8cc7-a6eb7c18763c")
    #     &DB.LIKE("card_id","%16274%")
    #     &~DB.IN("pagenum",1,0))+DB.LIMIT(2)).return_all2(print).zip_up()
    # print(len(x))
    pass
