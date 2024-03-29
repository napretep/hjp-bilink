# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'configsModel.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2021/11/15 1:34'
这是一个比较底层的模块, 尽量不要直接引用其他模块, 用lambda表达式的方式推迟引用
"""
import abc
import datetime
import json
import os
import re
import time
from dataclasses import dataclass, field
from enum import unique, Enum
from functools import reduce
from typing import *
# from .baseClass import CustomConfigItemView
from .language import Translate
from .src_admin import MAXINT, MININT, src
from . import widgets, terms, baseClass, G
from .compatible_import import *
from .compatible_import import tooltip, isMac, isWin
from typing import TYPE_CHECKING


class SafeImport:
    @property
    def funcs(self):
        from . import funcs
        return funcs

    @property
    def objs(self):
        from . import objs
        return objs


safe = SafeImport()
# class CustomConfigItemView(metaclass=abc.ABCMeta):
#
#     @property
#     def Item(self) -> "ConfigModelItem":
#         return self._item
#
#     @Item.setter
#     def Item(self, value: "ConfigModelItem"):
#         self._item = value
#
#     @property
#     def Parent(self):
#         return self._parent
#
#     @Parent.setter
#     def Parent(self, value):
#         self._parent = value
#
#     # @property
#     # def View(self) -> "QWidget":
#     #     return self._view
#     #
#     # @View.setter
#     # def View(self, value: "QWidget"):
#     #     self._view = value
#
#
#     def __init__(self, configItem: "ConfigModelItem" = None, parent: "QWidget" = None, *args, **kwargs):
#         self.Item: "ConfigModelItem" = configItem
#         self.Parent: "QWidget" = parent
#         self.View: "QWidget" = QWidget(parent)

本 = baseClass.枚举命名
译 = Translate


@dataclass
class GViewData:
    """视图数据类
    警告:当你要修改数据类的结构时,请你务必检查所有的调用方是否正确调用了这个类
    edges的结构:
        {"from_to":{connect:True,desc:"abc"}}
    20221226之前的结构:
        nodes:{card_id:[posX,posY]}
        edges:[[card_from,card_to]]
    """

    # uuid: str
    # name: str
    # # {"card_Id":{"pos":[posx,posy],"priority":int,"accesstimes":int,"dataType":"card/view"}}
    # nodes: 'models.类型_视图结点集模型'  #
    #
    #
    # edges: 'models.类型_视图边集模型'  # 在取出时就应该保证边的唯一性,而且主要用来存json字符串,所以不用set
    # meta: "Optional[dict[str,int|None|str]]"=None
    # config: 'str' = ""
    def __init__(self, **kwargs):
        from . import funcs, models
        uuid, name, 结点集数据源, 边集数据源 = kwargs["uuid"], kwargs["name"], kwargs["nodes"], kwargs["edges"]
        if "config" in kwargs:
            config = kwargs["config"]
        else:
            config = ""
        版本20221226 = False
        卡片标识 = ""
        边标识 = ""
        for 标识 in 结点集数据源.keys():
            卡片标识 = 标识
            break

        if 卡片标识 != "" and type(结点集数据源[卡片标识]) == list and type(边集数据源) == list:
            版本20221226 = True

        self.uuid: str = uuid
        self.name: str = name
        self.config: str = config
        self.meta = funcs.GviewOperation.默认元信息模板(kwargs["meta"] if "meta" in kwargs else None)

        if not safe.funcs.GviewConfigOperation.存在(self.config):
            # safe.funcs.GviewConfigOperation.指定视图配置(self,need_save=False)
            # 视图指定新配置
            self.config_model = safe.objs.Record.GviewConfig()
            self.config = self.config_model.uuid
            gview_list:list = self.config_model.data.appliedGview.value
            gview_list.append(self.uuid)
            self.config_model.saveModelToDB()
            # self.config_model.saveModelToDB()
        else:
            # 视图读取旧配置
            self.config_model = safe.funcs.GviewConfigOperation.从数据库读(self.config)
            # 视图维护旧配置
            if self.uuid not in self.config_model.data.appliedGview.value:
                self.config_model.data.appliedGview.value.append(self.uuid)
                self.config_model.saveModelToDB()

        # if safe.funcs.GviewConfigOperation.存在(self.config):
        #     self.config_model = safe.funcs.GviewConfigOperation.从数据库读(self.config)
        # else:
        #         # safe.funcs.GviewConfigOperation.指定视图配置(self,need_save=False) # 此时还在创建中, 不需要保存
        #     config_id = safe.funcs.GviewConfigOperation.指定视图配置(self)
        #     # self.config_model = safe.objs.Record.GviewConfig()
        #     # self.config = self.config_model.uuid
        #     # self.config_model.saveModelToDB()
        #     tooltip(f"create new config:{self.config_model.name}")

        结点数据集字典 = {}
        结点数据模板 = funcs.GviewOperation.依参数确定视图结点数据类型模板()
        边数据集字典 = {}
        边数据模板 = funcs.GviewOperation.默认视图边数据模板()
        不存在的结点集 = []
        结点属性 = baseClass.枚举命名.结点
        类型 = baseClass.枚举命名.结点.数据类型
        类型值 = baseClass.视图结点类型
        if 版本20221226:
            for 标识, 位置 in 结点集数据源.items():
                结点数据集字典[标识] = funcs.GviewOperation.依参数确定视图结点数据类型模板(编号=标识)
            for 对儿 in 边集数据源:
                边数据集字典[f"{对儿[0]},{对儿[1]}"] = funcs.GviewOperation.默认视图边数据模板()
        else:

            for 标识, 值 in 结点集数据源.items():
                if 类型 not in 值:
                    if "data_type" in 值:
                        值[类型] = 值["data_type"]  # 2023.2.25版本兼容
                    else:
                        raise ValueError(f"{值}的{类型}无法确定")
                if 结点属性.角色 in 值 and type(值[结点属性.角色]) == int:  # 2023.2.28版本兼容
                    值[结点属性.角色] = [值[结点属性.角色]]

                值[结点属性.角色] = [角色位置 for 角色位置 in 值[结点属性.角色] if
                                     角色位置 in range(len(self.获取结点角色表()))]
                if (值[类型] == 类型值.卡片 and not funcs.CardOperation.exists(标识)) or (
                        值[类型] == 类型值.视图 and not funcs.GviewOperation.exists(uuid=标识)):
                    不存在的结点集.append(标识)
                    continue
                else:
                    结点数据集字典[标识] = funcs.GviewOperation.依参数确定视图结点数据类型模板(结点类型=值[类型],
                                                                                               编号=标识, 数据=值)
            for 标识, 值 in 边集数据源.items():
                a, b = 标识.split(",")
                if a in 不存在的结点集 or b in 不存在的结点集:
                    continue
                else:
                    边数据集字典[标识] = funcs.GviewOperation.默认视图边数据模板(值)

        self.nodes: "models.类型_视图结点集模型" = models.类型_视图结点集模型(self, 结点数据集字典)
        self.edges: "models.类型_视图结点集模型" = models.类型_视图边集模型(self, 边数据集字典)
        self.meta_helper: "models.类型_视图本身模型" = models.类型_视图本身模型(数据源=self)
        self.数据更新 = self.类_函数库_数据更新(self)
        self.数据获取 = self.类_函数库_获取数据(self)

    def __str__(self):
        return self.__dict__.__str__()

    def __repr__(self):
        return self.__str__()

    def 清除无效结点(self):
        from . import funcs, baseClass
        类型 = baseClass.枚举命名.结点.数据类型
        类型值 = baseClass.视图结点类型
        新数据 = self.nodes.copy()
        for 标识, 值 in self.nodes.items():
            if (值[类型] == 类型值.卡片 and not funcs.CardOperation.exists(标识)) or (
                    值[类型] == 类型值.视图 and not funcs.GviewOperation.exists(uuid=标识)):
                del 新数据[标识]
                self.删除边(标识)
        self.nodes.data = 新数据

    def copy(self, new_name=None):
        from . import funcs
        # uuid = funcs.UUID.by_random()
        return GViewData(uuid=funcs.UUID.by_random(), name=self.name if new_name is None else new_name
                         , config=self.config, edges=self.edges.copy(), nodes=self.nodes.copy(),
                         meta=self.meta.copy() if self.meta else None)

    def to_html_repr(self):
        return f"uuid={self.uuid}<br>" \
               f"name={self.name}<br>" \
               f"node_list={json.dumps(self.nodes.data, ensure_ascii=False)}<br>" \
               f"edge_list={json.dumps(self.edges.data, ensure_ascii=False)}"

    def to_DB_format(self):
        return {
            "uuid": self.uuid,
            "name": self.name,
            "nodes": f"{json.dumps(self.nodes.data, ensure_ascii=False)}",
            "edges": f"{json.dumps(self.edges.data, ensure_ascii=False)}",
            "config": self.config,
            **self.meta  # 保存时将每个字段都提出来
        }

    def 设置结点属性(self, 结点编号: str, 属性名: str, 值):
        assert type(结点编号) == str and type(属性名) == str
        self.nodes.data[结点编号][属性名] = 值

    def 获取结点描述(self, 编号, 全部内容=False):
        from . import funcs
        return funcs.GviewOperation.获取视图结点描述(self, 编号, 全部内容)


    # def 更新配置(self):

    def 获取结点角色表(self):
        if self.config:
            return eval(self.config_model.data.node_role_list.value)
        else:
            return []

    def 更新结点角色位置表(self, node_id):
        结点属性 = baseClass.枚举命名.结点
        角色表 = self.获取结点角色表()
        角色位置表 = self.nodes[node_id].角色.值
        self.nodes[node_id].角色.设值([角色位置 for 角色位置 in 角色位置表 if 角色位置 in range(0, len(角色表))])

    def __hash__(self):
        return int(self.uuid, 16)

    def __eq__(self, other):
        if isinstance(other, GViewData):
            return other.uuid == self.uuid
        elif type(other) == str:
            return other == self.uuid
        else:
            raise ValueError("未知的比较对象")

    def 新增边(self, a, b, 文字=""):
        from . import funcs, models
        a_b = f"{a},{b}"
        self.edges[a_b] = funcs.GviewOperation.默认视图边数据模板({本.边.名称: 文字})
        # self.node_helper[a_b] = models.类型_视图边模型().初始化(self, a_b)

    def 删除边(self, a=None, b=None):
        if a and b:
            a_b = f"{a},{b}"
            if a_b in self.edges:
                del self.edges[a_b]
            # if a_b in self.node_helper:
            #     del self.node_helper[a_b]
        else:
            edge_list = list(self.edges.keys())
            for a_b in edge_list:
                if a in a_b:
                    del self.edges[a_b]
                    # if a_b in self.node_helper:
                    #     del self.node_helper[a_b]

    def 新增结点(self, 编号, 类型):
        from . import funcs
        self.nodes[编号] = funcs.GviewOperation.依参数确定视图结点数据类型模板(结点类型=类型, 编号=编号)
        # self.node_helper[编号]=models.类型_视图结点模型().初始化(self,编号)

    def 删除结点(self, 编号):
        if 编号 in self.nodes:
            del self.nodes[编号]
        edge_list = list(self.edges.keys())
        for a_b in edge_list:
            if 编号 in a_b:
                del self.edges[a_b]

    def 保存(self):
        from . import funcs
        funcs.GviewOperation.save(self)

    class 类_函数库_获取数据:
        def __init__(self, 上级: "GViewData"):
            self.上级: "GViewData" = 上级

        def 获取对应边(self,node_id)->list[str]:
            return [edge.__str__() for edge in self.上级.edges if node_id in edge]


    class 类_函数库_数据更新:
        def __init__(self, 上级: "GViewData"):
            self.上级: "GViewData" = 上级

        def 保存配置数据(self, *args):
            self.上级.config_model.saveModelToDB()

        def 保存视图数据(self):
            from . import funcs
            funcs.GviewOperation.save(self.上级)

        def 视图编辑发生(self):
            self.上级.meta[本.视图.上次编辑] = (int(time.time()))
            self.保存视图数据()
            pass

        def 视图访问发生(self):
            self.上级.meta[本.视图.上次访问] = (int(time.time()))
            self.上级.meta[本.视图.访问次数] += 1
            self.保存视图数据()
            pass

        def 视图复习发生(self):
            self.上级.meta[本.视图.上次复习] = (int(time.time()))
            self.保存视图数据()

        def 结点编辑发生(self, 结点编号):
            self.上级.nodes[结点编号][本.结点.上次编辑] = (int(time.time()))
            self.保存视图数据()

        def 结点访问发生(self, 结点编号):
            self.上级.nodes[结点编号][本.结点.上次访问] = (int(time.time()))
            self.上级.nodes[结点编号][本.结点.访问次数].设值(1 + self.上级.nodes[结点编号][本.结点.访问次数].值)
            self.保存视图数据()

        def 结点复习发生(self, 结点编号):
            self.上级.nodes[结点编号][本.结点.上次复习] = (int(time.time()))
            self.保存视图数据()

        def 刷新配置模型(self):
            self.上级.config = safe.funcs.GviewOperation.load(self.上级.uuid).config
            self.上级.config_model = safe.funcs.GviewConfigOperation.从数据库读(self.上级.config)


@dataclass
class GraphMode:
    normal: int = 0
    view_mode: int = 1
    debug_mode: int = 2


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
    """TODO 将本模型和新模型相融合"""
    instruction: "List[str]"
    value: "Any"
    component: "int"
    tab_at: "str"
    hide: "bool" = False
    display: 'Callable[[Any],Any]' = lambda x: x
    validate: 'Callable[[Any,Any],Any]' = lambda value, item: None
    limit: "list" = field(default_factory=lambda: [0, MAXINT])
    customizeComponent: "Callable[[],widgets.CustomConfigItemView.__class__]" = lambda: widgets.CustomConfigItemView  # 这个组件的第一个参数必须接受
    _id: "int" = 0  # 0表示无特殊信息
    widget: "QWidget" = None
    设值到组件: "Callable[[Any],Any]" = None  # 将配置表项的值设到组件上, BaseConfig.makeConfigRow中用到, 不同的组件设置方式不同,需要在那边自定义

    def setValue(self, 值, 需要设值回到组件=True):
        """设值到配置表项"""
        self.value = 值
        if self.设值到组件 and 需要设值回到组件:
            self.设值到组件(值)

    def to_dict(self):
        return {"value": self.value}

    def __eq__(self, other):
        return self.value == other

    # def 组件类型与组件值修改函数映射(self):
    #     w= BaseConfigModel.Widget
    #     return {
    #         w.spin:lambda 值:self.widget.setValue(值),
    #         w.line:lambda 值:self.widget.setText(值),
    #     }


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
class BaseConfigModel:
    """
    为了防止以后看不懂, 说明一下用法, 这个类是定制模板, 先实例化之后再修改模板的默认值.
    """

    class 元信息:
        确定保存到数据库 = True

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
    def json_load(source):
        raise NotImplementedError("")

    @staticmethod
    def readData(fromData: "dict", ConfigModel):
        todata: dict = {}
        for k, v in fromData.items():
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

    def __repr__(self):
        d = {}
        for k, v in self.__dict__.items():
            if isinstance(v, ConfigModelItem):
                d[k] = v.value
        return d.__str__()

    def __str__(self):
        return self.__repr__()


@dataclass
class ConfigModel(BaseConfigModel):
    """

    TODO:
        翻译instruction

    """

    @staticmethod
    def json_load(path) -> "ConfigModel":
        """从path读取,立即保存到path,是因为有可能这里的版本更高级,有新功能"""
        fromdata: dict = json.load(open(path, "r", encoding="utf-8"))
        return ConfigModel.readData(fromdata, ConfigModel)

    @staticmethod
    def pdfurl_default_system_cmd():
        """因为不同的系统需要的命令不同,所以要这个东西来确定"""
        url = f"""   file:///{{{terms.PDFLink.path}}}#page={{{terms.PDFLink.page}}} """
        if isMac:
            return f'''open -a Safari "{url}" '''
        if isWin:
            return f""" start msedge "{url}" """
        return ""

    gview_admin_default_display: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
        instruction=["默认的视图管理器展示视图的方式", "The default way the Gview manager presents the Gview"],
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

    # 2023年2月16日00:13:49 暂时取消这些功能, 存在bug以后再修复
    # time_up_buzzer: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
    #         instruction=["""该项如果设为大于0的值,比如10,则在10秒后弹出提示框,提醒你已经看了10秒卡片,提示框有三个按钮可选, 取消,重新计时,继续, 第一个表示什么都不做, 第二个表示再次计时, 第三个表示执行自动操作,如果设为0,则表示关闭该功能""",
    #                      "This item if set to a value greater than 0, such as 10, then after 10 seconds pop-up box to remind you have looked at the card for 10 seconds, the alert box has three buttons to choose from, cancel, retime, continue, the first means do nothing, the second means time again, the third means the implementation of automatic operations, if set to 0, it means that the function is closed"
    #                      ],
    #         value=0,
    #         component=ConfigModel.Widget.spin,
    #         tab_at=Translate.复习相关,
    # ))
    # time_up_auto_action: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
    #         instruction=[
    #                 """该项设置复习时间到后, 选择'继续'按钮所对应的自动操作,可选以下几种自动操作:no action, again, hard, good, easy, delay 1 day, delay 3 days, delay 1 week, delay 1 month, customize delay,just show answer,其中delay表示推迟卡片, 推迟不会有复习记录, customize delay可以在时间到了后手动填写推迟天数""",
    #                 "This item sets the automatic action corresponding to the 'Continue' button when the review time is up, you can choose the following automatic actions: no action, again, hard, good, easy, delay 1 day, delay 3 days, delay 1 week, delay 1 month, customize delay, just show answer, where delay means postpone the card, there will be no review record for delay, customize delay can be filled in manually after the time has come to postpone the number of days"],
    #         value=0,
    #         component=ConfigModel.Widget.combo,
    #         limit=[ComboItem(Translate.不操作, 0), ComboItem(Translate.忘记, 1), ComboItem(Translate.困难, 2),
    #                ComboItem(Translate.良好, 3), ComboItem(Translate.简单, 4), ComboItem(Translate.延迟一天, 5),
    #                ComboItem(Translate.延迟三天, 6), ComboItem(Translate.延迟一周, 7), ComboItem(Translate.延迟一月, 8),
    #                ComboItem(Translate.自定义延迟, 9), ComboItem(Translate.显示答案, 10)],
    #         tab_at=Translate.复习相关,
    # ))
    # time_up_skip_click: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
    #         instruction=["如果你想复习时间到了, 直接跳过提示按钮选择的环节,执行自动预设操作,请勾选本项", "If you want to skip the prompt button selection and perform the automatic preset operation when the review time is up, please check this box"],
    #         value=False,
    #         component=ConfigModel.Widget.radio,
    #         tab_at=Translate.复习相关,
    # ))
    # freeze_review: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
    #         instruction=[
    #                 "开启后,当到达显示答案的状态时,会冻结复习按钮一段时间,以防止你不假思索地复习卡片",
    #                 "When turned on, the review button will freeze for a period of time when it reaches the state where the answer is displayed, to prevent you from reviewing the card without thinking."
    #         ],
    #         value=False,
    #         component=ConfigModel.Widget.radio,
    #         tab_at=Translate.复习相关
    # ))
    # freeze_review_interval: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
    #         instruction=[
    #                 "阻止你在这个时间结束之前点击复习按钮.单位毫秒",
    #                 "Prevents you from clicking the review button before this time expires. Unit milliseconds"
    #         ],
    #         value=10000,
    #         component=ConfigModel.Widget.spin,
    #         tab_at=Translate.复习相关,
    # ))
    # too_fast_warn: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
    #         instruction=[
    #                 "开启后,如果你复习间隔太快,他会提示你, 这个功能只在reviewer中有效",
    #                 "After you turn it on, if you review the interval too fast, he will prompt you, this function is only effective in the reviewer"
    #         ],
    #         value=False,
    #         component=ConfigModel.Widget.radio,
    #         tab_at=Translate.复习相关
    # ))
    # too_fast_warn_interval: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
    #         instruction=[
    #                 "提示你复习过快的最小间隔,单位是毫秒",
    #                 "The minimum interval that prompts you to review too quickly, in milliseconds"
    #         ],
    #         value=2000,
    #         component=ConfigModel.Widget.spin,
    #         tab_at=Translate.复习相关
    # ))
    # too_fast_warn_everycard: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
    #         instruction=[
    #                 "当你连续复习X张卡片,并且每两张之间的间隔均小于配置表设定的最小间隔时,才会提示你复习过快 ,这里的X, 就是本字段设定的值",
    #                 "When you review X cards in a row, and the interval between each two cards is less than the minimum interval set in the configuration table, then you will be prompted to review too fast, where X, is the value set in this field"
    #         ],
    #         value=3,
    #         component=ConfigModel.Widget.spin,
    #         tab_at=Translate.复习相关
    # ))
    # group_review: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
    #         instruction=[
    #                 "假设某个搜索条件下有多张卡,你复习其中一张卡,那么其余卡片也会用相同的选项自动进行复习,开启后,在 group_review_search_string 中输入搜索词(就像你在搜索栏中做的那样),即可对同属于这个搜索结果的卡片执行同步复习",
    #                 "Suppose there are multiple cards in a certain search condition, and you review one of them, then the rest of the cards will be reviewed automatically with the same options, and when you turn it on, enter the search term in the group_review_search_string (as you did in the search field) to perform a simultaneous review of the cards belonging to the same search result"
    #         ],
    #         value=True,
    #         component=ConfigModel.Widget.radio,
    #         tab_at=Translate.复习相关
    # ))
    #
    # group_review_comfirm_dialog: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
    #         instruction=[
    #                 "如果开启,他会在你点复习之前弹出来询问你,让你确认要群组复习的卡片, 你如果不点确定, 他就不会复习",
    #                 "English Instruction Maybe later"
    #         ],
    #         value=True,
    #         component=ConfigModel.Widget.radio,
    #         tab_at=Translate.复习相关
    # ))
    # group_review_just_due_card: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
    #         instruction=[
    #                 "如果开启,则默认排除未到期的卡,仅复习已到期的卡",
    #                 "English Instruction Maybe later"
    #         ],
    #         value=True,
    #         component=ConfigModel.Widget.radio,
    #         tab_at=Translate.复习相关
    # ))
    # group_review_global_condition: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
    #         instruction=[
    #                 "默认将一个条件加到所有复习条件上",
    #                 "English Instruction Maybe later"
    #         ],
    #         value="",
    #         component=ConfigModel.Widget.line,
    #         tab_at=Translate.复习相关
    # ))
    # group_review_search_string: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
    #         instruction=[
    #                 "这里填群组复习的条件,列表的每一项为一个完整搜索条件,如果不会填,有更简单操作,点击browser界面菜单栏->hjp_bilink->群组复习操作->保存当前搜索条件为群组复习条件,即可",
    #                 "English Instruction Maybe later"
    #         ],
    #         value=[],
    #         validate=lambda text, item:  # 这个地方要有两次不同方式的调用所以要用两个不同的判断
    #         (re.search(r"\S", text) and text not in item.value) if type(text) == str
    #         else reduce(lambda x, y: x and y, map(lambda x: re.search(r"\S", x), text), True) if type(text) == list
    #         else False,
    #         component=ConfigModel.Widget.customize,
    #         customizeComponent=lambda: widgets.GroupReviewConditionList,
    #         tab_at=Translate.复习相关
    # ))
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
        instruction=[
            "在本项设置中,你可以指定提取卡片描述的方式, 比如指定什么模板,提取哪个字段,长度多少,还可以写正则表达式, 双击单元格修改,加号按钮增加规则,减号去掉选中规则"],
        value=[baseClass.枚举命名.全局配置.描述提取规则.默认规则()],  # 模板ID,字段ID,长度限制,正则表达式,是否自动更新描述
        component=ConfigModel.Widget.customize,
        tab_at=Translate.链接相关,
        customizeComponent=lambda: widgets.DescExtractPresetTable
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
        limit=[ComboItem(Translate.文内链接, 0), ComboItem(Translate.文内链接 + "(html)", 1),
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
        value=24,
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
    PDFLink_style: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
        instruction=["PDF链接的通用css样式"],
        value="""
background-color:green;
color:white;
text-decoration:none;""",
        tab_at=Translate.pdf链接,
        component=ConfigModel.Widget.text

    ))
    PDFLink_cmd: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
        instruction=["当你点击pdf链接时,会根据如下命令执行指定的程序",
                     f"其中{terms.PDFLink.url}表示文件路径会被自动转写成file协议的url编码, {terms.PDFLink.page}代表pdf的页码",
                     f"你可以用{terms.PDFLink.path}代替{terms.PDFLink.url},{terms.PDFLink.path}表示文件路径本身,不转写成url编码格式"],
        component=ConfigModel.Widget.line,
        value=ConfigModel.pdfurl_default_system_cmd(),
        tab_at=Translate.pdf链接,
    ))
    PDFLink_pagenum_str: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
        instruction=[f"{terms.PDFLink.page}该占位符将会被替换成对应的页码"],
        value=f"|page={{{terms.PDFLink.page}}}",
        component=ConfigModel.Widget.line,
        tab_at=Translate.pdf链接,
    ))
    PDFLink_show_pagenum: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
        instruction=[
            "选中表示开启,例子: 当pdf链接显示名字为 ABC.pdf,页码显示为|page=10,则在最终插入时, 名字会变成 ABC.pdf|page=10"],
        value=True,
        component=ConfigModel.Widget.radio,
        tab_at=Translate.pdf链接,
    ))

    PDFLink_presets: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
        instruction=["遇到指定路径的pdf,提供预先设置好的显示名称,样式, 是否显示页码,双击左侧表格单元修改对应行内容"],
        value=[],
        component=ConfigModel.Widget.customize,
        customizeComponent=lambda: widgets.PDFUrlLinkBooklist,
        tab_at=Translate.pdf链接,
    ))
    set_default_view: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
        instruction=[译.说明_设定默认视图],
        value=-1,
        component=ConfigModel.Widget.customize,
        customizeComponent=lambda: widgets.GlobalConfigDefaultViewChooser,
        tab_at="view"
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


