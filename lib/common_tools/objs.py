# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = '$NAME.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2021/7/30 9:09'
"""
import json
import re
import sqlite3
from dataclasses import dataclass
from typing import Any, Union
from urllib.parse import unquote

from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import QShortcut
from aqt import mw

class NONE:
    @staticmethod
    def activateWindow()->False:
        return False
@dataclass
class CmdArgs:
    type:"str"
    args:"str"
    def __init__(self,cmdargsli:[str,str]):
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

class CascadeStr:
    @dataclass
    class Node:
        item: "QStandardItem"
        children: "dict[str,CascadeStr.Node]"


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

    def flatten(self):
        """降维, 把group去掉, 通常用于complete_map的需要"""
        d = []
        for group in self.IdDescPairs:
            for pair in group:
                d.append(pair)
        return d


@dataclass
class LinkDataPair:
    """LinkDataJSONInfo 的子部件, 也可以独立使用"""
    card_id: "str"
    desc: "str" = ""
    dir: "str" = "→"

    @property
    def int_card_id(self):
        return int(self.card_id)

    def todict(self):
        return self.__dict__

    def update_desc(self):
        from . import funcs
        self.desc = funcs.desc_extract(self.card_id)

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
    "backlink": [], #backlink只用储存card_id
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
        "desc": ""
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
    link_dict: "dict[str,LinkDataPair]" = None

    def __init__(self, record: "dict"):
        """一般只用在DB中读取, DB读取先经过zip_up得到字典,字典的第一个键是card_id,第二个键是data"""
        self._src_data = record
        if not isinstance(record["data"], dict):
            try:
                d = json.loads(record["data"])
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
            if __name__ == "__main__":
                from lib.common_tools import funcs
            else:
                from . import funcs
            nodename_nodeuuid_map = {}
            for nodename, nodelist in d["node"].items():
                nodeuuid = funcs.UUID.by_random()
                nodename_nodeuuid_map[nodename] = nodeuuid
                self.node[nodeuuid] = LinkDataGroup(name=nodename, children=[LinkDataNode(**node) for node in nodelist])

            self.root = [LinkDataNode(card_id=link["card_id"] if "card_id" in link else ""
                                      , nodeuuid=nodename_nodeuuid_map[link["nodename"]] if "nodename" in link else ""
                                      ) for link in d["root"]]
        else:
            for groupuuid, groupinfo in d["node"].items():
                self.node[groupuuid] = LinkDataGroup(name=groupinfo["name"],
                                                     children=[LinkDataNode(**node) for node in groupinfo["children"]])
            self.root = [LinkDataNode(**link) for link in d["root"]]
        self.link_list = [LinkDataPair(**link) for link in d["link_list"]]
        self.self_data = LinkDataPair(**d["self_data"])
        self.link_dict = {}
        for pair in self.link_list:
            self.link_dict[pair.card_id] = pair
            if pair not in self.root:
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
        d["self_data"] = self.self_data.todict()
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
        s = json.dumps(self.todict()["data"])
        d = {"card_id": self.self_data.card_id, "data": s}
        return d

    def save_to_DB(self):
        from ..bilink import linkdata_admin
        linkdata_admin.write_card_link_info(**self.to_DB_record)

    def __contains__(self, item):
        """card_id 是否在 link_list中"""
        d = [pair.card_id for pair in self.link_list]
        return item in d

    def append_link(self, pair):
        self.link_list.append(pair)
        self.root.append(pair)

    def remove_link(self, pair: LinkDataPair):
        if pair in self.link_list:
            self.link_list.remove(pair)
        if pair in self.root:
            self.root.remove(LinkDataNode(pair.card_id))
        for uuid, groupli in self.node.items():
            if pair in groupli.children:
                groupli.children.remove(LinkDataNode(pair.card_id))

    def add_tag(self, tag):
        from . import funcs
        CardId = funcs.Compatible.CardId()
        card = mw.col.getCard(CardId(int(self.self_data.card_id)))
        note = card.note()
        note.add_tag(tag)
        note.flush()

    def add_timestamp_tag(self, timestamp):
        self.add_tag(f"""hjp-bilink::timestamp::{timestamp}""")


class NoRepeatShortcut(QShortcut):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAutoRepeat(False)


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
    """
    table_clipbox = 0
    table_pdfinfo = 1
    table_linkinfo = 2

    sqlstr_TABLE_CREATE = """create table if not exists {tablename} ({fields})"""

    sqlstr_TABLE_PRAGMA = """PRAGMA table_info({tablename})"""
    sqlstr_TABLE_ALTER = """alter table {tablename} add column {colname} {define}"""
    sqlstr_TABLE_EXIST = """select count(*) from sqlite_master where type="table" and name ="{tablename}" """
    sqlstr_RECORD_EXIST = """select count(*) from {tablename} where {where} """
    sqlstr_RECORD_SELECT = """select * from {tablename} where {where} """
    sqlstr_RECORD_UPDATE = """update {tablename} set {values} where {where}"""
    sqlstr_RECORD_DELETE = """delete from {tablename} where {where} """
    sqlstr_RECORD_INSERT = """insert into {tablename} ({cols}) values ({vals}) """

    class BOX:
        """仅用作传输,不作别的处理"""

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
        return DB_admin.BOX(string, list(value))

    @staticmethod
    def LIKE(colname, value):
        return DB_admin.BOX(colname + " LIKE (?) ", [value])

    @staticmethod
    def EQ(LOGIC="AND", **kwargs):
        string = ""
        values = []
        for k, v in kwargs.items():
            string += f" {k}=? {LOGIC} "
            values.append(v)
        string = re.sub(f"{LOGIC}\s+$", "", string)
        return DB_admin.BOX(string, values)

    @staticmethod
    def LIMIT(count, offset=0):
        value = []
        string = f"LIMIT {count} OFFSET {offset}"
        return DB_admin.BOX(string, value)

    @staticmethod
    def VALUEEQ(**kwargs):
        """确保插入的都是数据库字段, 不然就等着报错吧!"""
        string = ",".join([k + "=? " for k in list(kwargs.keys())])
        # string = f"""({string})"""
        value = list(kwargs.values())
        return DB_admin.BOX(string, value)

    @dataclass
    class linkinfo_fields:
        tablename: "str" = "CARD_LINK_INFO"
        card_id: "str" = "varchar primary key not null unique"
        data: "str" = "text not null"

        def get_dict(self):
            d = self.__dict__.copy()
            d.pop("tablename")
            return d

    @dataclass
    class pdfinfo_fields:
        tablename: "str" = "PDF_INFO_TABLE"
        uuid: "str" = "varchar primary key not null unique"
        pdf_path: "str" = "varchar not null"
        ratio: "float" = "float not null"
        offset: "int" = "integer not null"

        def get_dict(self):
            d = self.__dict__.copy()
            d.pop("tablename")
            return d

    @dataclass
    class clipbox_fields:
        tablename: "str" = "CLIPBOX_INFO_TABLE"
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

        def get_dict(self):
            d = self.__dict__.copy()
            d.pop("tablename")
            return d

    linkinfo_constrain = {
        "string": ["data"],
        "number": ["card_id"]
    }

    clipbox_constrain = {
        "number": ["commentQA", "QA", "x", "y", "w", "h", "ratio", "pagenum"],
        "string": ["uuid", "card_id", "comment", "pdfuuid"]
    }

    pdfinfo_constrain = {
        "string": ["uuid", "pdf_path"],
        "number": ["ratio", "offset"]
    }

    table_swtich = {
        table_clipbox: (clipbox_fields(), clipbox_constrain),
        table_pdfinfo: (pdfinfo_fields(), pdfinfo_constrain),
        table_linkinfo: (linkinfo_fields(), linkinfo_constrain)
    }

    def __init__(self):
        # self.tab_name = Get._().dir_clipboxTable_name
        if __name__ == "__main__":
            from lib.common_tools.src_admin import SrcAdmin
            pass
        else:
            from .src_admin import SrcAdmin
        self.tab_name = None
        self.db_dir = SrcAdmin.start().path.DB_file
        self.connection = None
        self.cursor = None
        self.sqlstr_isbussy = False
        self.excute_queue = []  # 队列结构

    def table_fields_align(self):
        """确保字段对齐,如果不对齐,则要增加字段,字段可以增加,一般不重命名和删除"""
        pragma = self.pragma().return_all()
        table_fields = set([i[1] for i in pragma])
        compare_fields = set(self.table_swtich[self.curr_tabtype][0].get_dict().keys())
        if len(compare_fields) > len(table_fields):
            # print("update table fields")
            need_add_fields = list(compare_fields - table_fields)
            for field in need_add_fields:
                self.alter_add_col(field).commit()

    def pragma(self):
        """返回字段结构"""
        s = self.sqlstr_TABLE_PRAGMA.format(tablename=self.tab_name)
        self.excute_queue.append(s)
        return self

    def alter_add_col(self, colname):
        all_column_names = self.table_swtich[self.curr_tabtype][0].get_dict()
        s = self.sqlstr_TABLE_ALTER.format(tablename=self.tab_name, colname=colname,
                                           define=all_column_names[colname])
        self.excute_queue.append(s)
        return self

    def go(self, curr_tabtype=None):
        """go是DB开始的入口,end是结束的标志,必须要调用end结束"""
        if not curr_tabtype:
            curr_tabtype = self.table_clipbox
        self.excute_queue = []
        self.result_queue = []
        self.connection = sqlite3.connect(self.db_dir)
        self.cursor = self.connection.cursor()
        self.curr_tabtype = curr_tabtype
        self.tab_name = self.table_swtich[curr_tabtype][0].tablename
        self.table_ifEmpty_create().commit()
        self.table_fields_align()
        return self

    def end(self):
        if self.connection is not None:
            self.connection.close()

    def del_card_id(self, condition: "DB_admin.BOX", card_id, callback=None):
        """使用的前提是在table_clipbox表中,目的是删掉对应clipbox已经不支持的卡片"""
        records = self.select(condition).return_all().zip_up().to_clipbox_data()
        # uuidli = [item["uuid"] for item in records]
        for r in records:
            card_idlist: "list[str]" = list(filter(lambda x: x.isdecimal(), r.card_id.split(",")))
            if card_id in card_idlist:
                card_idlist.remove(card_id)
            r.card_id = ",".join(card_idlist)
            self.update(where=self.EQ(uuid=r.uuid), values=self.VALUEEQ(**r.to_dict())).commit(callback=callback)

    def add_card_id(self, condition: "DB_admin.BOX", card_id, callback=None):
        """使用的前提是在table_clipbox表中,目的是增加对应clipbox没有支持的卡片"""
        records = self.select(condition).return_all().zip_up().to_clipbox_data()
        # uuidli = [item["uuid"] for item in records]
        for r in records:
            card_idlist: "list[str]" = list(filter(lambda x: x.isdecimal(), r.card_id.split(",")))
            if card_id not in card_idlist:
                card_idlist.append(card_id)
            r.card_id = ",".join(card_idlist)
            self.update(where=self.EQ(uuid=r.uuid), values=self.VALUEEQ(**r.to_dict())).commit(callback=callback)

    # 存在性检查,如果为空则创建
    def table_ifEmpty_create(self):
        s = self.create_table()
        self.excute_queue.append(s)
        return self

    def create_table(self):
        # make fields
        d = self.table_swtich[self.curr_tabtype][0].get_dict()
        fields = ""
        for k, v in d.items():
            fields += f"\n{k} {v},"
        fields = fields[:-1]
        s = self.sqlstr_TABLE_CREATE.format(tablename=self.tab_name, fields=fields)
        return s

    def exists(self, box: "DB_admin.BOX"):
        result = self.exists_check(box).return_all()
        return result[0][0] > 0

    # 存在性检查
    def exists_check(self, box: "DB_admin.BOX"):

        s = self.sqlstr_RECORD_EXIST.format(tablename=self.tab_name, where=box.string)
        self.excute_queue.append([s, box.values])
        return self

    def valCheck(self, k: "str", v: "str"):
        constrain = self.table_swtich[self.curr_tabtype][1]
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
            all_column_names = self.table_swtich[self.curr_tabtype][0].__dict__
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
        all_column_names = self.table_swtich[self.curr_tabtype][0].get_dict()
        for k, v in values.items():
            if k in all_column_names:
                string += f""" {k}=? ,"""
                val.append(v)
        if string == "":
            raise ValueError("values is empty!")
        return DB_admin.BOX(string, val)

    # 查
    # def select2(self, uuid: "str" = None, card_id: "str" = None, pagenum: "int" = None, pdfuuid: "str" = None,
    #            comment: "str" = None, where=None, limit=None, like=None, **kwargs):
    #     """# 简单的查询, 支持等于,包含,两种搜索条件,
    #     如果你想搜所有的记录,那么就输入 true=True
    #     """
    #
    #     if like is None:
    #         if where is None:
    #             where = self.where_maker(uuid=uuid, card_id=card_id, pagenum=pagenum, pdfuuid=pdfuuid, comment=comment,
    #                                      **kwargs)
    #         s = self.sqlstr_RECORD_SELECT.format(tablename=self.tab_name, where=where)
    #     else:
    #         colname = list(filter(lambda x: x is not None, [pdfuuid, card_id]))[0]
    #         s = self.sqlstr_RECORD_SELECT.format(tablename=self.tab_name, where=f"{colname} like '{like}'")
    #     s += (f"limit {limit}" if limit is not None else "")
    #     self.excute_queue.append(s)
    #     return self

    def select(self, box: "DB_admin.BOX" = None, **kwargs):
        assert box is not None or len(kwargs) > 0
        if box is None and len(kwargs) > 0:
            box = self.EQ(**kwargs)
        s = self.sqlstr_RECORD_SELECT.format(tablename=self.tab_name, where=box.string)
        self.excute_queue.append([s, box.values])

        return self

    # 改
    # def update2(self, values=None, where=None):
    #     assert values is not None and where is not None
    #     """values 和 where 可以用 valuemaker和wheremaker设计， 也可以自己设计"""
    #     s = self.sqlstr_RECORD_UPDATE.format(tablename=self.tab_name, values=values, where=where)
    #     self.excute_queue.append(s)
    #     return self

    def update(self, values: "DB_admin.BOX" = None, where: "DB_admin.BOX" = None):
        """values,where 应该是一个字典, k是字段名,v是字段值"""
        assert values is not None and where is not None
        entity = values.values + where.values

        s = self.sqlstr_RECORD_UPDATE.format(tablename=self.tab_name, values=values.string, where=where.string)
        self.excute_queue.append([s, entity])
        return self

    # 增
    def insert(self, **values):
        """insert 很简单, 不必走 box"""
        cols = ""
        vals = ""
        all_column_names = self.table_swtich[self.curr_tabtype][0].get_dict()
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

    # def insert(self,values:"DB_admin.BOX"):
    #
    #     s = self.sqlstr_RECORD_INSERT.format(tablename=self.tab_name, cols=cols[0:-1], vals=placeholder[0:-1])
    #     self.excute_queue.append([s,vals])
    #     return self
    # 删
    # def delete2(self, uuid: "str" = None, card_id: "str" = None, pagenum: "int" = None, pdfuuid: "str" = None,
    #            text_: "str" = None):
    #     where = self.where_maker(uuid=uuid, card_id=card_id, pagenum=pagenum, pdfuuid=pdfuuid, text_=text_)
    #     s = self.sqlstr_RECORD_DELETE.format(tablename=self.tab_name, where=where)
    #     self.excute_queue.append(s)
    #     return self

    def delete(self, where: "DB_admin.BOX"):
        s = self.sqlstr_RECORD_DELETE.format(tablename=self.tab_name, where=where.string)
        self.excute_queue.append([s, where.values])
        return self

    # def return_all2(self, callback=None):
    #     s = self.excute_queue.pop(0)
    #     # print(s)
    #     if s != "":
    #         if callback:
    #             callback(s)
    #         result = self.cursor.execute(s).fetchall()
    #         all_column_names = self.table_swtich[self.curr_tabtype][0].get_dict()
    #         return DBResults(result, all_column_names, self.curr_tabtype)

    def return_all(self, callback=None):
        s = self.excute_queue.pop(0)
        # print(s)
        if s != "":
            if callback:
                callback(s)
            if type(s) == list:
                result = self.cursor.execute(s[0], s[1]).fetchall()
            else:
                result = self.cursor.execute(s).fetchall()
            all_column_names = self.table_swtich[self.curr_tabtype][0].get_dict()
            return DBResults(result, all_column_names, self.curr_tabtype)

    # def commit2(self, callback=None):
    #     s = self.excute_queue.pop(0)
    #     if s != "":
    #         if callback:
    #             callback(s)
    #         result = self.cursor.execute(s)
    #
    #         self.connection.commit()
    #         return result

    def commit(self, callback=None):
        s = self.excute_queue.pop(0)
        if s:
            if callback:
                callback(s)
            if type(s) == list:
                result = self.cursor.execute(s[0], s[1])
            else:
                result = self.cursor.execute(s)
            self.connection.commit()
            return result


