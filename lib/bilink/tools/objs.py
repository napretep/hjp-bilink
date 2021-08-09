import json
import os
import re
from dataclasses import dataclass
from typing import Union


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
    backlink: "list[str]"
    version: "int"
    link_list: "list[LinkDataPair]"
    self_data: "LinkDataPair"
    root: "list[LinkDataNode]"
    node: "dict[str,list[LinkDataNode]]"

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

    def todict(self):
        d = {}
        d["backlink"] = self.backlink
        d["version"] = self.version
        d["link_list"]: "list[dict]" = []
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
        return d

    def to_json_string(self):
        s = json.dumps(self.todict())
        return s
