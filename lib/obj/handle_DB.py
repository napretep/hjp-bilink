

import os
import sqlite3, json

from .cardInfo_obj import CardLinkInfo
from .utils import BaseInfo, USER_FOLDER, Pair

DB_DIR = os.path.join(USER_FOLDER, BaseInfo().baseinfo["linkInfoDBFileName"])
TABLE_NAME = BaseInfo().baseinfo["linkInfoDBTableName"]


class LinkInfoDBmanager(object):
    def __init__(self, DB_dir=DB_DIR, tab_name=TABLE_NAME):
        self.tab_name = tab_name
        self.db_dir = DB_dir
        self.connection = sqlite3.connect(DB_dir)
        self.cursor = self.connection.cursor()
        self.init_table()

    def init_table(self):
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
        info TEXT)
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

    def cardinfo_get(self, pair: Pair):
        results = self.cursor.execute(self.str_data_table_fetch(pair.int_card_id)).fetchall()
        if results != []:
            result = results[0]
            obj = CardLinkInfo(result[0], jsondata=json.loads(result[1]))
        else:
            obj = CardLinkInfo(pair.card_id)
        return obj

    def str_data_table_fetch(self, card_id, tablename=""):
        if tablename == "":
            tablename = self.tab_name
        sql_string = """SELECT * FROM {tablename} where card_id={card_id}"""
        return sql_string

    def cardinfo_update(self, dict_cardinfo: CardLinkInfo):
        """更新指定卡片ID的某个字段,字段的全部内容更新, 因此需要在外部的JSON中完成,再传回来
            update包括了链接的建立与删除,一切改动都经过update
        """
        record_not_exists = self.cursor.execute(self.str_data_table_fetch(dict_cardinfo.card_id)).fetchall() == []
        if record_not_exists:
            self.cursor.execute(self.str_data_table_insert(dict_cardinfo))
        else:
            self.cursor.execute(self.str_data_table_update(dict_cardinfo))
        self.connection.commit()
        pass

    def str_data_table_update(self, dict_cardinfo: CardLinkInfo, tablename=""):
        """

        Parameters
        ----------
        dict_cardinfo :{"card_id":"","link_info":{"link_list":[],"link_tree":[],"group_info":{}}}
        tablename :

        Returns
        -------

        """
        if tablename == "":
            tablename = self.tab_name
        card_id = dict_cardinfo.card_id
        info = dict_cardinfo.info_toDBstring()
        sql_string = f"""update {tablename} set info='{info}' where card_id={card_id}"""
        return sql_string

    def cardinfo_remove(self, card_id):
        """直接删除指定的卡片ID"""
        self.cursor.execute(self.str_data_table_delete(card_id))
        self.connection.commit()
        pass

    def str_data_table_delete(self, card_id, tablename=""):
        if tablename == "":
            tablename = self.tab_name
        sql_string = f"""DELETE FROM {tablename} where card_id={card_id}"""
        return sql_string

    def str_data_table_insert(self, dict_cardinfo: CardLinkInfo, tablename=""):
        if tablename == "":
            tablename = self.tab_name
        info = dict_cardinfo.info_toDBstring()
        card_id = dict_cardinfo.card_id
        sql_string = f"""insert into {tablename} (card_id,info) values({card_id},'{info}')"""

        return sql_string