class DBResults(object):
    """这个对象只读不写,是DB返回结果的容器的简单包装"""

    def __init__(self, results, all_column_names, curr_tabletype=0):
        self.results: "list" = results
        self.all_column_names = all_column_names
        self.curr_tabletype = curr_tabletype

    def zip_up(self, version=1):
        """zip只包装成字典, 如果要用dataclass ,请返回后自己包装"""
        new_results = self.DBdataLi()

        for result in self.results:
            record = self.DBdata()
            step1 = list(zip(self.all_column_names.keys(), result))
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

    class DBdata(dict):

        def to_clipbox_data(self):
            return ClipboxRecord(**self)

        def to_pdfinfo_data(self):
            return PDFinfoRecord(**self)

        def to_givenformat_data(self, format):
            return format(self)

    class DBdataLi(list):
        """给数组附加一些功能"""

        def to_pdfinfo_data(self):
            li = [PDFinfoRecord(**i) for i in self]
            return li

        def to_clipbox_data(self):
            li = [ClipboxRecord(**i) for i in self]
            return li


@dataclass
class Pair:
    card_id: "str" = None
    desc: "str" = None


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
    DB = DB_admin()
    DB.go(DB.table_linkinfo)
    DB.delete(DB.EQ(card_id=card_id)).commit(print)
    DB.insert(**record).commit(print)
    x = DB.go(DB.table_linkinfo).select(DB.EQ(card_id=card_id)).return_all(print).zip_up()
    print(x)
    # DB.delete(DB.EQ(card_id=card_id)).commit(print)
    DB.update(values=DB.VALUEEQ(data=record2["data"]), where=DB.EQ(card_id=card_id)).commit(print)
    x = DB.select(DB.EQ(card_id=card_id)).return_all().zip_up()
    print(x)

    # x=DB.go(DB.table_clipbox).select2(
    #      (DB.EQ(pdfuuid="fbe0cb0e-8eba-39e9-8cc7-a6eb7c18763c")
    #     &DB.LIKE("card_id","%16274%")
    #     &~DB.IN("pagenum",1,0))+DB.LIMIT(2)).return_all2(print).zip_up()
    # print(len(x))
    pass
