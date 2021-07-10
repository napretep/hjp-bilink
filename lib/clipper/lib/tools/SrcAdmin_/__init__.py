import os, json
import sqlite3
import queue
from PyQt5.QtGui import QIcon
from aqt.utils import showInfo, aqt_data_folder


# def importer():
#     from . import funcs,objs,events
#     return funcs,objs,events
#
# def importprint():
#     from ..funcs import logger
#     return logger(__name__)


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

    def config_dict(cls, configname):
        if configname == 'clipper':
            path = "clipper.config.json"
            fullpath = cls.json_dir("clipper")
            # print(fullpath)
            if not os.path.exists(fullpath):
                print(f"{fullpath}不存在,重建中")
                default_path = cls.json_dir("clipper.template")
                default_dict_str = open(default_path, "r", encoding="utf-8").read()
                cls.save_dict(fullpath, default_dict_str)
            config = json.loads(open(fullpath, "r", encoding="utf-8").read())
            # print(config)
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
        return (os.path.join(cls.dir_clipper, cls.dir_resource, cls.dir_img, path))

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
    def __init__(self):
        d = {}
        self.clipper = Get._().json_dir("clipper")
        self.clipper_template = Get._().json_dir("clipper.template")
        self.pdf_info = Get._().json_dir("pdf_info")
        if not os.path.exists(self.clipper):
            json.dump(d, open(self.clipper, "w", encoding="utf-8"))
        if not os.path.exists(self.pdf_info):
            json.dump(d, open(self.pdf_info, "w", encoding="utf-8"), ensure_ascii=False, sort_keys=True, indent=4)

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
    sqlstr_TABLE_CREATE = """create table if not exists {tablename}(
uuid varchar(8) primary key not null unique,
x float not null,
y float not null,
w float not null,
h float not null,
QA integer not null,
text_ text ,
textQA integer not null,
card_id varchar not null,
ratio float not null,
pagenum integer not null,
pdfname varchar not null
)"""
    sqlstr_TABLE_PRAGMA = """PRAGMA table_info({tablename})"""
    sqlstr_TABLE_ALTER = """alter table {tablename} add column {colname} {define}"""
    sqlstr_TABLE_EXIST = """select count(*) from sqlite_master where type="table" and name ="{tablename}" """
    sqlstr_RECORD_EXIST = """select count(*) from {tablename} where {key}={value} """
    sqlstr_RECORD_SELECT = """select * from {tablename} where {where} """
    sqlstr_RECORD_UPDATE = """update {tablename} set {values} where {where}"""
    sqlstr_RECORD_DELETE = """delete from {tablename} where {where} """
    sqlstr_RECORD_INSERT = """insert into {tablename} ({cols}) values ({vals}) """

    table_all_column_names = {
        "uuid": "varchar(8) primary key not null unique,",
        "x": "float not null",
        "y": "float not null",
        "w": "float not null",
        "h": "float not null",
        "QA": "integer not null",
        "text_": "text",
        "textQA": "integer not null",
        "card_id": "varchar not null",
        "ratio": "float not null",
        "pagenum": "integer not null",
        "pdfname": "varchar not null",
    }
    constrain = {
        "number": ["textQA", "QA", "x", "y", "w", "h", "ratio", "pagenum"],
        "string": ["uuid", "card_id", "text_", "pdfname"]
    }

    def __init__(self):
        self.tab_name = Get._().dir_clipboxTable_name
        self.db_dir = Get._().DB_dir()
        self.connection = None
        self.cursor = None
        self.sqlstr_isbussy = False
        self.excute_queue = []  # 队列结构

    def table_fields_align(self):
        """确保字段对齐,如果不对齐,则要增加字段,字段可以增加,一般不重命名和删除"""
        pragma = self.pragma().return_all()
        table_fields = set([i[1] for i in pragma])
        compare_fields = set(self.table_all_column_names.keys())
        if len(compare_fields) > len(table_fields):
            print("update table fields")
            need_add_fields = list(compare_fields - table_fields)
            for field in need_add_fields:
                self.alter_add_col(field).commit()
            # print(add_fields)
            print("fields added")

    def pragma(self):
        s = self.sqlstr_TABLE_PRAGMA.format(tablename=self.tab_name)
        self.excute_queue.append(s)
        return self

    def alter_add_col(self, colname):
        s = self.sqlstr_TABLE_ALTER.format(tablename=self.tab_name, colname=colname,
                                           define=self.table_all_column_names[colname])
        self.excute_queue.append(s)
        return self

    def go(self):
        """go是DB开始的入口,end是结束的标志,必须要调用end结束"""
        self.excute_queue = []
        self.result_queue = []
        self.connection = sqlite3.connect(self.db_dir)
        self.cursor = self.connection.cursor()
        self.table_ifEmpty_create().commit()
        self.table_fields_align()
        return self

    def end(self):
        self.connection.close()

    # 存在性检查,如果为空则创建
    def table_ifEmpty_create(self, tablename=""):
        if tablename == "":
            tablename = self.tab_name
        s = self.sqlstr_TABLE_CREATE.format(tablename=tablename)
        self.excute_queue.append(s)
        return self

    def exists(self, uuid):
        result = self.exists_check(uuid).return_all()
        print("exists {}".format(result))
        return result[0][0] > 0

    # 存在性检查
    def exists_check(self, uuid):
        s = self.sqlstr_RECORD_EXIST.format(tablename=self.tab_name, key="uuid", value=f""" "{uuid}" """)
        self.excute_queue.append(s)
        return self

    def valCheck(self, k: "str", v: "str"):
        if k in self.constrain["string"]:
            return f""" "{v}"  """
        else:
            return v

    def where_maker(self, **values):
        print(values)
        where = ""
        for k, v in values.items():
            if v is not None:
                where += f""" {k}={self.valCheck(k, v)} """
        if where == "":
            raise ValueError("where is empty!")
        return where

    def value_maker(self, **values):
        value = ""
        for k, v in values.items():
            value += f""" {k}={self.valCheck(k, v)} ,"""
        if value == "":
            raise ValueError("values is empty!")
        return value[0:-1]

    # 查
    def select(self, uuid: "str" = None, card_id: "str" = None, pagenum: "int" = None, pdfname: "str" = None,
               text_: "str" = None, where=None, limit=None, like=None, **kwargs):
        """# 简单的查询, 支持等于,包含,两种搜索条件,
        如果你想搜所有的记录,那么就输入 true=True
        """

        if like is None:
            if where is None:
                where = self.where_maker(uuid=uuid, card_id=card_id, pagenum=pagenum, pdfname=pdfname, text_=text_,
                                         **kwargs)
            s = self.sqlstr_RECORD_SELECT.format(tablename=self.tab_name, where=where)
        else:
            colname = list(filter(lambda x: x is not None, [pdfname, card_id]))[0]
            s = self.sqlstr_RECORD_SELECT.format(tablename=self.tab_name, where=f"{colname} like '{like}'")
        s += (f"limit {limit}" if limit is not None else "")
        self.excute_queue.append(s)
        return self

    # def select_like(self,colname,pattern,limit=None):
    #     """查找包含条件的记录."""
    #     result = self.select(where=f"{colname} like {pattern}",limit=limit).return_all()
    #     return result

    # 改
    def update(self, values, where):
        """values 和 where 可以用 valuemaker和wheremaker设计， 也可以自己设计"""
        s = self.sqlstr_RECORD_UPDATE.format(tablename=self.tab_name, values=values, where=where)
        self.excute_queue.append(s)
        return self

    # 增
    def insert(self, **values):
        cols = ""
        vals = ""
        for k, v in values.items():
            cols += k + ","
            vals += f"{self.valCheck(k, v)},"  # 最后一个逗号要去掉
        s = self.sqlstr_RECORD_INSERT.format(tablename=self.tab_name, cols=cols[0:-1], vals=vals[0:-1])
        self.excute_queue.append(s)
        return self

    # 删
    def delete(self, uuid: "str" = None, card_id: "str" = None, pagenum: "int" = None, pdfname: "str" = None,
               text_: "str" = None):
        where = self.where_maker(uuid=uuid, card_id=card_id, pagenum=pagenum, pdfname=pdfname, text_=text_)
        s = self.sqlstr_RECORD_DELETE.format(tablename=self.tab_name, where=where)
        self.excute_queue.append(s)
        return self

    def return_all(self):
        s = self.excute_queue.pop(0)
        print(s)
        if s != "":
            result = self.cursor.execute(s).fetchall()
            return DBResults(result, self.table_all_column_names)

    def commit(self):
        s = self.excute_queue.pop(0)
        if s != "":
            result = self.cursor.execute(s)
            self.connection.commit()
            return result


class DBResults(object):
    """这个对象只读不写,是DB返回结果的容器的简单包装"""

    def __init__(self, results, table_all_column_names):
        self.results: "list" = results
        self.table_all_column_names = table_all_column_names

    def zip_up(self):
        new_results = []
        for result in self.results:
            record = {}
            step1 = list(zip(self.table_all_column_names.keys(), result))
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


# funcs=importfuncs()
# print,printer=importprint()
if __name__ == "__main__":
    print(Get._().img_dir(""))
