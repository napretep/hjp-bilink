# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = '$NAME.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2021/7/29 16:20'
请直接使用相关函数,最好别引用DB
"""
import json

from ..common_tools import funcs
from ..common_tools.objs import LinkDataJSONInfo
from ..common_tools import G

# json数据结构:
"""
 {
    "backlink": [],
    "version": 1,
    "link_list": [
            {"card_id": "1627437034945","desc": "yeyeyeyeyeyeyeye2","dir": "\\u2192"},
            {"card_id": "1627437000208","desc": "yeyeyeyeyeyeyeye333","dir": "\\u2192"}],
    "self_data": {"card_id": "1627401415334","desc": "yeyeyeye"},
    "root": [{"nodename": "new_new_group"},
             {"nodename": "new_group"}],
    "node": {
        "new_new_group": [
            {"card_id": "1627437034945"},
            {"card_id": "1627437000208"}],
        "new_group": []
    }
}

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
                "child":[{"card_id":"1620468291507"},{"card_id":"1620468290938"}, {"card_id":"1620468289832"}]
            }
        }
    }
"""


class LinkInfoDB(object):
    @staticmethod
    def exists(card_id:str)->bool:
        return card_exists(card_id)

    @staticmethod
    def get_template(card_id, desc="", version=2) ->dict:
        return get_template(card_id,desc=desc,version=version)

    @staticmethod
    def single_write(linkinfo:"LinkDataJSONInfo",autocommit=True,fromDB=None):
        if fromDB:
            DB=fromDB
        DB.go(DB.table_linkinfo)
        card_id,data=linkinfo.to_DB_record
        if LinkInfoDB.exists(card_id):
            DB.update(values=DB.VALUEEQ(data=data), where=DB.EQ(card_id=card_id))
        else:
            DB.insert(card_id=card_id, data=data)
        if autocommit:
            DB.commit()
            DB.end()

    @staticmethod
    def read(card_id: str)->LinkDataJSONInfo:
        return read_card_link_info(card_id)


#------------------------请使用以上接口,以下的废弃------


def get_template(card_id, desc="", version=2):
    empty_template = {
        "backlink": [],  # backlink只用储存card_id
        "version": version,  # 将来会用
        "link_list": [],
        "link_dict": {},
        "self_data": {  # 自身的数据
            "card_id": card_id,
            "desc": desc if desc else funcs.desc_extract(card_id, fromField=True), # 如果不 fromField会循环引用报错
            "get_desc_from":funcs.Config.get().new_card_default_desc_sync.value,
        },
        "root": [],
        "node": {}
    }
    return empty_template


DB = G.DB
DB.go(DB.table_linkinfo)


def read_card_link_info(card_id: str) -> LinkDataJSONInfo:
    DB.go(DB.table_linkinfo)
    if not card_exists(card_id):
        data = json.dumps(get_template(card_id))
        DB.insert(card_id=card_id, data=data).commit()
    result: "LinkDataJSONInfo" = DB.select(DB.EQ(card_id=card_id)).return_all().zip_up()[0].to_givenformat_data(
        LinkDataJSONInfo)
    DB.end()
    return result



def write_card_link_info(card_id: str, data: str, commit=True):
    """接受两种参数, cid为"""
    DB.go(DB.table_linkinfo)
    if card_exists(card_id):
        DB.update(values=DB.VALUEEQ(data=data), where=DB.EQ(card_id=card_id))
    else:
        DB.insert(card_id=card_id, data=data)
    if commit:
        DB.commit()
        DB.end()


def card_exists(card_id: "str") -> bool:
    DB.go(DB.table_linkinfo)
    result = len(DB.select(DB.EQ(card_id=card_id)).return_all()) > 0

    return result
