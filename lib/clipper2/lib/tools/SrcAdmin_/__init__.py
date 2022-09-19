from dataclasses import dataclass, asdict
import logging
import os, json
import re
import sqlite3, uuid
import queue
from collections import namedtuple
from typing import Union

from PyQt5.QtGui import QIcon
from aqt.utils import showInfo, aqt_data_folder

print = showInfo


class Get:
    instance = None
    dir_SrcAdmin_ = os.path.abspath(os.path.dirname(__file__))
    dir_tools = os.path.split(dir_SrcAdmin_)[0]
    dir_lib = os.path.split(dir_tools)[0]
    dir_clipper = os.path.split(dir_lib)[0]
    dir_lib0 = os.path.split(dir_clipper)[0]
    dir_root = os.path.split(dir_lib0)[0]
    dir_user_files = "user_files"
    dir_resource = "resource"
    dir_tempfile = "tempfile"
    dir_bookmark = ""
    dir_img = ""
    dir_json = ""
    dir_DB = "linkInfo.db"
    dir_clipboxTable_name = "CLIPBOX_INFO_TABLE"

    def json_dict(cls, path="config.json"):  # type: (str)->dict
        fullpath = os.path.join(cls.dir_clipper, cls.dir_resource, cls.dir_json, path)
        obj_dict = json.loads(open(fullpath, "r", encoding="utf-8").read())
        return obj_dict

    def config_dict(cls, configname="clipper"):
        if configname == 'clipper':
            fullpath = cls.json_dir("clipper")
            showInfo(fullpath)
            if not os.path.exists(fullpath):
                default_path = cls.json_dir("clipper.template")
                showInfo(default_path)
                template_dict = json.load(open(default_path, "r", encoding="utf-8"))
                # default_dict_str = open(default_path, "r", encoding="utf-8").read()
                # cls.save_dict(fullpath, default_dict_str)
                json.dump(template_dict, open(fullpath,"w", encoding="utf-8"), ensure_ascii=False, sort_keys=True, indent=4)
            config = json.loads(open(fullpath, "r", encoding="utf-8").read())
            return config
        elif configname == "clipper.template":
            fullpath = cls.json_dir(configname)
            config = json.loads(open(fullpath, "r", encoding="utf-8").read())
            return config
        else:
            raise ValueError("没有对应的文件！")

    def save_dict(self, olddict_path, newdict_str):
        f = open(olddict_path, "w", encoding="utf-8")
        f.write(newdict_str)
        f.close()

    def json_dir(cls, jsonname):
        if jsonname == "clipper":
            return os.path.join(cls.dir_root, cls.dir_user_files, "clipper.config.json")
        if jsonname == "clipper.template":
            return os.path.join(cls.dir_clipper, cls.dir_resource, cls.dir_json, "config.template.json")
        if jsonname == "pdf_info":
            return os.path.join(cls.dir_root, cls.dir_user_files, "pdf_info.json")

    def img_dir(cls, path):
        result = os.path.join(cls.dir_clipper, cls.dir_resource, cls.dir_img, path)
        if os.path.exists(result):
            return result
        else:
            raise ValueError(f"path={path} don't exist")

    def DB_dir(self, DBname=""):
        if DBname == "":
            DBname = self.dir_DB
        return os.path.join(self.dir_root, self.dir_user_files, DBname)

    def temp_dir(self):
        return os.path.join(self.dir_root, self.dir_user_files, self.dir_tempfile)

    def user_files_dir(self):
        return os.path.join(self.dir_root, self.dir_user_files)

    @classmethod
    def _(cls):
        if cls.instance is None:
            cls.instance = cls()
        return cls.instance


class JSONDir:
    """返回地址罢了, 不必关心是否存在"""
    def __init__(self):
        d = {}
        self.clipper = Get._().json_dir("clipper")
        self.clipper_template = Get._().json_dir("clipper.template")
        self.pdf_info = Get._().json_dir("pdf_info")
        # if not os.path.exists(self.clipper):
        #     json.dump(d, open(self.clipper, "w", encoding="utf-8"), ensure_ascii=False, sort_keys=True, indent=4)
        # if not os.path.exists(self.pdf_info):
        #     json.dump(d, open(self.pdf_info, "w", encoding="utf-8"), ensure_ascii=False, sort_keys=True, indent=4)


