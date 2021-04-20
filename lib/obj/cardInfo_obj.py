import copy
import json

linktemplate = {
    "card_id": "",
    "self_desc": "",
    "link_list": [],
    "link_tree": [],
    "card_dict": {},
    "group_info": {}
}


class CardLinkInfo:
    """
    20210417123432版本
    旧版兼容接口
    card_linked_pairLi:List[Pair], 以Pair类型为元素的列表
    card_selfdata_dict={ 这个东西在anchor里叫做 model_dataJSON, 其实是一回事.
        "menuli":[{"type": "cardinfo", "card_id": "1611035897919" },
        {"type":"groupinfo","groupname":"new group"}]
        "groupinfo":{#groupinfo不做嵌套处理, 因为不需要这么多.
            "new group": ["1611035897919","1611035897919","1611035897919"],
            "new new group": ["1611035897919","1611035897919","1611035897919"]
        }
    }, 表达链接的存储结构
    cardinfo_dict:{"card_id":Pair} 用来查询卡片的具体内容

    新版数据库JSON格式规范
    字段1 : card_id : 123456789
    字段2 : info:{
        "card_id":"123456789",
        "link_list":["123456789","123456789","123456789","123456789","123"]
        "link_tree":[{"card_id":"123456789"},{"groupname":"1234567"},{"card_id":"123"},{"groupname":"123456789"]
        "card_dict":{
            "123456789":{"card_id":"123456789","desc":"ABCDE","dir":"→"},
            "123456789":{"card_id":"123456789","desc":"ABCDE","dir":"→"}
        }
        group_info:{
            "new group":[{"card_id":"123456789"},{"groupname":"1234567"},{"card_id":"123"},{"groupname":"123456789"],
            "new group2":[{"card_id":"123456789"},{"groupname":"1234567"},{"card_id":"123"},{"groupname":"123456789"]
        }
    }
    """

    def __init__(self, card_id, jsondata=None):
        self.card_id = card_id
        self.info = jsondata if jsondata is not None else copy.deepcopy(linktemplate)
        self.self_desc = self.info["self_desc"]
        self.link_list = self.info["link_list"]
        self.link_tree = self.info["link_tree"]
        self.card_dict = self.info["card_dict"]
        self.group_info = self.info["group_info"]
        self.card_linked_pairLi = []
        self.card_selfdata_dict = {"menuli": [], "groupinfo": {}}
        self.cardinfo_dict = {}

    def info_toDBstring(self):
        string = json.dumps(self.info).replace("'", "''")
        return string

    def __setattr__(self, name, value):
        self.__dict__[name] = value
        if name in ["self_desc"]:
            self.info[name] = value
