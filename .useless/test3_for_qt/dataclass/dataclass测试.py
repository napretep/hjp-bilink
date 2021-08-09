import json
from dataclasses import dataclass, field, asdict
from typing import Union, Any


@dataclass
class A:
    b: "int" = 0
    c: "int" = 1
    h: "list" = field(default_factory=list)


@dataclass
class B(A):
    e: "int" = 2
    f: "int" = 3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.e: "str" = "x"
        pass

    def __post_init__(self):
        self.e: "str" = "x"

    def say(self, s):
        print(s + self.e)


@dataclass
class LinkDataPair:
    card_id: "str"
    desc: "str" = ""
    dir: "str" = "→"

    @property
    def int_card_id(self):
        return int(self.card_id)

    def todict(self):
        return self.__dict__


@dataclass
class LinkDataNode:
    card_id: "str" = ""
    nodename: "str" = ""

    def todict(self):
        d = {}
        if self.card_id != "":
            d["card_id"] = self.card_id
        if self.nodename != "":
            d["nodename"] = self.nodename
        return d


@dataclass
class LinkDataJSONInfo:
    """本质上,只有两个实体,pair{}和 node{}"""
    backlink: "list[str]"
    version: "int"
    link_list: "list[LinkDataPair]"
    self_data: "LinkDataPair"
    root: "list[LinkDataNode]"
    node: "dict[str,list[LinkDataNode]]"
    link_dict: "dict[str,LinkDataPair]" = None

    def __init__(self, d: "dict"):
        self._src_data = d
        self.backlink = d["backlink"]
        self.version = d["version"]
        self.link_list = [LinkDataPair(**link) for link in d["link_list"]]
        self.self_data = LinkDataPair(**d["self_data"])
        self.root = [LinkDataNode(**link) for link in d["root"]]
        self.node = {}
        for nodename, li in d["node"].items():
            self.node[nodename] = [LinkDataNode(**link) for link in li]
        self.link_dict = {}
        for pair in self.link_list:
            self.link_dict[pair.card_id] = pair

    def todict(self):
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
        for nodename, nodeli in self.node.items():
            d["node"][nodename] = []
            for node in nodeli:
                d["node"][nodename].append(node.todict())
        d["link_dict"] = {}
        for k, v in self.link_dict:
            d["link_dict"][k] = v.todict()
        return d

    def to_json_string(self):
        s = json.dumps(self.todict())
        return s


def _kwargs(**kwargs):
    return kwargs


if __name__ == "__main__":
    b = B()
    b.h.append(1)
    print(b)
    # print(_kwargs(**b.__dict__))
    # print(_kwargs(**asdict(b)))
    d = {
        "backlink": ["1333355241723", "1333355241723"],  # backlink只用储存card_id
        "version": 1,  # 将来会用
        "link_list": [  # 链接列表,也就是所有有关的卡片
            {
                "card_id": "1333355241723",
                "desc": "intellect",
                "dir": "\u2192"
            }
        ],
        "self_data": {  # 自身的数据
            "card_id": "1333355241734",
            "desc": ""
        },
        "root": [  # 根节点, 是anchor的第一层
            {"card_id": "1333355241723"},
            {"nodename": "new_group"}
        ],
        "node": {  # 在root中查找到键名为nodename时,在这里找他的列表,
            "new_group": [{"card_id": "1620468291507"}, {"card_id": "1620468290938"}, {"card_id": "1620468289832"}]
        }
    }
    x = LinkDataJSONInfo(d)
    q = x.link_list[0]
    q.card_id = "uuuuuuuuuuuuuuuuuuuuuuuu"
    print(json.dumps(x.todict()))
