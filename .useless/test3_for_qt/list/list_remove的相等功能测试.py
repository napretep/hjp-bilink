# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'list_remove的相等功能测试.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2021/8/5 17:42'
"""
from dataclasses import dataclass


@dataclass
class LinkDataPair:
    """LinkDataJSONInfo 的子部件, 也可以独立使用"""
    card_id: "str"
    desc: "str" = ""
    dir: "str" = "→"

    @property
    def int_card_id(self):
        return int(self.card_id)

    def todict(self):
        return self.__dict__

    def __eq__(self, other: "LinkDataPair"):
        return self.card_id == other.card_id

    # def __hash__(self):
    #     return self.card_id


@dataclass
class LinkDataNode:  # 在root和group中的结点列表
    """LinkDataJSONInfo 的子部件"""
    card_id: "str" = ""
    nodeuuid: "str" = ""

    def __init__(self, card_id="", nodeuuid="", **kwargs):
        self.card_id = card_id
        self.nodeuuid = nodeuuid

    def todict(self):
        d = {}
        if self.card_id != "":
            d["card_id"] = self.card_id
        if self.nodeuuid != "":
            d["nodeuuid"] = self.nodeuuid
        return d

    def __contains__(self, item):
        return item in self.__dict__

    def __eq__(self, other):
        if type(other) == type(self):
            return other.card_id == self.card_id and other.nodeuuid == self.nodeuuid
        else:
            return other.card_id == self.card_id


if __name__ == "__main__":
    a = LinkDataPair("123", "456")
    b = LinkDataNode("123", "456")
    x = LinkDataPair("123", "4567", "←")
    c = [a]
    # c.remove(b)
    print(a == b)
    pass