class IMGDir:
    def __init__(self):
        self.cancel = Get._().img_dir("icon_cancel.png")
        self.item_open = Get._().img_dir("icon_fileopen.png")
        self.item_plus = Get._().img_dir("icon_addToView.png")
        self.answer = Get._().img_dir("icon_answer.png")
        self.question = Get._().img_dir("icon_question.png")
        self.refresh = Get._().img_dir("icon_refresh.png")
        self.reset = Get._().img_dir("icon_reset.png")
        self.clipper = Get._().img_dir("icon_window_clipper.png")
        self.prev = Get._().img_dir("icon_prev_button.png")
        self.next = Get._().img_dir("icon_next_button.png")
        self.bag = Get._().img_dir("icon_page_pick.png")
        self.expand = Get._().img_dir("icon_fullscreen.png")
        self.config = Get._().img_dir("icon_configuration.png")
        self.config_reset = Get._().img_dir("icon_config_reset.png")
        self.close = Get._().img_dir("icon_close_button.png")
        self.correct = Get._().img_dir("icon_correct.png")
        self.bookmark = Get._().img_dir("icon_book_mark.png")
        self.zoomin = Get._().img_dir("icon_zoom_in.png")
        self.zoomout = Get._().img_dir("icon_zoom_out.png")
        self.download = Get._().img_dir("icon_download.png")
        self.goback = Get._().img_dir("icon_return.png")
        self.stop = Get._().img_dir("icon_stop.png")
        self.clear = Get._().img_dir("icon_clear.png")
        self.singlepage = Get._().img_dir("icon_SinglePage.png")
        self.doublepage = Get._().img_dir("icon_DoublePage.png")
        self.fit_in_width = Get._().img_dir("icon_fitin_width.png")
        self.fit_in_height = Get._().img_dir("icon_fitin_height.png")
        self.mouse_mid_button = Get._().img_dir("icon_fitin_width.png")
        self.mouse_wheel_zoom = Get._().img_dir("icon_mouse_wheel_zoom.png")
        self.read = Get._().img_dir("icon_read.png")
        self.link = Get._().img_dir("icon_link.png")
        self.link2 = Get._().img_dir("icon_link2.png")
        self.left_direction = Get._().img_dir("icon_direction_left.png")
        self.right_direction = Get._().img_dir("icon_direction_right.png")
        self.top_direction = Get._().img_dir("icon_direction_top.png")
        self.bottom_direction = Get._().img_dir("icon_direction_bottom.png")
        self.ID_card = Get._().img_dir("icon_ID_card.png")


