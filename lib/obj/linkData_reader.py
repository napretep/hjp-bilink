"""
表结构:
    20210417123432版本
    旧版兼容接口
    card_linked_pairLi:List[Pair], 以Pair类型为元素的列表
    card_selfdata_dict={
        "menuli":[{"type": "cardinfo", "card_id": "1611035897919" },
        {"type":"groupinfo","groupname":"new group"}]
        "groupinfo":{#groupinfo不做嵌套处理, 因为不需要这么多.
            "new group": [1611035897919]
        }
    }, 表达链接的存储结构
    cardinfo_dict:{"card_id":Pair} 用来查询卡片的具体内容

    新版数据库JSON格式规范
    字段1 : card_id : 123456789
    字段2 : info:
            {
            "link_list":[
                {"card_id":"1620468291507","desc":"d","dir":"→"},
                {"card_id":"1620468290938","desc":"c","dir":"→"},
                {"card_id":"1620468289832","desc":"b","dir":"→"}
            ],
            "node":{"new_group":[{"card_id":"1620468291507"},{"card_id":"1620468290938"}, {"card_id":"1620468289832"}]},
            "root":[{"nodename":"new_group"}],
            "self_data":{"card_id":"1620468288991","desc":"A"},
            "version":1
            }


    <!--<script id="hjp_bilink_data">hjp_bilink_data=[{"card_id": "1618912345046", "desc": "B", "dir": "→"}]</script>
<script id="hjp_bilink_selfdata">hjp_bilink_selfdata={"menuli": [], "groupinfo": {}}</script>-->

最新的id 是 hjp_bilink_info_v1
"""

import json, re
import os

from anki.notes import Note
from aqt.utils import showInfo

from .handle_DB import LinkDataDBmanager
from .languageObj import rosetta as say
from .linkData_syncer import DataSyncer
from .utils import BaseInfo, Pair, console, Config, USER_FOLDER, JSONFile_FOLDER, template_data
from bs4 import BeautifulSoup, element
from aqt import mw


# class FieldHandler(Config):
# """可能是将来的统一类, 用来操作从field中提取"""



class LinkDataReader(Config):
    """
    用来统一读取链接数据的接口.
    """

    def __init__(self, card_id):
        super().__init__()
        self.card_id = card_id
        self.storageLocation = self.user_cfg["linkInfoStorageLocation"]
        self.consolerName = self.base_cfg["consoler_Name"]
        self.data_version = self.base_cfg["data_version"]
        self.readFuncDict = {
            0: DataDBReader,
            1: DataFieldReader,
            2: DataJSONReader
        }

    def read(self):
        """用来读取链接信息为下一步的按钮渲染做准备, 并且作兼容处理, """
        data = self.readFuncDict[self.storageLocation](self.card_id).read()
        return DataSyncer(data).sync().data


class DataFieldReader(Config):
    """
    从字段中读取的工具
    """

    def __init__(self, card_id):
        super().__init__()
        if type(card_id) == str:
            card_id = int(card_id)
        self.card_id = card_id
        self.consolerName = self.base_cfg["consoler_Name"]
        self.data_version = self.base_cfg["data_version"]
        self.note: Note = mw.col.getCard(card_id).note()
        self.field = self.note.fields[self.user_cfg["appendNoteFieldPosition"]]
        self.domRoot = BeautifulSoup(self.field, "html.parser")
        self.comment_el = self.comment_el_select()
        self.script_el_li = self.script_el_select()
        self.json_data = self.json_data_make()
        self.link_list = self.json_data["link_list"]
        self.root = self.json_data["root"]
        self.node = self.json_data["node"]

    def json_data_make(self):
        """制作JSON数据"""
        json_data = template_data(self.card_id,self.data_version)
        old_keywords1 = ["menuli", "groupinfo"]
        if self.script_el_li != [None, None]:
            for el in self.script_el_li:
                el_str = el.string
                try:
                    el_json = json.loads(re.sub(fr"{self.consolerName}\w+=", "", el_str))
                except json.JSONDecodeError as e:
                    print(repr(e))

                # 我们要将最终数据直接保存成json_data变量中的样子,所以下面的写法,要兼容新版和旧版.
                if "version" in el_json:
                    if el_json["version"] == self.base_cfg["data_version"]:  # 这个版本直接就提取了
                        json_data = el_json
                    else:  # 目前还没有其他版本.
                        pass
                else:  # 连版本字段都不存在,那就是最旧的版本.
                    if "hjp_bilink_data" in el_str:
                        json_data["link_list"] = el_json
                    if "hjp_bilink_selfdata" in el_str:
                        json_data["root"] = el_json["menuli"]
                        json_data["node"] = el_json["groupinfo"]

        return json_data

    def script_el_select(self):
        """读取指定的脚本内容"""
        if self.comment_el is not None:
            comment = BeautifulSoup(self.comment_el.string, "html.parser")
            return comment.find_all(name="script", attrs={"id": re.compile(fr"{self.consolerName}\w+")})
        else:
            return [None, None]

    def comment_el_select(self):
        """读取指定的注释内容"""
        parent_el, dataType = self.domRoot, self.consolerName
        return parent_el.find(text=lambda text: isinstance(text, element.Comment) and dataType in text)

    def read(self):
        """这是从JSON,DB,FIELD读取数据的统一接口"""
        return self.json_data


class DataDBReader(Config):
    """从数据库中读取数据"""
    def __init__(self,card_id):
        super().__init__()
        if type(card_id) == str:
            card_id = int(card_id)
        self.card_id = card_id
        self.consolerName = self.base_cfg["consoler_Name"]
        self.data_version = self.base_cfg["data_version"]
        self.DB=LinkDataDBmanager()
        self.results = self.DB.data_fetch(card_id)
        self.jsondata_make()

    def jsondata_make(self):
        if self.results!=[]: #即存在
            json_str = self.results[0][1]
            self.data = json.loads(json_str)
        else:#不存在就设计这个。
            self.data = template_data(self.card_id,self.data_version)
            self.DB.data_update(self.card_id,self.data)

    def read(self):
        return self.data

    pass


class DataJSONReader(Config):
    """从JSON文件中读取数据"""
    def __init__(self,card_id):
        super().__init__()
        if type(card_id) == str:
            card_id = int(card_id)
        self.card_id = card_id
        self.consolerName = self.base_cfg["consoler_Name"]
        self.data_version = self.base_cfg["data_version"]
        self.jsondata_make()

    def jsondata_make(self):
        path = os.path.join(JSONFile_FOLDER,str(self.card_id)+".json")
        if not os.path.exists(JSONFile_FOLDER):
            os.mkdir(JSONFile_FOLDER)
        if os.path.exists(path):
            json_str = open(path, "r", encoding="utf-8").read()
            self.data = json.loads(json_str)
        else:
            self.data = template_data(self.card_id,self.data_version)
            json_str=json.dumps(self.data,ensure_ascii=False,sort_keys=True, indent=4, separators=(',', ':'))
            f = open(path, "w", encoding="utf-8")
            f.write(json_str)
            f.close()
    def read(self):
        return self.data
    pass
