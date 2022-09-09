# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'configsModel.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2021/11/15 1:34'
这是一个比较底层的模块, 尽量不要直接引用其他模块, 用lambda表达式的方式推迟引用
"""
import datetime
import json
import os
import re
import time
from dataclasses import dataclass, field
from enum import unique, Enum
from functools import reduce
from typing import List, Any, Union, Callable

from .language import Translate
from .src_admin import MAXINT, MININT, src
from . import widgets, terms, baseClass
from .compatible_import import *
from .compatible_import import tooltip,  isMac, isWin
from typing import TYPE_CHECKING


class CustomConfigItemView:

    @property
    def Item(self) -> "ConfigModelItem":
        return self._item

    @Item.setter
    def Item(self, value: "ConfigModelItem"):
        self._item = value

    @property
    def Parent(self):
        return self._parent

    @Parent.setter
    def Parent(self, value):
        self._parent = value

    @property
    def View(self) -> "QWidget":
        return self._view

    @View.setter
    def View(self, value: "QWidget"):
        self._view = value

    def __init__(self, configItem: "ConfigModelItem" = None, parent: "QWidget" = None, *args, **kwargs):
        self.Item: "ConfigModelItem" = configItem
        self.Parent: "QWidget" = parent
        self.View: "QWidget" = QWidget(parent)


@dataclass
class GViewData:
    uuid: str
    name: str
    nodes: 'dict[str,list[Union[float,int],Union[float,int]]]'  # key=card_id,value=pos
    edges: 'list[list[str,str]]'  # 在取出时就应该保证边的唯一性,而且主要用来存json字符串,所以不用set

    def to_html_repr(self):
        return f"uuid={self.uuid}<br>" \
               f"name={self.name}<br>" \
               f"node_list={json.dumps(self.nodes)}<br>" \
               f"edge_list={json.dumps(self.edges)}"

    def to_DB_format(self):
        return {
                "uuid" : self.uuid,
                "name" : self.name,
                "nodes": f"{json.dumps(self.nodes)}",
                "edges": f"{json.dumps(self.edges)}"
        }

    def __hash__(self):
        return int(self.uuid, 16)


@dataclass
class GraphMode:
    normal: int = 0
    view_mode: int = 1
    debug_mode :int=2


@dataclass
class GroupReviewDictInterface:
    card_group: 'dict[int,List[str]]' = field(default_factory=dict)
    search_group: 'dict[str,List[int]]' = field(default_factory=dict)
    union_search: str = ""
    version: "float" = 0

    def card_group_insert(self, cid: int, s_str: str):
        if cid not in self.card_group:
            self.card_group[cid] = []
        self.card_group[cid].append(s_str)

    def search_group_insert(self, cid: int, s_str: str):
        if s_str not in self.search_group:
            self.search_group[s_str] = []
        self.search_group[s_str].append(cid)

    def build_union_search(self):
        self.union_search = "or".join([f"{search}" for search in self.search_group.keys()])

    def update_version(self):
        self.version = time.time()

    def __str__(self):
        return json.dumps({"search_group": self.search_group, "card_group": self.card_group}, ensure_ascii=False,
                          indent=4)


@dataclass
class AnswerInfoInterface:
    platform: Any
    card_id: int
    option_num: int

    def __str__(self):
        return json.dumps({"card_id": self.card_id, "option_num": self.option_num}, ensure_ascii=False, indent=4)


@dataclass
class ConfigModelItem:
    instruction: "List[str]"
    value: "Any"
    component: "int"
    tab_at: "str"
    hide: "bool" = False
    display: 'Callable[[Any],Any]' = lambda x: x
    validate: 'Callable[[Any,Any],Any]' = lambda x, item: None
    limit: "list" = field(default_factory=lambda: [0, MAXINT])
    customizeComponent: "Callable[[],CustomConfigItemView.__class__]" = lambda: CustomConfigItemView  # 这个组件的第一个参数必须接受
    _id: "int" = 0  # 0表示无特殊信息

    def setValue(self, value):
        self.value = value

    def to_dict(self):
        return {"value": self.value}


@dataclass
class ComboItem:
    name: str
    value: Any

    def __eq__(self, other: "ComboItem"):
        if isinstance(other, ComboItem):
            return self.value == other.value
        elif isinstance(other, int):
            return self.value == other


@dataclass
class ConfigModel:
    """
    这个用来读取配置表的json文件,使之形成对应,这意味着我需要实现几个方法
    第一, 填入json格式的数据要能准确转化.
    第二, 要能保存写入到对应的文件
    """

    @dataclass
    class Widget:
        spin = 0
        radio = 1
        line = 2
        combo = 3
        list = 4
        none = 5
        inputFile = 6
        inputStr = 7
        label = 8
        text = 9
        customize = 10

    @staticmethod
    def pdfurl_default_system_cmd():
        """因为不同的系统需要的命令不同,所以要这个东西来确定"""
        url = f"""   file:///{{{terms.PDFLink.url}}}#page={{{terms.PDFLink.page}}} """
        if isMac:
            return f'''open -a Safari "{url}" '''
        if isWin:
            return f""" start msedge "{url}" """
        return ""

    gview_admin_default_display: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=["默认的视图管理器展示视图的方式"],
            value=0,
            component=ConfigModel.Widget.none,
            validate=lambda x, item: x in item.limit,
            limit=[ComboItem("tree", 0), ComboItem("list", 1)],
            tab_at=Translate.视图
    ))
    # gview_popup_when_review:ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
    #     instruction=["复习时,相关视图自动弹出,相关视图有多种时,只会弹出一种"],
    #     value=False,
    #     component=ConfigModel.Widget.radio,
    #     tab_at=Translate.视图
    # ))
    # gview_popup_type:ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
    #     instruction=["规定自动弹出哪种视图"],
    #     value=0,
    #     component=ConfigModel.Widget.combo,
    #     limit=[ComboItem(Translate.自动复习视图, 0), ComboItem(Translate.反链视图,1)],
    #     tab_at=Translate.视图
    # ))

    time_up_buzzer: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=["该项如果设为大于0的值,比如10,则在10秒后弹出提示框,提醒你已经看了10秒卡片",
                         "提示框有三个按钮可选, 取消,重新计时,继续, 第一个表示什么都不做, 第二个表示再次计时, 第三个表示执行自动操作",
                         "如果设为0,则表示关闭该功能"
                         ],
            value=0,
            component=ConfigModel.Widget.spin,
            tab_at=Translate.复习相关,
    ))
    time_up_auto_action: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=["该项设置复习时间到后, 选择'继续'按钮所对应的自动操作,可选以下几种自动操作:",
                         "no action, again, hard, good, easy, delay 1 day, delay 3 days, delay 1 week, delay 1 month, customize delay,just show answer",
                         "其中delay表示推迟卡片, 推迟不会有复习记录, customize delay可以在时间到了后手动填写推迟天数"],
            value=0,
            component=ConfigModel.Widget.combo,
            limit=[ComboItem(Translate.不操作, 0), ComboItem(Translate.忘记, 1), ComboItem(Translate.困难, 2),
                   ComboItem(Translate.良好, 3), ComboItem(Translate.简单, 4), ComboItem(Translate.延迟一天, 5),
                   ComboItem(Translate.延迟三天, 6), ComboItem(Translate.延迟一周, 7), ComboItem(Translate.延迟一月, 8),
                   ComboItem(Translate.自定义延迟, 9), ComboItem(Translate.显示答案, 10)],
            tab_at=Translate.复习相关,
    ))
    time_up_skip_click: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=["如果想复习时间到了,跳过选择按钮的环节,直接执行自动操作,请勾选本项"],
            value=False,
            component=ConfigModel.Widget.radio,
            tab_at=Translate.复习相关,
    ))
    freeze_review: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=[
                    "开启后,当到达显示答案的状态时,会冻结复习按钮一段时间,以防止你不假思索地复习卡片",
                    "English Instruction Maybe later"
            ],
            value=False,
            component=ConfigModel.Widget.radio,
            tab_at=Translate.复习相关
    ))
    freeze_review_interval: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=[
                    "阻止你在这个时间结束之前点击复习按钮.单位毫秒",
                    "English Instruction Maybe later"
            ],
            value=10000,
            component=ConfigModel.Widget.spin,
            tab_at=Translate.复习相关,
    ))
    too_fast_warn: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=[
                    "开启后,如果你复习间隔太快,他会提示你, 这个功能只在reviewer中有效",
                    "English Instruction Maybe later"
            ],
            value=False,
            component=ConfigModel.Widget.radio,
            tab_at=Translate.复习相关
    ))
    too_fast_warn_interval: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=[
                    "提示你复习过快的最小间隔,单位是毫秒",
                    "English Instruction Maybe later"
            ],
            value=2000,
            component=ConfigModel.Widget.spin,
            tab_at=Translate.复习相关
    ))
    too_fast_warn_everycard: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=[
                    "当你连续复习X张卡片,并且每两张之间的间隔均小于配置表设定的最小间隔时,才会提示你复习过快",
                    "这里的X, 就是本字段设定的值",
                    "English Instruction Maybe later"
            ],
            value=3,
            component=ConfigModel.Widget.spin,
            tab_at=Translate.复习相关
    ))
    group_review: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=[
                    "假设某个搜索条件下有多张卡,你复习其中一张卡,那么其余卡片也会用相同的选项自动进行复习",
                    "开启后,在 group_review_search_string 中输入搜索词(就像你在搜索栏中做的那样),即可对同属于这个搜索结果的卡片执行同步复习",
                    "English Instruction Maybe later"
            ],
            value=True,
            component=ConfigModel.Widget.radio,
            tab_at=Translate.复习相关
    ))

    group_review_comfirm_dialog: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=[
                    "如果开启,他会在你点复习之前弹出来询问你,让你确认要群组复习的卡片, 你如果不点确定, 他就不会复习",
                    "English Instruction Maybe later"
            ],
            value=True,
            component=ConfigModel.Widget.radio,
            tab_at=Translate.复习相关
    ))
    group_review_just_due_card: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=[
                    "如果开启,则默认排除未到期的卡,仅复习已到期的卡",
                    "English Instruction Maybe later"
            ],
            value=True,
            component=ConfigModel.Widget.radio,
            tab_at=Translate.复习相关
    ))
    group_review_global_condition: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=[
                    "默认将一个条件加到所有复习条件上",
                    "English Instruction Maybe later"
            ],
            value="",
            component=ConfigModel.Widget.line,
            tab_at=Translate.复习相关
    ))
    group_review_search_string: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=[
                    "这里填群组复习的条件,列表的每一项为一个完整搜索条件",
                    "如果不会填,有更简单操作,点击browser界面菜单栏->hjp_bilink->群组复习操作->保存当前搜索条件为群组复习条件,即可",
                    "English Instruction Maybe later"
            ],
            value=[],
            validate=lambda text, item:  # 这个地方要有两次不同方式的调用所以要用两个不同的判断
            (re.search(r"\S", text) and text not in item.value) if type(text) == str
            else reduce(lambda x, y: x and y, map(lambda x: re.search(r"\S", x), text), True) if type(text) == list
            else False,
            component=ConfigModel.Widget.list,
            tab_at=Translate.复习相关
    ))
    length_of_desc: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=[
                    "length_of_desc项控制从卡片正文提取多少字符作为链接的标题,该项仅支持非负数字,0表示不限制",
                    "English Instruction Maybe later"
            ],
            value=0,
            component=ConfigModel.Widget.spin,
            tab_at=Translate.链接相关
    ))
    desc_sync: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=[
                    "开启后,所有的链接内容,都会从卡片内容同步提取,关闭,则可打开卡片的anchor,手动设定链接的内容,或者指定卡片自动同步",
                    "English Instruction Maybe later"
            ],
            value=False,
            component=ConfigModel.Widget.radio,
            tab_at=Translate.链接相关
    ))

    descExtractTable: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=["在本项设置中,你可以指定提取卡片描述的方式, 比如指定什么模板,提取哪个字段,长度多少,还可以写正则表达式, 双击单元格修改,加号按钮增加规则,减号去掉选中规则"],
            value=[],  # 模板ID,字段ID,长度限制,正则表达式,是否自动更新描述
            component=ConfigModel.Widget.customize,
            tab_at=Translate.链接相关,
            customizeComponent=lambda: widgets.ConfigWidget.DescExtractPresetTable
    ))

    new_card_default_desc_sync: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=[
                    "开启后,链接默认被设定为与卡片内容保持同步,关闭后,则链接默认不同步",
                    "English Instruction Maybe later"
            ],
            value=True,
            component=ConfigModel.Widget.radio,
            tab_at=Translate.链接相关
    ))
    add_link_tag: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=[
                    "开启时,链接操作结束后,会给这组参与链接的卡片添加一个时间戳tag",
                    "这个功能适合作为链接操作的历史记录使用",
                    "English Instruction Maybe later"
            ],
            value=True,
            component=ConfigModel.Widget.radio,
            tab_at=Translate.链接相关
    ))
    open_browser_after_link: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=[
                    "开启时,链接操作结束后,会打开浏览窗口,展示链接的项",
                    "English Instruction Maybe later"
            ],
            value=True,
            component=ConfigModel.Widget.radio,
            tab_at=Translate.链接相关
    ))
    delete_intext_link_when_extract_desc: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=[
                    "本项用来控制当执行卡片内容提取时,是否将文内链接也识别为卡片内容一并提取",
                    "若开启,此时提取卡片内容之前,会删掉文内链接的信息再提取,若关闭,则会直接提取",
                    "English Instruction Maybe later"
            ],
            value=True,
            component=ConfigModel.Widget.radio,
            tab_at=Translate.链接相关
    ))

    # ------------------ 下面的统一为快捷键设置
    default_link_mode: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=[
                    "使用快捷键时,默认执行的链接操作,可填3,4两个数字值,3表示完全链接,4表示组到组连接,默认一张卡为一组",
                    "English Instruction Maybe later"
            ],
            value=3,
            component=ConfigModel.Widget.combo,
            tab_at=Translate.快捷键,
            limit=[ComboItem(Translate.完全图绑定, 3), ComboItem(Translate.组到组绑定, 4)],
    ))
    default_unlink_mode: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=[
                    "使用快捷键时,默认执行的取消链接操作,可填5,6两个数字值,6表示按结点取消链接,5表示按路径取消链接",
                    "English Instruction Maybe later"
            ],
            value=6,
            component=ConfigModel.Widget.combo,
            tab_at=Translate.快捷键,
            limit=[ComboItem(Translate.按路径解绑, 5), ComboItem(Translate.按结点解绑, 6)],
    ))
    default_insert_mode: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=[
                    "使用快捷键时,默认执行的插入连接池的操作,可填0,1,2三个数字值,0表示清空后插入,1表示追加插入,2表示编组插入",
                    "English Instruction Maybe later"
            ],
            value=0,
            component=ConfigModel.Widget.combo,
            tab_at=Translate.快捷键,
            limit=[ComboItem(Translate.清空后插入, 0), ComboItem(Translate.直接插入, 1), ComboItem(Translate.编组插入, 2)],
    ))
    default_copylink_mode: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=[
                    "使用快捷键时,默认执行的链接复制操作,可填0,1,2,3,0表示复制为文内链接,1表示复制为html链接",
                    "2表示复制为markdown链接,3表示复制为orgmode链接",
                    "English Instruction Maybe later"
            ],
            value=0,
            component=ConfigModel.Widget.combo,
            tab_at=Translate.快捷键,
            limit=[ComboItem(Translate.文内链接, 0), ComboItem(Translate.文内链接 + "(new)", 1),
                   ComboItem(Translate.html链接, 2), ComboItem(Translate.markdown链接, 3),
                   ComboItem(Translate.orgmode链接, 4)],
    ))
    shortcut_for_link: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=[
                    "本项用来控制链接操作的快捷键,格式为'ctrl+A'的形式,修改后需要重开anki实现快捷键绑定 ",
                    "English Instruction Maybe later"
            ],
            value="alt+ctrl+1",
            component=ConfigModel.Widget.line,
            tab_at=Translate.快捷键
    ))
    shortcut_for_unlink: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=[
                    "本项用来控制取消链接操作的快捷键,格式为'ctrl+A'的形式,修改后需要重开anki实现快捷键绑定  ",
                    "English Instruction Maybe later"
            ],
            value="alt+ctrl+2",
            component=ConfigModel.Widget.line,
            tab_at=Translate.快捷键
    ))
    shortcut_for_insert: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=[
                    "本项用来控制卡片插入链接池操作的快捷键,格式为'ctrl+A'的形式,修改后需要重开anki实现快捷键绑定  ",
                    "English Instruction Maybe later"
            ],
            value="alt+ctrl+3",
            component=ConfigModel.Widget.line,
            tab_at=Translate.快捷键
    ))
    shortcut_for_copylink: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=[
                    "本项用来控制复制卡片链接的快捷键,格式为'ctrl+A'的形式,修改后需要重开anki实现快捷键绑定  ",
                    "English Instruction Maybe later"
            ],
            value="alt+ctrl+4",
            component=ConfigModel.Widget.line,
            tab_at=Translate.快捷键
    ))
    shortcut_for_openlinkpool: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=[
                    "本项用来控制打开链接池的快捷键,格式为'ctrl+A'的形式,修改后需要重开anki实现快捷键绑定 ",
                    "English Instruction Maybe later"
            ],
            value="alt+ctrl+`",
            component=ConfigModel.Widget.line,
            tab_at=Translate.快捷键
    ))
    anchor_style_text: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=["在这里写入anchor的样式,读取的先后顺序为 text,file,preset",
                         "如果你想自己修改anchor样式,可以参考文件:",
                         f"{os.path.join(src.path.resource_data, 'anchor_example.html')}"],
            value="",
            component=ConfigModel.Widget.text,
            tab_at="anchor"
    ))
    anchor_style_file: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=["在这里写入anchor的样式,读取的先后顺序为 text,file,preset",
                         "如果你想自己修改anchor样式,可以参考文件:",
                         f"{os.path.join(src.path.resource_data, 'anchor_example.html')}"],
            value="",
            component=ConfigModel.Widget.line,
            validate=lambda x, item: type(x) == str and (os.path.isfile(x) or x == "" or not re.search(r"\S", x)),
            tab_at="anchor"
    ))
    anchor_style_preset: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=["在这里写入anchor的样式,读取的先后顺序为 text,file,preset",
                         "如果你想自己修改anchor样式,可以参考文件:",
                         f"{os.path.join(src.path.resource_data, 'anchor_example.html')}"],
            value=0,
            component=ConfigModel.Widget.combo,
            tab_at="anchor",
            limit=[ComboItem(Translate.手风琴式, 0), ComboItem(Translate.直铺式, 1)]
    ))

    auto_backup: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=["开启链接数据自动备份,每当关闭anki时,会检查是否满足备份条件", "English Instruction Maybe later"],
            value=True,
            component=ConfigModel.Widget.radio,
            tab_at=Translate.同步与备份
    ))
    # distChoice: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
    #         instruction=["当你同时装了anki网络版与本地版的hjp-bilink, 你选择启动哪一个版本?默认选择本地版"],
    #         value=0,
    #         tab_at=Translate.同步与备份,
    #         limit=[ComboItem(Translate.本地版, 0), ComboItem(Translate.anki网络版, 1)]
    #
    # ))
    auto_backup_interval: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=["自动备份链接数据的间隔,单位是小时", "English Instruction Maybe later"],
            value=12,
            component=ConfigModel.Widget.spin,
            tab_at=Translate.同步与备份
    ))
    auto_backup_path: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=["链接数据自动备份的地址,默认为空则地址为数据库所在文件夹"],
            value="",
            validate=lambda x, item: type(x) == str and (os.path.isdir(x) or x == "" or not re.search(r"\S", x)),
            component=ConfigModel.Widget.line,
            tab_at=Translate.同步与备份
    ))
    last_backup_time: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=["不必解释"],
            value=0,
            validate=lambda x, item: type(x) in {float, int},
            component=ConfigModel.Widget.label,
            tab_at=Translate.同步与备份,
            display=lambda x: time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(x))
    ))
    PDFUrlLink_style: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=["PDF链接的通用css样式"],
            value="""
background-color:green;
color:white;
text-decoration:none;""",
            tab_at=Translate.pdf链接,
            component=ConfigModel.Widget.text

    ))
    PDFUrlLink_cmd: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=["当你点击pdf链接时,会根据如下命令执行指定的程序",
                         f"其中{terms.PDFLink.url}表示文件路径会被自动转写成file协议的url编码, {terms.PDFLink.page}代表pdf的页码",
                         f"你可以用{terms.PDFLink.path}代替{terms.PDFLink.url},{terms.PDFLink.path}表示文件路径本身,不转写成url编码格式"],
            component=ConfigModel.Widget.line,
            value=ConfigModel.pdfurl_default_system_cmd(),
            tab_at=Translate.pdf链接,
    ))
    PDFUrlLink_page_num_str: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=[f"{terms.PDFLink.page}该占位符将会被替换成对应的页码"],
            value=f"|page={{{terms.PDFLink.page}}}",
            component=ConfigModel.Widget.line,
            tab_at=Translate.pdf链接,
    ))
    PDFUrlLink_default_show_pagenum: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=["选中表示开启,例子: 当pdf链接显示名字为 ABC.pdf,页码显示为|page=10,则在最终插入时, 名字会变成 ABC.pdf|page=10"],
            value=True,
            component=ConfigModel.Widget.radio,
            tab_at=Translate.pdf链接,
    ))

    PDFUrlLink_booklist: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
            instruction=["遇到指定路径的pdf,提供预先设置好的显示名称,样式, 是否显示页码,双击左侧表格单元修改对应行内容"],
            value=[],
            component=ConfigModel.Widget.customize,
            customizeComponent=lambda: widgets.ConfigWidget.PDFUrlLinkBooklist,
            tab_at=Translate.pdf链接,
    ))

    # PDFUrlLink_path_arg:ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
    #     instruction=["{xxx},用花括号包裹起来的是替换字符,在执行命令时会被替换成对应的内容, fileurl表示将pdf路径转换成file协议的url编码",
    #                  "如果"],
    #     value="",
    #     component=ConfigModel.Widget.line,
    #
    # ))
    # PDFUrlLink_page_arg:ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
    #     instruction=[""],
    #     value="",
    # ))
    def save_to_file(self, path):
        json.dump(self.get_dict(), open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=4)

    def get_dict(self):
        d = {}
        for key, value in self.__dict__.items():
            if isinstance(value, ConfigModelItem):
                d[key] = value.value
            else:
                d[key] = value
        return d

    def to_json_string(self):
        return json.dumps(self.get_dict(), ensure_ascii=False, indent=4)

    @staticmethod
    def json_load(path):
        """从path读取,立即保存到path,是因为有可能这里的版本更高级,有新功能"""
        fromdata: dict = json.load(open(path, "r", encoding="utf-8"))
        todata: dict = {}
        for k, v in fromdata.items():
            todata[k] = ConfigModelItem(**v)
        config = ConfigModel(**todata)
        return config

    def get_editable_config(self):
        d = {}
        for key, value in self.__dict__.items():

            if type(value).__name__ != ConfigModelItem.__name__ or value.hide:
                continue
            d[key] = value
        return d

    def __setitem__(self, key, value):
        self.__dict__[key].value = value

    def __iter__(self):
        return self.__dict__.items().__iter__()

    def __getitem__(self, item):
        return self.__dict__[item]

    def __contains__(self, item):
        return item in self.__dict__.keys()


if __name__ == '__main__':
    test = """
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
    c = ConfigModel()
    print(c.open_browser_after_link.value)