class DB(object):
    # dict_TABLE_Field={
    #     "uuid":"varchar(8) primary key not null unique",
    #     "x":"float not null",
    #     "y":"float not null",
    #     "w":""
    # }
    # all_fields=[#用来确保字段对齐
    #     "x","y","w","h","QA","text_","textQA","card_id","pagenum","ratio","pdfname","pageshift"
    # ]
    table_clipbox = 0
    table_pdfinfo = 1
    table_linkinfo = 2

    sqlstr_TABLE_CREATE = """create table if not exists {tablename} ({fields})"""

    sqlstr_TABLE_PRAGMA = """PRAGMA table_info({tablename})"""
    sqlstr_TABLE_ALTER = """alter table {tablename} add column {colname} {define}"""
    sqlstr_TABLE_EXIST = """select count(*) from sqlite_master where type="table" and name ="{tablename}" """
    sqlstr_RECORD_EXIST = """select count(*) from {tablename} where {key}={value} """
    sqlstr_RECORD_SELECT = """select * from {tablename} where {where} """
    sqlstr_RECORD_UPDATE = """update {tablename} set {values} where {where}"""
    sqlstr_RECORD_DELETE = """delete from {tablename} where {where} """
    sqlstr_RECORD_INSERT = """insert into {tablename} ({cols}) values ({vals}) """

    @dataclass
    class linkinfo_fields:
        tablename: "str" = "CARD_LINK_INFO"
        data: "str" = "text not null"

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
        "string": ["card_id", "data"]
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
        self.tab_name = None
        self.db_dir = Get._().DB_dir()
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

    def del_card_id(self, condition, card_id, callback=None):
        records = self.select(where=condition).return_all().zip_up()
        uuidli = [item["uuid"] for item in records]
        for r in records:
            card_idlist: "list[str]" = list(filter(lambda x: x.isdecimal(), r["card_id"].split(",")))
            if card_id in card_idlist:
                card_idlist.remove(card_id)
            r["card_id"] = ",".join(card_idlist)
            self.update(where=self.where_maker(uuid=r["uuid"]), values=self.value_maker(**r)).commit(callback=callback)

    def add_card_id(self, condition, card_id, callback=None):
        records = self.select(where=condition).return_all().zip_up()
        uuidli = [item["uuid"] for item in records]
        for r in records:
            card_idlist: "list[str]" = list(filter(lambda x: x.isdecimal(), r["card_id"].split(",")))
            if card_id not in card_idlist:
                card_idlist.append(card_id)
            r["card_id"] = ",".join(card_idlist)
            self.update(where=self.where_maker(uuid=r["uuid"]), values=self.value_maker(**r)).commit(callback=callback)

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

    def exists(self, uuid):
        result = self.exists_check(uuid).return_all()
        # print("exists {}".format(result))
        return result[0][0] > 0

    # 存在性检查
    def exists_check(self, uuid):

        s = self.sqlstr_RECORD_EXIST.format(tablename=self.tab_name, key="uuid", value=f""" "{uuid}" """)
        self.excute_queue.append(s)
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
        value = ""
        all_column_names = self.table_swtich[self.curr_tabtype][0].get_dict()
        for k, v in values.items():
            if k in all_column_names:
                value += f""" {k}={self.valCheck(k, v)} ,"""
        if value == "":
            raise ValueError("values is empty!")
        return value[0:-1]

    # 查
    def select(self, uuid: "str" = None, card_id: "str" = None, pagenum: "int" = None, pdfuuid: "str" = None,
               comment: "str" = None, where=None, limit=None, like=None, **kwargs):
        """# 简单的查询, 支持等于,包含,两种搜索条件,
        如果你想搜所有的记录,那么就输入 true=True
        """

        if like is None:
            if where is None:
                where = self.where_maker(uuid=uuid, card_id=card_id, pagenum=pagenum, pdfuuid=pdfuuid, comment=comment,
                                         **kwargs)
            s = self.sqlstr_RECORD_SELECT.format(tablename=self.tab_name, where=where)
        else:
            colname = list(filter(lambda x: x is not None, [pdfuuid, card_id]))[0]
            s = self.sqlstr_RECORD_SELECT.format(tablename=self.tab_name, where=f"{colname} like '{like}'")
        s += (f"limit {limit}" if limit is not None else "")
        self.excute_queue.append(s)
        return self

    # def select_like(self,colname,pattern,limit=None):
    #     """查找包含条件的记录."""
    #     result = self.select(where=f"{colname} like {pattern}",limit=limit).return_all()
    #     return result

    # 改
    def update(self, values=None, where=None):
        assert values is not None and where is not None
        """values 和 where 可以用 valuemaker和wheremaker设计， 也可以自己设计"""
        s = self.sqlstr_RECORD_UPDATE.format(tablename=self.tab_name, values=values, where=where)
        self.excute_queue.append(s)
        return self

    # 增
    def insert(self, **values):
        cols = ""
        vals = ""
        all_column_names = self.table_swtich[self.curr_tabtype][0].get_dict()

        for k, v in values.items():
            if k not in all_column_names:
                continue
            cols += k + ","
            vals += f"{self.valCheck(k, v)},"  # 最后一个逗号要去掉
        s = self.sqlstr_RECORD_INSERT.format(tablename=self.tab_name, cols=cols[0:-1], vals=vals[0:-1])
        self.excute_queue.append(s)
        return self

    # 删
    def delete(self, uuid: "str" = None, card_id: "str" = None, pagenum: "int" = None, pdfuuid: "str" = None,
               text_: "str" = None):
        where = self.where_maker(uuid=uuid, card_id=card_id, pagenum=pagenum, pdfuuid=pdfuuid, text_=text_)
        s = self.sqlstr_RECORD_DELETE.format(tablename=self.tab_name, where=where)
        self.excute_queue.append(s)
        return self

    def return_all(self, callback=None):
        s = self.excute_queue.pop(0)
        # print(s)
        if s != "":
            if callback:
                callback(s)
            result = self.cursor.execute(s).fetchall()
            all_column_names = self.table_swtich[self.curr_tabtype][0].get_dict()
            return DBResults(result, all_column_names, self.curr_tabtype)

    def commit(self, callback=None):
        s = self.excute_queue.pop(0)
        if s != "":
            if callback:
                callback(s)
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
            from .. import objs
            return objs.ClipboxRecord(**self)

        def to_pdfinfo_data(self):
            from .. import objs
            return objs.PDFinfoRecord(**self)

        def to_givenformat_data(self, format):
            return format(self)

    class DBdataLi(list):
        """给数组附加一些功能"""

        def to_pdfinfo_data(self):
            from .. import objs
            li = [objs.PDFinfoRecord(**i) for i in self]
            return li

        def to_clipbox_data(self):
            from .. import objs
            li = [objs.ClipboxRecord(**i) for i in self]
            return li


class PDFJSON(object):
    from .. import objs
    def __init__(self):
        self.data = {}

    def load(self):
        self.pdf_json_dir = JSONDir().pdf_info
        self.data = json.load(open(self.pdf_json_dir, "r", encoding="utf-8"))
        return self

    def save(self):
        json.dump(self.data, open(self.pdf_json_dir, "w", encoding="utf-8"),
                  ensure_ascii=False, sort_keys=True, indent=4)
        return self

    def exists(self, pdfuuid=None, pdfname=None):
        if pdfname is not None:
            pdfuuid = self.to_uuid(pdfname)
        return pdfuuid in self.data

    def to_uuid(self, pdfname):
        return str(uuid.uuid3(uuid.NAMESPACE_URL, pdfname))

    def read(self, uuid=None, pdfname=None):
        """根据uuid查找PDF名字, 也可以传入pdfname转化为uuid"""
        if pdfname is not None:
            uuid = self.to_uuid(pdfname)
        if uuid in self.data:
            return self.data[uuid]
        else:
            raise TypeError(f"uuid={uuid},not found")

    def mount(self, uuid=None, pdfname=None, **kwargs):
        if pdfname is not None:
            uuid = self.to_uuid(pdfname)
        if uuid not in self.data:
            self.data[uuid] = {
                "pdf_path": pdfname
            }
        for key, val in kwargs.items():
            self.data[uuid][key] = val
        return self

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __contains__(self, item):
        return item in self.data


# funcs=importfuncs()
# print,printer=importprint()
if __name__ == "__main__":
    print(Get._().img_dir(""))
