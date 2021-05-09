import os
import sqlite3, json

from .utils import BaseInfo, USER_FOLDER, Pair

DB_DIR = os.path.join(USER_FOLDER, BaseInfo().baseinfo["linkInfoDBFileName"])
TABLE_NAME = BaseInfo().baseinfo["linkInfoDBTableName"]

"""
根据linkData_reader的注释设计json的格式。
"""
class LinkDataDBmanager(object):
    def __init__(self, DB_dir=DB_DIR, tab_name=TABLE_NAME):
        self.tab_name = tab_name
        self.db_dir = DB_dir
        self.connection = sqlite3.connect(DB_dir)
        self.cursor = self.connection.cursor()
        self.init_table()

    def init_table(self):
        #fetchall()[0][0] 是第一个数据的第一个字段的内容
        table_not_exist = self.cursor.execute(self.str_table_check_exist(self.tab_name)).fetchall()[0][0] == 0
        if table_not_exist:
            self.cursor.execute(self.str_CARD_LINK_INFO_table_init())
            self.connection.commit()

    def str_CARD_LINK_INFO_table_init(self, tablename=""):
        if tablename == "":
            tablename = self.tab_name
        sql_string = """
        CREATE TABLE {tablename}
        (card_id INTEGER PRIMARY KEY not null,
        data TEXT)
        """.format(tablename=tablename)
        return sql_string

    def str_table_check_exist(self, tablename):
        sql_string = """
        select count(*) from sqlite_master where type="table" and name ="{tablename}"
        """.format(tablename=tablename)
        return sql_string

    def jsonstr_dict_convert(self, dict_or_list):
        """把dict或list通过json转换成string"""
        return json.dumps(dict_or_list)

    def data_fetch(self, card_id):
        results = self.cursor.execute(self.str_data_table_fetch(card_id)).fetchall()
        return results

    def str_data_table_fetch(self, card_id, tablename=""):
        if tablename == "":
            tablename = self.tab_name
        sql_string = f"""SELECT * FROM {tablename} where card_id={card_id}"""
        return sql_string

    def data_update(self, card_id,data):
        """更新指定卡片ID的某个字段,字段的全部内容更新, 因此需要在外部的JSON中完成,再传回来
            update包括了链接的建立与删除,一切改动都经过update
        """
        record_not_exists = self.cursor.execute(self.str_data_table_fetch(card_id)).fetchall() == []
        if record_not_exists:
            self.cursor.execute(self.str_data_table_insert(card_id,data))
        else:
            self.cursor.execute(self.str_data_table_update(card_id,data))
        self.connection.commit()
        pass

    def str_data_table_update(self, card_id,data,tablename=""):
        """

        Parameters
        ----------
        tablename :

        Returns
        -------

        """
        if tablename == "":
            tablename = self.tab_name
        card_id = card_id
        data =self.JSON_to_string(data)
        sql_string = """update {tablename} set data='{data}' where card_id={card_id}""".format(
            tablename=tablename,data=data,card_id=card_id
        )
        return sql_string

    def JSON_to_string(self,data):
        s = json.dumps(data)
        return s.replace("'","''")

    def data_remove(self, card_id):
        """直接删除指定的卡片ID"""
        self.cursor.execute(self.str_data_table_delete(card_id))
        self.connection.commit()
        pass

    def str_data_table_delete(self, card_id, tablename=""):
        if tablename == "":
            tablename = self.tab_name
        sql_string = f"""DELETE FROM {tablename} where card_id={card_id}"""
        return sql_string

    def str_data_table_insert(self, card_id,data,tablename=""):
        if tablename == "":
            tablename = self.tab_name
        card_id = card_id
        data =self.JSON_to_string(data)
        sql_string = f"""insert into {tablename} (card_id,data) values({card_id},'{data}')"""

        return sql_string