@dataclass
class GviewConfigModel(BaseConfigModel):
    @staticmethod
    def json_load(source: "dict"):
        """"""
        template = GviewConfigModel()
        for k, v in source.items():
            template[k].value = v
        return template

    @staticmethod
    def ViewExist(uuid):
        from . import funcs
        return funcs.GviewOperation.exists(uuid=uuid)

    uuid: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
        instruction=["只读"],
        value="",
        component=ConfigModel.Widget.none,
        tab_at="main",
    ))
    name: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
        instruction=["本项设定次此视图配置的名字"],
        value="",
        component=ConfigModel.Widget.line,
        tab_at="main",
        validate=lambda value, item: re.search(r"\S", value)
    ))
    roaming_sidebar_hide: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
        instruction=[译.说明_漫游复习侧边栏收起],
        value=True,
        component=ConfigModel.Widget.radio,
        tab_at="main"
    ))

    roamingStart: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
        instruction=["本项设定漫游的起点"],
        value=1,
        component=ConfigModel.Widget.combo,
        tab_at="roaming",
        limit=[ComboItem(Translate.随机选择卡片开始, 0), ComboItem(Translate.手动选择卡片开始, 1), ]
    ))
    # groupReview: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
    #         instruction=["本项设定是否对使用本配置的视图开启群组复习,提示:开启群组复习后,最好就别再使用漫游复习,因为会一下子复习掉所有卡片,毫无漫游的意义"],
    #         value=False,
    #         component=ConfigModel.Widget.radio,
    #         tab_at="main",
    #
    # ))

    appliedGview: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
        instruction=[
            "本项设定本配置表所应用的视图们, 如果你删掉了表中的全部视图, 那么会导致该配置被删除, 并且为当前的视图立即新建一个配置"],
        value=[],
        tab_at="main",
        component=ConfigModel.Widget.customize,
        customizeComponent=lambda: widgets.GviewConfigApplyTable,
        validate=lambda value, item: sum([0 if GviewConfigModel.ViewExist(uuid) else 1 for uuid in value]) == 0
    ))
    node_role_list: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
        instruction=[译.说明_结点角色枚举],
        tab_at="main",
        value="[]",  # "list[str]"
        validate=lambda value, item: Validation.node_tag_enum_validate(value, item),
        component=ConfigModel.Widget.customize,
        customizeComponent=lambda: widgets.GviewConfigNodeRoleEnumEditor,
    ))
    edge_name_always_show: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
        instruction=[译.说明_总是显示边名],
        tab_at="main",
        value=False,  # deck_id
        component=ConfigModel.Widget.radio,
    ))
    # view_node_inherit_config: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
    #     instruction=[译.说明_视图结点创建默认配置],
    #     tab_at="main",
    #     value=False,
    #     component=ConfigModel.Widget.radio,
    #
    # ))

    split_screen_when_roaming: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
        instruction=[译.说明_漫游复习时分屏],
        tab_at="main",
        value=True,
        component=ConfigModel.Widget.radio,

    ))

    default_deck_for_add_card: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
        instruction=[译.说明_新增卡片指定存放牌组],
        tab_at="main",
        value=-1,
        component=ConfigModel.Widget.customize,
        customizeComponent=lambda: widgets.GviewConfigDeckChooser,
    ))
    default_template_for_add_card: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
        instruction=[译.说明_视图添加卡片_默认模板],
        tab_at="main",
        value=-1,  # 本项要么None要么数字
        component=ConfigModel.Widget.customize,
        customizeComponent=lambda: widgets.GviewConfigTemplateChooser,
    ))
    default_config_for_add_view: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
        instruction=[译.说明_视图添加视图_默认配置],
        tab_at="main",
        value="",  # 本项要么None要么数字
        component=ConfigModel.Widget.customize,
        customizeComponent=lambda: widgets.GviewConfigViewConfigChooser,
    ))
    roaming_path_mode: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
        instruction=[译.说明_漫游路径算法选择],
        tab_at="roaming",
        value=0,
        component=ConfigModel.Widget.combo,
        limit=[ComboItem("random_sort", 0), ComboItem("cascading_sort", 1), ComboItem("weighted_sort", 2),
               ComboItem("graph_sort", 3)]
    ))
    roaming_node_filter: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
        instruction=[译.说明_漫游路径过滤],
        tab_at="roaming",
        value=[[], -1],  # excutable string list
        component=ConfigModel.Widget.customize,
        customizeComponent=lambda: widgets.GviewConfigNodeFilter
    ))
    cascading_sort: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
        instruction=[译.说明_多级排序],
        tab_at="roaming",
        value=[[], -1],  # excutable string list
        component=ConfigModel.Widget.customize,
        customizeComponent=lambda: widgets.GviewConfigCascadingSorter
    ))
    weighted_sort: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
        instruction=[译.说明_加权排序],
        tab_at="roaming",
        value=[[], -1],  # excutable string list
        component=ConfigModel.Widget.customize,
        customizeComponent=lambda: widgets.GviewConfigWeightedSorter
    ))
    graph_sort: ConfigModelItem = field(default_factory=lambda: ConfigModelItem(
        instruction=[译.说明_图排序],
        tab_at="roaming",
        value=0,  # excutable string list
        component=ConfigModel.Widget.combo,
        limit=[ComboItem(译.深度优先遍历, 0), ComboItem(译.广度优先遍历, 1)]
    ))

    def __repr__(self):
        d = {}
        for k, v in self.__dict__.items():
            if isinstance(v, ConfigModelItem):
                d[k] = v.value
        return d.__str__()

    def __str__(self):
        return self.__repr__()

        pass


class Validation:
    @staticmethod
    def node_tag_enum_validate(value: str, item: ConfigModelItem):
        from ast import literal_eval
        try:
            new_value: list = literal_eval(value)
            if type(new_value) != list:
                return False
            else:
                if len(new_value) != 0:
                    for el in new_value:
                        if type(el) != "str":
                            return False
                return True
        except:
            return False


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
