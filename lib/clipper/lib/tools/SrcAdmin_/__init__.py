import os, json
import sqlite3

from PyQt5.QtGui import QIcon
from aqt.utils import showInfo, aqt_data_folder



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
        self.clipper = Get._().json_dir("clipper")
        self.clipper_template = Get._().json_dir("clipper.template")

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


class DB(object):
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
    sqlstr_TABLE_EXIST = """select count(*) from sqlite_master where type="table" and name ="{tablename}" """
    sqlstr_RECORD_EXIST = """select count(*) from {tablename} where {key}={value} """
    sqlstr_RECORD_SELECT = """select * from {tablename} where {where} """
    sqlstr_RECORD_UPDATE = """update {tablename} set {values} where {where}"""
    sqlstr_RECORD_DELETE = """delete from {tablename} where {where} """
    sqlstr_RECORD_INSERT = """insert into {tablename} ({cols}) values ({vals}) """

    table_column_names = ["uuid", "x", "y", "w", "h", "QA", "text_", "textQA", "card_id", "ratio", "pagenum", "pdfname"]
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

    def go(self):
        self.excute_queue = []
        self.connection = sqlite3.connect(self.db_dir)
        self.cursor = self.connection.cursor()
        self.table_ifEmpty_create().commit()
        return self

    def end(self):
        self.connection.close()

    # 存在性检查
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
            # return f""" "{v.replace("'", "''")}"  """
            return f""" "{v}"  """
        else:
            return v

    def where_maker(self, **values):
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
               text_: "str" = None):
        where = self.where_maker(uuid=uuid, card_id=card_id, pagenum=pagenum, pdfname=pdfname, text_=text_)
        s = self.sqlstr_RECORD_SELECT.format(tablename=self.tab_name, where=where)
        self.excute_queue.append(s)
        return self

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
            vals += f"{self.valCheck(k, v)},"
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
        if s != "":
            result = self.cursor.execute(s).fetchall()
            return result

    def commit(self):
        s = self.excute_queue.pop(0)
        if s != "":
            result = self.cursor.execute(s)
            self.connection.commit()
            return result


if __name__ == "__main__":
    print(Get._().img_dir(""))
