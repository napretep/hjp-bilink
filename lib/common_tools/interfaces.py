# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'interfaces.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2021/11/15 1:34'
"""
import json
from dataclasses import dataclass, field
from enum import unique, Enum
from typing import List, Any, Union

from aqt.utils import tooltip

@dataclass
class GViewData:
    uuid:str
    name:str
    nodes:'dict[str,list[Union[float,int],Union[float,int]]]'#key=card_id,value=pos
    edges:'list[list[str,str]]' #在取出时就应该保证边的唯一性,而且主要用来存json字符串,所以不用set

    def to_html_repr(self):
        return f"uuid={self.uuid}<br>" \
               f"name={self.name}<br>" \
               f"node_list={json.dumps(self.nodes)}<br>" \
               f"edge_list={json.dumps(self.edges)}"

    def to_DB_format(self):
        return {
            "uuid":self.uuid,
            "name":self.name,
            "nodes":json.dumps(self.nodes),
            "edges":json.dumps(self.edges)
        }

@dataclass
class GraphMode():
    normal:int = 0
    view_mode:int = 1


@dataclass
class AutoReviewDictInterface:
    card_group:'dict[int,List[str]]'=field(default_factory=dict)
    search_group:'dict[str,List[int]]'=field(default_factory=dict)
    union_search:str=""

    def card_group_insert(self, cid: int, s_str: str):
        if cid not in self.card_group:
            self.card_group[cid] = []
        self.card_group[cid].append(s_str)

    def search_group_insert(self, cid: int, s_str: str):
        if s_str not in self.search_group:
            self.search_group[s_str]=[]
        self.search_group[s_str].append(cid)

    def build_union_search(self):
        self.union_search = "or".join([f"{search}" for search in self.search_group.keys()])

    def __str__(self):
        return json.dumps({"search_group": self.search_group,"card_group":self.card_group},ensure_ascii=False, indent=4)

@dataclass
class AnswerInfoInterface:
    platform:Any
    card_id:int
    option_num:int

    def __str__(self):
        return json.dumps({"card_id":self.card_id,"option_num":self.option_num},ensure_ascii=False, indent=4)


@dataclass
class ConfigInterfaceItem:
    instruction:List[str]
    value:Any



@dataclass
class ConfigInterface:
    """
    这个用来读取配置表的json文件,使之形成对应,这意味着我需要实现几个方法
    第一, 填入json格式的数据要能准确转化.
    第二, 要能保存写入到对应的文件
    """
    auto_review:ConfigInterfaceItem = field(default_factory=lambda: ConfigInterfaceItem(
        instruction=[
            "假设某个搜索条件下有多张卡,你复习其中一张卡,那么其余卡片也会用相同的选项自动进行复习,填入0表示关闭,填入1表示开启,",
            "开启后,在 auto_review_search_string 中输入搜索词(就像你在搜索栏中做的那样),即可对同属于这个搜索结果的卡片执行同步复习",
            "English Instruction Maybe later"
        ],
        value=0
    ))
    auto_review_search_string:ConfigInterfaceItem = field(default_factory=lambda: ConfigInterfaceItem(
        instruction=[
            "比如,'tag:xxx', 'prop:due=0' 之类的语法都可以, 以数组的形式记录, 每一项为一个完整搜索条件",
            "English Instruction Maybe later"
        ],
        value=[]
    ))

    length_of_desc:ConfigInterfaceItem = field(default_factory=lambda :ConfigInterfaceItem(
        instruction=[
            "length_of_desc项控制从卡片正文提取多少字符作为链接的标题,该项仅支持非负数字,0表示不限制",
            "English Instruction Maybe later"
        ],
        value=0
    ))
    desc_sync:ConfigInterfaceItem = field(default_factory=lambda:ConfigInterfaceItem(
        instruction=[
            "desc_sync_enabled项控制是否开启自动绑定卡片内容和链接标题,",
            "填入1表示开启,则将自动同步卡片内容和链接标题两者的内容,填入0表示关闭,则可打开卡片的anchor,手动修改链接标题",
            "English Instruction Maybe later"
        ],
        value=0
    ))
    add_link_tag: ConfigInterfaceItem = field(default_factory=lambda: ConfigInterfaceItem(
        instruction=[
            "add_link_tag_enabled用来控制链接操作结束后,是否给这组参与链接的卡片添加一个时间戳tag",
            "这个功能适合作为链接操作的历史记录使用,填入1表示开启,填入0表示关闭",
            "English Instruction Maybe later"
        ],
        value=1
    ))
    open_browser_after_link: ConfigInterfaceItem = field(default_factory=lambda: ConfigInterfaceItem(
        instruction=[
            "open_browser_after_link用来控制链接操作结束后,是否打开浏览窗口,展示链接的项",
            "填入1表示开启,填入0表示关闭",
            "English Instruction Maybe later"
        ],
        value=1
    ))
    delete_intext_link_when_extract_desc:ConfigInterfaceItem = field(default_factory=lambda: ConfigInterfaceItem(
        instruction=[
            "本项用来控制当执行卡片内容提取时,是否将文内链接也识别为卡片内容一并提取",
            "填入1表示开开启,此时提取卡片内容之前,会删掉文内链接的信息再提取,填入0表示关闭,则会直接提取",
            "English Instruction Maybe later"
        ],
        value=1
    ))

#------------------ 下面的统一为快捷键设置
    default_link_mode: ConfigInterfaceItem = field(default_factory=lambda: ConfigInterfaceItem(
        instruction=[
            "使用快捷键时,默认执行的链接操作,可填0,1两个数字值,0表示完全链接,1表示组到组连接,默认一张卡为一组",
            "English Instruction Maybe later"
        ],
        value=0
    ))
    default_unlink_mode: ConfigInterfaceItem = field(default_factory=lambda: ConfigInterfaceItem(
        instruction=[
            "使用快捷键时,默认执行的取消链接操作,可填0,1两个数字值,0表示按结点取消链接,1表示按路径取消链接",
            "English Instruction Maybe later"
        ],
        value=0
    ))
    default_insert_mode: ConfigInterfaceItem = field(default_factory=lambda: ConfigInterfaceItem(
        instruction=[
            "使用快捷键时,默认执行的插入连接池的操作,可填0,1,2两个数字值,0表示清空后插入,1表示追加插入,2表示编组插入",
            "English Instruction Maybe later"
        ],
        value=0
    ))
    default_copylink_mode: ConfigInterfaceItem = field(default_factory=lambda:ConfigInterfaceItem(
        instruction=[
            "使用快捷键时,默认执行的链接复制操作,可填0,1,2,3,0表示复制为文内链接,1表示复制为html链接",
            "2表示复制为markdown链接,3表示复制为orgmode链接",
            "English Instruction Maybe later"
        ],
        value=0
    ))
    shortcut_for_link: ConfigInterfaceItem = field(default_factory=lambda: ConfigInterfaceItem(
        instruction=[
            "本项用来控制链接操作的快捷键,格式为'ctrl+A'的形式,填入不规范或导致报错,会自动重置为空字符串'' ",
            "English Instruction Maybe later"
        ],
        value=""
    ))
    shortcut_for_unlink: ConfigInterfaceItem = field(default_factory=lambda: ConfigInterfaceItem(
        instruction=[
            "本项用来控制取消链接操作的快捷键,格式为'ctrl+A'的形式,填入不规范或导致报错,会自动重置为空字符串'' ",
            "English Instruction Maybe later"
        ],
        value=""
    ))
    shortcut_for_insert: ConfigInterfaceItem = field(default_factory=lambda: ConfigInterfaceItem(
        instruction=[
            "本项用来控制卡片插入链接池操作的快捷键,格式为'ctrl+A'的形式,填入不规范或导致报错,会自动重置为空字符串'' ",
            "English Instruction Maybe later"
        ],
        value=""
    ))
    shortcut_for_copylink: ConfigInterfaceItem = field(default_factory=lambda: ConfigInterfaceItem(
        instruction=[
            "本项用来控制复制卡片链接的快捷键,格式为'ctrl+A'的形式,填入不规范或导致报错,会自动重置为空字符串'' ",
            "English Instruction Maybe later"
        ],
        value=""
    ))



    def save_to_file(self,path):
        try:
            cfg = self.json_load(path)
            if cfg.auto_review_search_string.value != self.auto_review_search_string.value:
                from . import G,language
                G.signals.on_auto_review_search_string_changed.emit()
                tooltip(language.Translate.重建数据库)
        except:
            pass
        json.dump(self.get_dict(),open(path,"w",encoding="utf-8"),ensure_ascii=False, indent=4)

    def get_dict(self):
        d = {}
        for key, value in self.__dict__.items():
            if isinstance(value, ConfigInterfaceItem):
                d[key] = value.__dict__
            else:
                d[key] = value
        return d

    def to_json_string(self):
        return json.dumps(self.get_dict(),ensure_ascii=False, indent=4)

    @staticmethod
    def json_load(path):
        """从path读取,立即保存到path,是因为有可能这里的版本更高级,有新功能"""
        fromdata:dict = json.load(open(path,"r",encoding="utf-8"))
        todata:dict={}
        for k,v in fromdata.items():
            todata[k]=ConfigInterfaceItem(**v)
        config = ConfigInterface(**todata)
        return config

if __name__ == '__main__':
    test= """
    {
    "ins_说明_length_of_desc":["hlee","gaga"],
    "add_link_tag": true,
    "default_insert_mode": 0,
    "default_link_mode": 0,
    "default_unlink_mode": 1,
    "length_of_desc": 32,
    "open_browser_after_link": true,
    "shortcut_for_insert": "",
    "shortcut_for_link": "",
    "shortcut_for_unlink": ""
}
    """
    c=ConfigInterface()
    print(c.open_browser_after_link.value)