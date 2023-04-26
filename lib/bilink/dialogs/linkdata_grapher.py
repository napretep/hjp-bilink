# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'linkdata_grapher.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2021/8/10 21:18'


"""
import datetime
import json
import math
import random
import re
import sys
import time
from dataclasses import dataclass, field

import typing
from enum import Enum, unique
from typing import Optional, Union

import aqt

from ..imports import *

from aqt.utils import showInfo, tooltip

from ..linkdata_admin import read_card_link_info

if __name__ == "__main__":
    from lib import common_tools

    pass
else:
    from ..imports import common_tools

import collections

LinkDataPair = common_tools.objs.LinkDataPair
GraphMode = common_tools.configsModel.GraphMode
GViewData = common_tools.configsModel.GViewData
GviewConfigModel = common_tools.configsModel.GviewConfigModel
GviewConfig = common_tools.objs.Record.GviewConfig
译 = Translate = common_tools.language.Translate
Struct = common_tools.objs.Struct
funcs = common_tools.funcs
funcs2 = common_tools.funcs2
src = common_tools.G.src
models = common_tools.models
本 = common_tools.baseClass.枚举命名
枚举_视图结点类型 = common_tools.baseClass.视图结点类型
VisualBilinker = common_tools.graphical_bilinker.VisualBilinker


class 安全导入():
    @property
    def SingleCardPreviewer(self):
        from .custom_cardwindow import SingleCardPreviewer
        return SingleCardPreviewer


load = 安全导入()


class Grapher(QMainWindow):
    """所有的个性化数据都储存在Entity对象中
    启动grapher的方式, 1 临时视图, 此时不需要边名, 直接禁用, 2 普通视图, 此时可以用边名,
    普通视图可以是读取的, 也可以是新建的,
    TODO 2023年2月25日15:24:28
        1 写一个放大缩小的功能 2 写一个搜索卡片的功能 3 写一个批量修改卡片属性的功能, 4结点要提供一个属性重置按钮
    """
    on_card_updated = pyqtSignal(object)

    def __init__(self,
                 pair_li: "list[LinkDataPair]" = None,  # 直接导入卡片描述对儿
                 gviewdata: "GViewData" = None,  # 读取已经保存过的视图数据
                 mode=GraphMode.view_mode, ):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, on=True)
        self.data = self.Entity(self)
        self.data.gviewdata = gviewdata
        if not funcs.GviewConfigOperation.存在(gviewdata.config):
            funcs.GviewConfigOperation.指定视图配置(gviewdata)
        # self.data.gview_config = funcs.GviewConfigOperation.从数据库读(gviewdata.config)
        self.data.graph_mode = mode
        self.view = self.View(self)
        self.scene = self.Scene(self)
        self.view.setScene(self.scene)
        self.roaming: "Optional[GrapherRoamingPreviewer]" = None  # roaming是个窗口

        self.toolbar = self.ToolBar(self)

        r = self.rect()
        self.scene.setSceneRect(-float(r.width() / 2), -float(r.height() / 2), float(r.width() * 4),
                                float(r.height() * 4))
        self.init_UI()
        self.all_event = common_tools.objs.AllEventAdmin([
                [self.scene.selectionChanged, self.on_scene_selectionChanged_handle],
                [self.view.verticalScrollBar().valueChanged, self.on_view_verticalScrollBar_valueChanged_handle],
                [self.view.horizontalScrollBar().valueChanged, self.on_view_horizontalScrollBar_valueChanged_handle],
                [self.on_card_updated, self.on_card_updated_handle],
                # [self.on_card_reviewed, lambda card_id : if card_id in self.data.node_dict.keys(): self.data.updateNodeDue() else None]
        ]).bind()
        self.init_graph_item()
        self.data.gviewdata.数据更新.视图访问发生()
        QShortcut(Qt.Key.Key_Delete, self).activated.connect(self.toolbar.deleteItem)
        QShortcut(Qt.Key.Key_F2,self).activated.connect(self.toolbar.node_property_editor)

    def 自身属性查看器(self):
        self.data.gviewdata.meta_helper.创建UI(funcs.组件定制.对话窗口(标题="info of view", 最大宽度=600)).exec()

    def 批量结点属性编辑器(self, 结点列表: "list[str]"):
        models.类型_集模型_批量视图结点(结点列表, self.data.gviewdata, self.data.gviewdata.nodes.data).创建UI().exec()

    def 结点属性查看器(self, node_items: "list[Grapher.ItemRect]", edge_items: "list[Grapher.ItemEdge]"):
        if node_items:
            if len(node_items) == 1:
                self.data.gviewdata.nodes[node_items[0].索引].创建UI(funcs.组件定制.对话窗口(标题="info of node")).exec()
            else:
                self.批量结点属性编辑器([item.索引 for item in node_items])
        elif edge_items:
            self.边属性查看器(edge_items[0])
        self.data.node_edge_packup()
        pass

    def 边属性查看器(self, item: "Grapher.ItemEdge"):
        开始, 结束 = item.获取关联的结点()
        边名 = self.data.gviewdata.edges[f"{开始},{结束}"].边名.值
        text, okPressed = common_tools.compatible_import.QInputDialog.getText(self, "get new description for the edge", "", text=边名)
        if okPressed:
            # funcs.Utils.print(self.data.gviewdata.edge_helper.keys())
            self.data.gviewdata.edges[f"{开始},{结束}"].边名.设值(text)
            # self.data.gviewdata.edges[f"{开始},{结束}"][本.边.名称]=text
        pass

    def on_card_updated_handle(self, event):
        pass
        # for node in self.data.node_dict.values():
        #     node.pair.update_desc()
        #     node.item.pair.update_desc()

    def on_view_verticalScrollBar_valueChanged_handle(self, value):
        # x,y=self.scene.items()[0].pos().x(),self.scene.items()[0].pos().y()
        # tooltip(f"x={x},y={y}")
        rect = self.view.sceneRect()
        if value > self.view.verticalScrollBar().maximum() - 10:
            rect.setBottom(rect.bottom() + 50)
        elif value == self.view.verticalScrollBar().minimum():
            rect.setTop(rect.top() - 50)
        self.view.setSceneRect(rect)
        pass

    def on_view_horizontalScrollBar_valueChanged_handle(self, value):
        rect = self.view.sceneRect()
        if value > self.view.horizontalScrollBar().maximum() - 40:
            rect.setRight(rect.right() + 50)
        elif value <= self.view.horizontalScrollBar().minimum() + 10:
            rect.setLeft(rect.left() - 50)
        self.view.setSceneRect(rect)
        pass

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:

        self.data.node_edge_packup()

        if self.roaming:
            self.roaming.close()

        # common_tools.funcs.GviewOperation.更新缓存(视图=self.data.gviewdata.uuid)
        # common_tools.funcs.Utils.print("当前关闭时的视图对象",self.data.gviewdata)
        common_tools.G.mw_gview[self.data.gviewdata.uuid] = None
            # common_tools.G.GViewAdmin_window

    def close(self):
        self.scene.blockSignals(True)
        super().close()

    def reject(self) -> None:
        self.close()
        super().reject()

    def on_scene_selectionChanged_handle(self):
        self.update_edge_highlight()

    def create_view(self):
        """根据当前视图的情况,创建一个新的视图"""
        # name, submitted = funcs.GviewOperation.get_correct_view_name_input()
        # if not submitted: return
        # self.data.node_edge_packup()
        # common_tools.funcs.Dialogs.open_grapher(gviewdata=self.data.gviewdata.copy(new_name=name), mode=funcs.GraphMode.view_mode)
        self.data.node_edge_packup()
        config = None
        config_id = self.data.gviewdata.config_model.data.default_config_for_add_view.value
        if funcs.GviewConfigOperation.存在(config_id):
            config = config_id
        自身数据 = self.data.gviewdata
        视图 = common_tools.funcs.GviewOperation.create(
            nodes=自身数据.nodes.data.copy(),
            edges=自身数据.edges.data.copy(),
            meta =自身数据.meta.copy(),
            config=config)
        if 视图:
            视图.保存()
    # node
    def create_node(self, pair: "LinkDataPair|str", 参数_视图结点类型=枚举_视图结点类型.卡片, fromGviewData=False):
        """
        create_node 只是单纯地添加, 不会对位置作修改,
        如果你没有位置数据,那就调用默认的 arrange_node函数来排版位置
        如果你有位置数据, 那就用 item自己的setPos
        注意, create_node, 添加的是view中的图形结点, 请在外部完成gviewdata中数据的添加.
        """
        node_id = pair if type(pair) == str else pair.card_id
        item = self.ItemRect(self, node_id, 参数_视图结点类型)
        self.scene.addItem(item)
        self.data.add_to_node_data(item, fromGviewData)
        return item

    def load_node(self, pair_li: "list[LinkDataPair|str|GViewData|None]", begin_item=None, selected_as_center=True, 参数_视图结点类型=枚举_视图结点类型.卡片, from_outside=True):
        """ """
        if pair_li is None:
            return
        item_li = []
        last_item = None

        if len(self.data.node_dict) > 0:
            last_item = self.data.node_dict[(list(self.data.node_dict.keys())[-1])].item
        for pair in pair_li:
            card_id: "str" = pair if type(pair) == str else pair.card_id if isinstance(pair, LinkDataPair) else pair.uuid
            if card_id in self.data.gviewdata.nodes:
                continue
            else:
                self.data.node_dict[card_id] = self.data.Node(card_id)
                item = self.create_node(card_id, 参数_视图结点类型)  # 我就单纯读
                item_li.append(card_id)
                if begin_item:
                    self.arrange_node(item, begin_item)
                elif selected_as_center:
                    self.arrange_node(item)
                else:
                    self.arrange_node(item, last_item)
                    begin_item = item
                last_item = item
        if last_item:
            self.view.centerOn(item=last_item)
            self.scene.clearSelection()
            last_item.setSelected(True)
        self.data.node_edge_packup()
        self.data.updateNodeDueAll()

    def add_edge(self, card_idA: "str", card_idB: "str", fromGviewData=False):
        """A->B, 反过来不成立
        add_bilink 用来判断是否要修改全局链接.
        """
        nodeA = self.data.node_dict[card_idA]
        nodeB = self.data.node_dict[card_idB]
        edgeItem = self.ItemEdge(self, nodeA.item, nodeB.item)
        self.scene.addItem(edgeItem)
        self.data.add_to_edge_data(edgeItem, fromGviewData)

        return edgeItem
        pass

    def remove_edge(self, card_idA=None, card_idB=None):
        """
        """
        edge = self.data.edge_dict[card_idA][card_idB]
        a, b = edge.item.获取关联的结点()
        edge.item.hide()
        self.scene.removeItem(edge.item)
        self.data.remove_from_edge_data(a, b)
        pass

    # bilink
    def remove_node(self, item: "Grapher.ItemRect|str"):
        """"""
        if type(item) == str:
            item = self.data.node_dict[item].item
        node_id = item.索引
        for edge in item.node.edges:
            self.scene.removeItem(edge.item)
        for edge in item.node.inver_edges:
            self.scene.removeItem(edge.item)
        self.scene.removeItem(item)
        self.data.remove_from_node_data(item.索引)

    def remove_many_nodes(self, items: "list[Grapher.ItemRect]"):
        for item in items:
            self.remove_node(item)

    def arrange_node(self, new_item: "Grapher.ItemRect", center_item=None):
        def get_random_p(center_item, radius, part):
            total = radius / self.data.default_radius * 6
            a_part = 360 / total
            angle = (part * a_part) / 180 * math.pi
            x, y = math.cos(angle) * radius, math.sin(angle) * radius
            center_p = center_item.pos() if center_item else QPointF(0, 0)
            p = center_p + QPointF(x, y)
            return p

        if center_item is None and len(self.data.node_dict) > 0:
            if self.selected_nodes():
                center_item = self.selected_nodes()[0]
                # tooltip("center_item = selected nodes")
            else:
                center_id = list(self.data.node_dict.keys())[0]
                center_item = self.data.node_dict[center_id].item
        if new_item == center_item:
            return
        radius = self.data.default_radius
        count = 0
        while True:
            new_item.setPos(get_random_p(center_item, radius, count))
            if new_item.collidingItems():
                print("重叠")
            else:
                break
            count += 1
            if count == 6 * radius / self.data.default_radius:
                radius += self.data.default_radius
                count = 0

    def selected_nodes(self):
        item_li: "list[Grapher.ItemRect]" = [item for item in self.scene.selectedItems() if isinstance(item, Grapher.ItemRect)]

        return item_li

    def selected_edges(self):
        item_li: "list[Grapher.ItemEdge]" = [item for item in self.scene.selectedItems() if isinstance(item, Grapher.ItemEdge)]

        return item_li

    def update_all_edges_posi(self):
        updated = set()

        for card_idA, card_idB_dict in self.data.edge_dict.items():
            for card_idB, edge in card_idB_dict.items():
                if edge is not None and f"{card_idA},{card_idB}" not in updated:
                    edge.item.update_line()
                    updated.add(f"{card_idA},{card_idB}")

    def update_edge_highlight(self):
        for a_b in self.data.gviewdata.edges:
            a, b = a_b.split(",")
            # funcs.Utils.print(a,b)
            if a in self.data.edge_dict and b in self.data.edge_dict[a]:
                self.data.edge_dict[a][b].item.unhighlight()
        node_id_li: "list[str]" = [item.索引 for item in self.selected_nodes()]
        for node_id in node_id_li:
            edges = self.data.node_dict[node_id].edges
            for edge in edges:
                edge.item.highlight()

    # init

    def init_graph_item(self, need_centerOn=True):
        """用于初始化"""
        last_item = None

        for 结点编号 in self.data.gviewdata.nodes.keys():
            结点数据 = self.data.gviewdata.nodes[结点编号]
            item = self.create_node(结点编号, 结点数据.数据类型.值, fromGviewData=True)
            if 结点数据.位置.值:
                item.setPos(*结点数据.位置.值)
            else:
                self.arrange_node(item)
            last_item = item
        for cardA_cardB in self.data.gviewdata.edges.keys():
            cardA, cardB = cardA_cardB.split(",")
            item = self.add_edge(cardA, cardB, fromGviewData=True)

        if last_item and need_centerOn:
            self.update_all_edges_posi()
            # last_item.setSelected(True)
            self.view.centerOn(item=last_item)

    def init_UI(self):
        if self.data.graph_mode == GraphMode.view_mode:
            self.setWindowTitle("view of " + self.data.gviewdata.name)
        self.setWindowIcon(QIcon(common_tools.G.src.ImgDir.link2))
        self.setWindowFlags(Qt.WindowType.WindowMinMaxButtonsHint | Qt.WindowType.WindowCloseButtonHint)

        self.resize(800, 600)
        # Hbox = QHBoxLayout(self)
        # Hbox.setContentsMargins(0, 0, 0, 0)
        # Hbox.addWidget(self.view)
        # self.setLayout(Hbox)
        self.setCentralWidget(self.view)
        self.addToolBar(self.toolbar)

        self.scene.selectionChanged.connect(self.toolbar.checkAction)

        pass

    # def saveAsGroupReviewCondition(self):
    #
    #     common_tools.funcs.GroupReview.saveGViewAsGroupReviewCondition(self.data.gviewdata.uuid)

    def 结点访问记录更新(self, 索引):
        self.data.gviewdata.nodes[索引][本.结点.访问次数] += 1
        self.data.gviewdata.nodes[索引][本.结点.上次访问] = int(time.time())
        self.data.node_edge_packup()

    # class

    def 结点编辑记录更新(self, 索引):
        self.data.gviewdata.nodes[索引][本.结点.上次编辑] = int(time.time())
        self.data.node_edge_packup()

    class Entity:

        """Entity的价值在于把数据独立出来,itemrect和itemedge只用管展示的部分, 数据保存在entity中"""
        default_radius = 180
        default_rect = QRectF(0, 0, 150, 100)

        def __init__(self, superior: "Grapher"):
            self.superior = superior
            self.root = superior
            self.graph_mode = GraphMode.view_mode
            self.gviewdata: Optional[GViewData] = None
            # self.gview_config: "Optional[GviewConfig]" = None
            self._node_dict: "Optional[dict[str,Optional[Grapher.Entity.Node]]]" = {}
            self._edge_dict: "Optional[dict[str,dict[str,Optional[Grapher.Entity.Edge]]]]" = {}
            self.currentSelectedEdge: "list[Grapher.ItemEdge]" = []
            self.state = Grapher.Entity.State()
            self.inverse_edge = self.InverseEdge()  # 反向表

        @property
        def node_dict(self) -> 'dict[str,Grapher.Entity.Node]':
            return self._node_dict

        @node_dict.setter
        def node_dict(self, 索引表: "list[str|LinkDataPair]"):
            """node_dict是用来保存视图UI上的图元数据,和gviewdata的对象无关"""
            if not 索引表:
                return
            if isinstance(索引表[0], LinkDataPair):
                for pair in 索引表:
                    self._node_dict[pair.card_id] = self.Node(pair.card_id)
            else:
                for 索引 in 索引表:
                    self._node_dict[索引] = self.Node(索引)
            if not common_tools.G.ISLOCALDEBUG:
                self.updateNodeDueAll()

        def updateNodeDue(self, card_id):
            last_, next_ = funcs.CardOperation.getLastNextRev(card_id)
            self.node_dict[card_id].due = next_ <= datetime.datetime.now()

        def updateNodeDueAll(self):
            for card_id in self.gviewdata.nodes.keys():

                if self.gviewdata.nodes[card_id][本.结点.数据类型].值 == 枚举_视图结点类型.卡片:
                    self.updateNodeDue(card_id)

        @property
        def edge_dict(self) -> 'dict[str,dict[str,Optional[Grapher.Entity.Edge]]]':
            return self._edge_dict

        def node_edge_packup(self):
            """
            这是为了获取边与顶点的最新信息, 然后打包存储
            """
            for node_id, nodeinfo in self.node_dict.items():
                self.gviewdata.nodes[node_id].位置.设值(nodeinfo.item.获取保存用的位置())
            # def get_edgeinfo_list():
            #     for cardA in self.edge_dict.keys():
            #         for cardB in self.edge_dict[cardA].keys():
            #             边 = f"{cardA},{cardB}"
            #             self.gviewdata.edge_helper[边].边名.设值(self.edge_dict[cardA][cardB].描述)

            # def get_nodeinfo_list():
            #     d = {}
            #     新结点集 = self.gviewdata.nodes.copy()
            #     for 索引, 值 in self.node_dict.items():
            #         if 索引 in 新结点集:
            #             if 本.结点.位置 not in 新结点集[索引]:
            #                 新结点集[索引][本.结点.位置] = {}
            #             新结点集[索引][本.结点.位置] = [值.item.scenePos().x(), 值.item.scenePos().y()]
            #         else:
            #             新结点集[索引] = {本.结点.位置  : [值.item.scenePos().x(), 值.item.scenePos().y()],
            #                         本.结点.数据类型: 值.item.结点类型()
            #                         }
            #     for 索引 in self.gviewdata.nodes.keys():
            #         if 索引 not in self.node_dict:
            #             del 新结点集[索引]
            #     self.gviewdata.nodes = 新结点集.copy()

            # def 备份视图元信息():
            #     self.gviewdata.meta = funcs.GviewOperation.默认元信息模板(self.gviewdata.meta)
            # self.gviewdata.meta = funcs.GviewOperation.默认元信息模板(self.gviewdata.meta)

            # 备份视图元信息()
            # get_nodeinfo_list()
            # get_edgeinfo_list()
            funcs.GviewOperation.save(self.gviewdata)
            # return node_info_list, edge_info_list
            # showInfo(self.gviewdata.meta.__str__())

        def remove_from_node_data(self, node_id):
            node = self.node_dict[node_id]
            for edge in node.edges.copy():
                node.edges.remove(edge)
                self.node_dict[edge.nodes[1].索引].inver_edges.remove(edge)
            for edge in node.inver_edges.copy():
                node.inver_edges.remove(edge)
                self.node_dict[edge.nodes[0].索引].edges.remove(edge)
            del self.node_dict[node_id]
            self.gviewdata.删除结点(node_id)

        def remove_from_edge_data(self, a: "str", b: "str"):
            edge = self.edge_dict[a][b]
            if a in self.node_dict:
                self.node_dict[a].edges.remove(edge)
            if b in self.node_dict:
                self.node_dict[b].inver_edges.remove(edge)
            del self.edge_dict[a][b]
            del self.inverse_edge[a, b]
            self.gviewdata.删除边(a, b)

        def add_to_node_data(self, item: "Grapher.ItemRect", fromGviewData=False):
            self.node_dict[item.索引] = self.Node(item.索引, item=item)
            if not fromGviewData:
                self.gviewdata.新增结点(item.索引, item.结点类型)

        def add_to_edge_data(self, item: "Grapher.ItemEdge", fromGviewData=False):
            a, b = item.itemStart, item.itemEnd
            if a.索引 not in self.edge_dict:
                self.edge_dict[a.索引] = {}
            self.edge_dict[a.索引][b.索引] = self.Edge(item, [a, b])

            self.inverse_edge[a.索引, b.索引] = self.edge_dict[a.索引][b.索引]
            self.node_dict[a.索引].edges.append(self.edge_dict[a.索引][b.索引])
            self.node_dict[b.索引].inver_edges.append(self.edge_dict[a.索引][b.索引])
            if not fromGviewData:
                self.gviewdata.新增边(a.索引, b.索引)

        @dataclass
        class Node:
            "一个node就是一个结点, 他有图形表示的item, 和数据表示的pair"
            # pair: "LinkDataPair"
            索引: "str"
            due: bool = False
            item: "Optional[Grapher.ItemRect]" = None
            edges: "list[Grapher.Entity.Edge]" = field(default_factory=list)

            def __init__(self, 索引: "str|LinkDataPair", due=False, item=None, edges=None, inver_edges=None):
                self.索引 = 索引 if type(索引) == str else 索引.card_id
                self.due = due
                self.item = item
                self.edges: "list[Grapher.Entity.Edge]" = [] if edges is None else edges
                self.inver_edges: "list[Grapher.Entity.Edge]" = [] if inver_edges is None else inver_edges

        @dataclass
        class Edge:
            item: "Grapher.ItemEdge" = None
            nodes: "list[Grapher.Entity.Node]" = None
            描述: "str" = ""

            def as_card(self) -> 'set':
                return set([int(item.索引) for item in self.nodes])

            def __str__(self):
                return self.描述

            def __repr__(self):
                return self.描述

        @dataclass
        class State:
            mouseIsMoving: bool = False
            mouseIsMovingAndRightClicked: bool = False
            mouseIsMovingAndLeftClicked: bool = False
            mouseRightClicked: bool = False
            mouseLeftClicked: bool = False

        class InverseEdge:
            """
            输入以正向输入, 查询以反向查询
            """

            def __init__(self):
                self.反查表: "dict[str,dict[str,Grapher.Entity.Edge]]" = {}

            def __getitem__(self, item):

                if type(item) != tuple:
                    if item in self.反查表:
                        return self.反查表[item]
                    else:
                        return {}
                else:
                    if item[0] in self.反查表 and item[1] in self.反查表[item[0]]:
                        return self.反查表[item[0]][item[1]]
                    else:
                        return None

            def __setitem__(self, key, value):
                A, B = key
                if B not in self.反查表:
                    self.反查表[B] = {}
                self.反查表[B][A] = value

            def __delitem__(self, key):
                """删除以正向删除"""
                if type(key) == tuple:
                    if key[1] in self.反查表 and key[0] in self.反查表[key[1]]:
                        del self.反查表[key[1]][key[0]]
                else:
                    raise TypeError("key must be tuple")
                pass

    class View(QGraphicsView):
        def __init__(self, parent: "Grapher"):
            super().__init__(parent)
            self.ratio = 1
            self.superior: "Grapher" = parent
            self.setDragMode(common_tools.compatible_import.DragMode.ScrollHandDrag)
            self.setRenderHints(QPainter.RenderHint.Antialiasing |  # 抗锯齿
                                QPainter.RenderHint.LosslessImageRendering |  # 高精度抗锯齿
                                QPainter.RenderHint.SmoothPixmapTransform)  # 平滑过渡 渲染设定
            self.setViewportUpdateMode(common_tools.compatible_import.ViewportUpdateMode.FullViewportUpdate)
            self.Auxiliary_line: "Optional[QGraphicsLineItem]" = common_tools.baseClass.Geometry.ArrowLine()
            self.Auxiliary_line.setZValue(-1)
            self.Auxiliary_line.setPen(Grapher.ItemEdge.normal_pen)
            self.clicked_pos: "Optional[QPointF]" = None
            self.draw_line_start_item: "Optional[Grapher.ItemRect]" = None
            self.draw_line_end_item: "Optional[Grapher.ItemRect]" = None

        def centerOn(self, pos: "Union[QPoint]" = None, item: "QGraphicsItem" = None):
            """居中显示"""
            assert pos is not None or item is not None
            if pos is None:
                x, y, r, b = item.boundingRect().left(), item.boundingRect().top(), item.boundingRect().right(), item.boundingRect().bottom()

                pos = item.mapToScene(int((x + r) / 2), int((y + b) / 2)).toPoint()
            curr_view_center = self.mapToScene(int(self.viewport().width() / 2),
                                               int(self.viewport().height() / 2)).toPoint()
            dp = pos - curr_view_center
            self.safeScroll(dp.x(), dp.y())

        def safeScroll(self, x, y):
            """遇到边界会扩大scene"""
            x_scroll = self.horizontalScrollBar()
            y_scroll = self.verticalScrollBar()
            rect = self.sceneRect()
            if x_scroll.value() + x > x_scroll.maximum():
                rect.setRight(rect.right() + x)
                # self.setSceneRect(rect.x(),rect.y(),rect.width()+x,rect.height())
            if x_scroll.value() + x < x_scroll.minimum():
                rect.setLeft(rect.left() + x)
                # self.setSceneRect(rect.x()+x, rect.y(), rect.width() + x, rect.height())
            if y_scroll.value() + y > y_scroll.maximum():
                # self.setSceneRect(rect.x(),rect.y(),rect.width(),rect.height()+y)
                rect.setBottom(rect.bottom() + y)
            if y_scroll.value() + y < y_scroll.minimum():
                rect.setTop(rect.top() + y)
                # self.setSceneRect(rect.x(),rect.y()+y,rect.width(),rect.height())
            self.setSceneRect(rect)
            x_scroll.setValue(x_scroll.value() + x)
            y_scroll.setValue(y_scroll.value() + y)

        def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
            if event.buttons() == Qt.MouseButton.LeftButton:
                self.superior.data.state.mouseIsMovingAndLeftClicked = True
                if self.superior.scene.selectedItems() and self.itemAt(event.pos()):
                    # self.superior.update_all_edges_posi()
                    pass
                if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                    choose1 = len(self.superior.scene.selectedItems()) == 1
                    if isinstance(self.draw_line_start_item, Grapher.ItemRect) and choose1:
                        self.moveLine(event.pos())
                        # self.draw_line_end_item = self.itemAt(event.pos())
                        # line = self.Auxiliary_line.line()
                        # p1 = line.p1()  # self.draw_line_start_item.mapToScene(self.draw_line_start_item.rect().center())
                        # p2 = self.mapToScene(event.pos())
                        # rect = self.draw_line_start_item.mapRectToScene(self.draw_line_start_item.rect())
                        # line.setP2(p2)
                        # line.setP1(p1)
                        # self.Auxiliary_line.setLine(line)
                        # print(f"p1={p1}")
                        return
            elif event.buttons() == Qt.MouseButton.RightButton:
                self.superior.data.state.mouseIsMovingAndRightClicked = True
            super().mouseMoveEvent(event)

        def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:

            # if self.itemAt(event.pos()) is None:
            #     self.clearSelection()
            if event.buttons() == Qt.MouseButton.LeftButton:
                self.superior.data.state.mouseLeftClicked = True
                self.superior.data.state.mouseRightClicked = False
                if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                    select_1 = len(self.superior.scene.selectedItems()) == 1
                    if isinstance(self.itemAt(event.pos()), Grapher.ItemRect) and select_1:
                        self.startLine(event.pos())
                        # self.draw_line_start_item: "Grapher.ItemRect" = self.itemAt(event.pos())
                        # startItemCenter = self.draw_line_start_item.mapToScene(self.draw_line_start_item.rect().center())
                        # self.Auxiliary_line.setLine(QLineF(startItemCenter, startItemCenter))
                        # # print(self.Auxiliary_line.line().p1())
                        # self.superior.scene.addItem(self.Auxiliary_line)
            elif event.buttons() == Qt.MouseButton.RightButton:
                self.superior.data.state.mouseLeftClicked = False
                self.superior.data.state.mouseRightClicked = True
                self.setDragMode(common_tools.compatible_import.DragMode.RubberBandDrag)
                pass

            # if event.buttons() == Qt.MouseButton.RightButton:

            super().mousePressEvent(event)

        def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
            # self.superior.scene.removeItem(self.Auxiliary_line)
            # end_item, begin_item = self.draw_line_end_item, self.draw_line_start_item
            # if isinstance(end_item, Grapher.ItemRect) and begin_item != end_item:
            #     add_bilink = self.superior.data.graph_mode == GraphMode.normal
            #     self.superior.add_edge(begin_item.pair.card_id, end_item.pair.card_id, add_bilink=add_bilink)
            self.makeLine()
            if not self.itemAt(event.pos()) \
                    and not self.superior.data.state.mouseIsMovingAndLeftClicked \
                    and not self.superior.data.state.mouseIsMovingAndRightClicked \
                    and event.button() == Qt.MouseButton.RightButton:  # and not self.superior.data.mouse_moved and event.button()==Qt.MouseButton.RightButton:# and self.superior.data.mouse_right_clicked:
                self.make_context_menu(event)
            self.draw_line_end_item, self.draw_line_start_item = None, None
            super().mouseReleaseEvent(event)
            self.setDragMode(common_tools.compatible_import.DragMode.ScrollHandDrag)
            self.superior.update()
            self.superior.data.state.mouseLeftClicked = False
            self.superior.data.state.mouseRightClicked = False
            self.superior.data.state.mouseIsMovingAndLeftClicked = False
            self.superior.data.state.mouseIsMovingAndRightClicked = False
            选中结点 = self.superior.selected_nodes()
            if 选中结点:
                for 结点 in 选中结点:
                    for 边 in 结点.node.edges:
                        边.item.update_line()
                    for 边 in 结点.node.inver_edges:
                        边.item.update_line()

            # self.superior.data.mouse_moved = False
            # self.Auxiliary_line.hide()
            # self.superior.scene.removeItem(self.Auxiliary_line)

        def moveLine(self, pos):
            self.draw_line_end_item = self.itemAt(pos)
            line = self.Auxiliary_line.line()
            p1 = line.p1()  # self.draw_line_start_item.mapToScene(self.draw_line_start_item.rect().center())
            p2 = self.mapToScene(pos)
            rect = self.draw_line_start_item.mapRectToScene(self.draw_line_start_item.rect())
            line.setP2(p2)
            line.setP1(p1)
            self.Auxiliary_line.setLine(line)
            pass

        def startLine(self, pos):
            self.draw_line_start_item: "Grapher.ItemRect" = self.itemAt(pos)
            startItemCenter = self.draw_line_start_item.mapToScene(self.draw_line_start_item.rect().center())
            self.Auxiliary_line.setLine(QLineF(startItemCenter, startItemCenter))
            # print(self.Auxiliary_line.line().p1())
            self.Auxiliary_line.show()
            self.superior.scene.addItem(self.Auxiliary_line)
            pass

        def makeLine(self):
            self.superior.scene.removeItem(self.Auxiliary_line)
            end_item, begin_item = self.draw_line_end_item, self.draw_line_start_item

            if isinstance(end_item, Grapher.ItemRect) and begin_item != end_item:
                begin_id, end_id = begin_item.索引, end_item.索引
                if f"{begin_id},{end_id}" not in self.superior.data.gviewdata.edges:
                    self.superior.add_edge(begin_item.索引, end_item.索引)
            self.superior.data.state.mouseIsMoving = False
            self.Auxiliary_line.hide()

        def make_context_menu(self, event: QtGui.QMouseEvent):
            pairli = funcs.AnkiLinks.get_card_from_clipboard()
            menu = QMenu()
            menu.addAction(Translate.创建为视图).triggered.connect(lambda: self.superior.create_view())
            if len(pairli) > 0:
                menu.addAction(Translate.粘贴卡片).triggered.connect(lambda: self.superior.load_node(pairli))
            # if self.superior.data.graph_mode == GraphMode.view_mode:
            #     menu.addAction(Translate.保存当前视图为群组复习条件).triggered.connect(lambda: self.superior.saveAsGroupReviewCondition())
            pos = event.globalPosition() if common_tools.compatible_import.Anki.isQt6 else event.screenPos()
            menu.exec(pos.toPoint())

        def clearSelection(self):
            if self.superior.data.currentSelectedEdge:
                self.superior.data.currentSelectedEdge[0].unsaveSelect()
            pass

        pass

    class Scene(QGraphicsScene):

        def __init__(self, superior):
            super().__init__(superior)
            self.superior: Grapher = superior

        # def addItem(self, item: "Grapher.ItemRect|Grapher.ItemEdge"):
        #     super().addItem(item)
        #     if isinstance(item,Grapher.ItemRect):
        #         self.superior.data.gviewdata.新增结点(item.索引,item.结点类型)
        #         self.superior.data.add_item_to_node_dict(item)
        #     else:

        pass

    class ItemEdge(common_tools.baseClass.Geometry.ArrowLine):
        edge_from_pen = QPen(QColor(255, 215, 0), 8.0, PenStyle.DashLine)
        highlight_pen = QPen(QColor(255, 215, 0), 8.0, PenStyle.DashLine)
        selected_pen = QPen(QColor(102, 255, 230), 8.0, PenStyle.DashLine)
        normal_pen = QPen(QColor(170,170,170, 70), 6.0, PenStyle.DashLine)
        pdflink_pen = QPen(QColor(255, 255, 127), 6.0, PenStyle.DashLine)
        intextlink_pen = QPen(QColor(255, 255, 127), 6.0, PenStyle.DashLine)
        normal, pdflink, intextlink = 0, 1, 2

        def __init__(self, superior: "Grapher", itemStart: "Grapher.ItemRect", itemEnd: "Grapher.ItemRect", edge_type=0):
            super().__init__()
            self.edge_type = edge_type
            self.superior = superior
            self.itemStart: "Grapher.ItemRect" = itemStart
            self.itemEnd: "Grapher.ItemRect" = itemEnd
            self.update_line()
            self.setZValue(1)
            self.setPen(self.normal_pen)
            self.setFlag(QGraphicsLineItem.GraphicsItemFlag.ItemIsSelectable, True)

        def update_line(self):
            p1: QPointF = self.itemStart.mapToScene(self.itemStart.boundingRect().center())
            p2: QPointF = self.itemEnd.mapToScene(self.itemEnd.boundingRect().center())
            # rectA = self.itemStart.mapRectToScene(self.itemStart.rect())
            # rectB = self.itemEnd.mapRectToScene(self.itemEnd.rect())
            # pA = common_tools.funcs.Geometry.IntersectPointByLineAndRect(QLineF(p1, p2), rectA)
            # pB = common_tools.funcs.Geometry.IntersectPointByLineAndRect(QLineF(p1, p2), rectB)

            # if pA is not None: p1=pA
            # if pB is not None: p2=pB
            # line = QLineF(p1, p2)
            self.setLine(p1.x(), p1.y(), p2.x(), p2.y())
            # self.setLine(line)
            self.show()
            self.setVisible(True)
            # print(f"self visibility = {self}")

        def highlight(self):
            self.setPen(self.highlight_pen)
            self.setZValue(-1)

        def unhighlight(self):
            self.setPen(self.normal_pen)
            self.setZValue(-10)

        def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
            self.saveSelect()
            if event.buttons() == Qt.MouseButton.RightButton:
                menu = QMenu()
                menu.addAction(Translate.删除边).triggered.connect(
                        lambda: self.superior.remove_edge(self.itemStart.索引, self.itemEnd.索引))

                pos = event.screenPos()  # if common_tools.compatible_import.Anki.isQt6 else event.screenPosition()
                # menu.exec(pos)
            super().mousePressEvent(event)

        def saveSelect(self):
            if self.superior.data.currentSelectedEdge:
                self.superior.data.currentSelectedEdge[0].unsaveSelect()
            self.superior.data.currentSelectedEdge = [self]
            self.setPen(self.selected_pen)
            self.setZValue(5)

        def unsaveSelect(self):
            self.setPen(self.normal_pen)
            self.superior.data.currentSelectedEdge = []
            self.setZValue(1)
            # self.unhighlight()

        def shape(self) -> QtGui.QPainterPath:
            path = super().shape()
            path.addPolygon(QPolygonF(self.triangle))
            return path

        #
        def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem',
                  widget: typing.Optional[QWidget] = ...) -> None:
            option.state &= ~QStyle_StateFlag.State_Selected
            super().paint(painter, option, widget)

            if self.isSelected():
                self.setPen(self.selected_pen)
                self.setZValue(5)

            elif not self.isSelected() and not self.superior.scene.selectedItems():
                self.setPen(self.normal_pen)
                self.setZValue(1)
            self.绘制边名(painter)

        def 获取关联的结点(self):
            return self.itemStart.索引, self.itemEnd.索引

        def 获取边名(self):
            A, B = self.获取关联的结点()
            a_b = f"{A},{B}"
            try:
                if a_b in self.superior.data.gviewdata.edges.keys():
                    return self.superior.data.gviewdata.edges[a_b].边名.值
                else:
                    return ""
            except:
                return ""

        def 绘制边名(self, painter):
            paint_center = (self.triangle[1] + self.triangle[2]) / 2
            总是显示 = self.superior.data.gviewdata.config_model.data.edge_name_always_show.value

            文本 = self.获取边名() if self.获取边名() \
                else "debug hello world world hello" \
                if self.superior.data.state == GraphMode.debug_mode \
                else ""
            if 总是显示 or (文本 != "" and self.pen() == self.selected_pen or self.pen() == self.highlight_pen):
                painter.setPen(QColor(50, 205, 50))
                painter.setBrush(QBrush(QColor(50, 205, 50)))
                painter.drawText(QRectF(paint_center, QSizeF(100.0, 100.0)), Qt.TextFlag.TextWordWrap, 文本)

        pass

    class ItemRect(QGraphicsRectItem):

        class 所属类型:
            卡片 = 0
            视图 = 1

        class MODE:
            all = 0
            pdf = 1
            intext = 2
            outext = 3

        def __init__(self, superior: "Grapher", 索引: "str|LinkDataPair", 类型=枚举_视图结点类型.卡片):
            super().__init__()
            self.card_body_style = QColor(197, 224, 235) # card_type_node
            self.card_title_style = QColor(114, 154, 189)
            self.card_body_text_style = QColor(47,109,153)
            self.view_body_style = QColor(239, 220, 118) # view_type_node
            self.view_title_style = QColor(95, 142, 172)
            self.view_body_text_style = QColor(47,109,153)
            self.due_dot_style = QColor(255, 0, 0)

            self.current_title_style = self.card_title_style
            self.current_body_style = self.card_body_style
            self.current_text_style = self.card_body_text_style

            self._类型 = 类型
            self.superior = superior
            self.索引: "str" = 索引 if type(索引) == str else 索引.card_id
            if self.结点类型 == 枚举_视图结点类型.视图:
                self.current_title_style = self.view_title_style
                self.current_body_style = self.view_body_style
                self.current_text_style = self.view_body_text_style
            self.setPen(QPen(self.current_body_style))
            self.setBrush(QBrush(self.current_body_style))
            self.setRect(self.superior.data.default_rect)
            self.setFlag(common_tools.compatible_import.QGraphicsRectItemFlags.ItemIsMovable, True)
            self.setFlag(common_tools.compatible_import.QGraphicsRectItemFlags.ItemIsSelectable, True)
            self.setFlag(common_tools.compatible_import.QGraphicsRectItemFlags.ItemSendsGeometryChanges, True)
            self.setAcceptHoverEvents(True)
            self.contextMenuOpened = False

            w, h = self.boundingRect().width(), self.boundingRect().height()
            self.collide_LeftTop = QRectF(0, 0, w / 4, h / 4)
            self.collide_LeftBot = QRectF(0, h * 3 / 4, w / 4, h / 4)
            self.collide_RightTop = QRectF(w * 3 / 4, 0, w / 4, h / 4)
            self.collide_RightBot = QRectF(w * 3 / 4, h * 3 / 4, w / 4, h / 4)
            self.collide_center = QRectF(w * 1 / 4, h * 1 / 4, w / 2, h / 2)
            self.collide_left = QRectF(0, h * 1 / 4, w / 4, h / 2)
            self.collide_right = QRectF(w * 3 / 4, h * 1 / 4, w / 4, h / 2)
            self.collide_top = QRectF(w / 4, 0, w / 2, h / 4)
            self.collide_bottom = QRectF(w / 4, h * 3 / 4, w / 2, h / 4)

        def 获取保存用的位置(self):

            return [self.scenePos().x(), self.scenePos().y()]

        @property
        def node(self):
            return self.superior.data.node_dict[self.索引]

        def collide_handle(self, item_li: "list[Grapher.ItemRect]" = None):
            if item_li is None:
                item_li = self.get_collide_rect()

            myL, myR, myT, myB = self.rect().left(), self.rect().right(), self.rect().top(), self.rect().bottom()

            for item in item_li:
                L, R, T, B = item.rect().left(), item.rect().right(), item.rect().top(), item.rect().bottom()

                if myL < R:  # item在左边
                    item.moveBy(myL - R, 0)
                elif myR > L:  # item在右边
                    item.moveBy(myR - L, 0)
                elif myB > T:  # item在下边
                    item.moveBy(0, myB - T)
                elif myT < B:  # item在上边
                    item.moveBy(0, myT - B)

        def get_collide_rect(self):
            return [i for i in self.collidingItems() if isinstance(i, Grapher.ItemRect)]

        def check_collide_rect_position(self, item: "Grapher.ItemRect"):
            target = self.mapFromScene(item.pos())

        def make_context_menu(self):
            menu = QMenu()
            menu.addAction(Translate.删除结点).triggered.connect(lambda: self.superior.remove_many_nodes(self.superior.selected_nodes()))
            # noinspection PyUnresolvedReferences
            menu.addAction(Translate.修改描述).triggered.connect(lambda: self.superior.结点属性查看器([self],[]))

            if self.superior.data.gviewdata.nodes[self.索引].数据类型.值 == common_tools.baseClass.视图结点类型.卡片:
                pair_li: "list[LinkDataPair]" = [LinkDataPair(item.索引, funcs.CardOperation.desc_extract(item.索引)) for item in self.superior.selected_nodes() if funcs.CardOperation.exists(item.索引)]
                common_tools.menu.maker(common_tools.menu.T.grapher_node_context)(pair_li, menu, self.superior,
                                                                                  needPrefix=False)

            def menuCloseEvent():
                self.setSelected(True)
                self.setFlag(common_tools.compatible_import.QGraphicsRectItemFlags.ItemIsMovable, True)
                self.contextMenuOpened = False

            menu.closeEvent = lambda x: menuCloseEvent()
            self.contextMenuOpened = True
            self.setFlag(common_tools.compatible_import.QGraphicsRectItemFlags.ItemIsMovable, False)
            return menu

        def mouseDoubleClickEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
            if self.superior.data.graph_mode == GraphMode.debug_mode:
                return
            if event.buttons() == Qt.MouseButton.LeftButton:
                if self.结点类型 == 枚举_视图结点类型.卡片:
                    common_tools.funcs.Dialogs.open_custom_cardwindow(self.索引)
                elif self.结点类型 == 枚举_视图结点类型.视图:
                    data = common_tools.funcs.GviewOperation.load(uuid=self.索引)
                    common_tools.funcs.Dialogs.open_grapher(gviewdata=data, mode=GraphMode.view_mode)
                self.superior.data.gviewdata.数据更新.结点访问发生(self.索引)

            super().mouseDoubleClickEvent(event)

        def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
            if self.superior.data.currentSelectedEdge:
                self.superior.data.currentSelectedEdge[0].unsaveSelect()

            if event.buttons() == Qt.MouseButton.RightButton:
                if event.modifiers() != Qt.KeyboardModifier.ControlModifier:
                    self.make_context_menu().exec(event.screenPos())
            # if not self.contextMenuOpened:
            super().mousePressEvent(event)

            pass

        def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
            self.prepareGeometryChange()
            if event.buttons() == Qt.MouseButton.LeftButton:
                edges = self.superior.data.node_dict[self.索引].edges
                inver_edges = self.superior.data.node_dict[self.索引].inver_edges
                for edge in edges:
                    edge.item.update_line()
                for edge in inver_edges:
                    edge.item.update_line()
            super().mouseMoveEvent(event)

            # print(self.scenePos().__str__())

        def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:

            if not self.contextMenuOpened:
                super().mouseReleaseEvent(event)
                self.setFlag(common_tools.compatible_import.QGraphicsRectItemFlags.ItemIsMovable, True)

        # def drawRedDot(self):

        @property
        def 结点类型(self):
            return self._类型

        def 结点描述(self):
            if self.superior.data.graph_mode == GraphMode.debug_mode:
                return "debug"
            return self.superior.data.gviewdata.nodes[self.索引].描述.值

        def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem',
                  widget: typing.Optional[QWidget] = ...) -> None:
            super().paint(painter, option, widget)

            painter.setPen(self.current_title_style)
            painter.setBrush(QBrush(self.current_title_style))
            header_height = 24
            header_rect = QRectF(0, 0, int(self.rect().width()), header_height)
            body_rect = QRectF(0, header_height, int(self.rect().width()), int(self.rect().height() - header_height))
            painter.drawRect(header_rect)

            painter.setPen(QColor(255, 255, 255))
            painter.drawText(header_rect.adjusted(5, 5, -5, -5), Qt.TextFlag.TextWordWrap, str(self.索引))
            painter.setPen(self.current_text_style)
            painter.drawText(body_rect.adjusted(5, 5, -5, -5), Qt.TextFlag.TextWordWrap, f"""{self.结点描述()}""")

            if self.isSelected():
                path = QPainterPath()
                path.addRect(self.rect())
                painter.strokePath(path, Grapher.ItemEdge.highlight_pen)
                self.setZValue(20)
            else:
                self.setZValue(10)

        pass

    class ToolBar(QToolBar):
        """这是一个工具栏

        """

        class Actions:
            def __init__(self, parent: "Grapher.ToolBar"):
                self.superior = parent
                imgDir = common_tools.G.src.ImgDir
                self.save = QAction(QIcon(imgDir.save_as), "", parent)
                self.roaming = QAction(QIcon(imgDir.box2), "", parent)
                self.config = QAction(QIcon(imgDir.config), "", parent)
                self.reConfig_Btn = QAction(QIcon(imgDir.config_reset), "", parent)
                self.help = QAction(QIcon(imgDir.help), "", parent)
                self.itemDel = QAction(QIcon(imgDir.delete), "", parent)
                self.itemRename = QAction(QIcon(imgDir.ID_card), "", parent)
                self.insert_item = QMenu()
                self.initUI()

            def initUI(self):
                [self.li[i].setToolTip(self.tooltips[i]) for i in range(len(self.li))]

            @property
            def tooltips(self):
                T = common_tools.language.Translate
                return [
                        T.另存视图,
                        T.开始漫游复习,
                        T.打开配置表,
                        T.重置配置表,
                        "help",
                        T.删除,
                        T.说明_属性查看,
                ]

            @property
            def li(self):
                return [
                        self.save,
                        self.roaming,
                        self.config,
                        self.reConfig_Btn,
                        self.help,
                        self.itemDel,
                        self.itemRename
                ]

        def __init__(self, parent: "Grapher"):
            super().__init__(parent)
            self.superior = parent
            self.act = self.Actions(self)
            self.setIconSize(QSize(16, 16))
            self.initUI()
            self.initEvent()

        def initUI(self):
            self.addActions(self.act.li[0:4])
            self.addSeparator()
            self.addActions(self.act.li[4:])
            self.addSeparator()
            self.生成图元插入菜单()

            self.act.itemDel.setDisabled(True)
            # self.act.itemRename.setDisabled(True)
            pass

        def 生成图元插入菜单(self):
            引入图标 = QPushButton()
            引入图标.setIcon(QIcon(common_tools.G.src.ImgDir.item_plus))
            主菜单 = QMenu()
            新建菜单 = 主菜单.addMenu(译.新建)
            新建菜单.addAction(译.卡片).triggered.connect(self.create_card)
            新建菜单.addAction(译.视图).triggered.connect(self.create_view)
            引入图标.setMenu(主菜单)
            self.addWidget(引入图标)
            pass

        def create_card(self):
            """
            调用原生的卡片创建窗口,并在完成后返回卡片id到当前视图id
            """
            common_tools.G.常量_当前等待新增卡片的视图索引 = self.superior.data.gviewdata.uuid
            mw.onAddCard()
            addcard: aqt.addcards.AddCards = aqt.DialogManager._dialogs["AddCards"][1]
            did = self.superior.data.gviewdata.config_model.data.default_deck_for_add_card.value
            if did != -1:
                addcard.deck_chooser.selected_deck_id = did
            mid = self.superior.data.gviewdata.config_model.data.default_template_for_add_card.value
            if mid != -1:
                addcard.notetype_chooser.selected_notetype_id = mid
            # addcard.deck_chooser.selected_deck_id
            pass

        def create_view(self):
            config = None
            config_id = self.superior.data.gviewdata.config_model.data.default_config_for_add_view.value
            if funcs.GviewConfigOperation.存在(config_id):
                config = config_id
            视图 = common_tools.funcs.GviewOperation.create(config=config)
            if 视图:
                视图.保存()
                self.superior.load_node([视图.uuid], 参数_视图结点类型=枚举_视图结点类型.视图)
            pass

        def initEvent(self):
            [self.act.li[i].triggered.connect(self.slots[i]) for i in range(len(self.slots))]
            # self.act.cardDel.triggered.connect(self.deleteItem)
            # self.act.cardRename.triggered.connect(self.renameItem)
            pass

        def checkAction(self):
            """判断删除项目的按钮是否应当激活
            1 多选卡片和多选边都能批量删除, 如果同时多选了卡片和边, 则批量删除卡片, 忽略边的删除,因为删除卡片的时候会删掉一些边,变得不好处理
            """
            try:
                if len(self.superior.scene.selectedItems()) > 0:
                    items = self.superior.scene.selectedItems()
                    # if len(items) == 1 and (isinstance(items[0], Grapher.ItemRect) or isinstance(items[0], Grapher.ItemEdge)):
                    #     self.act.itemRename.setDisabled(False)
                    # else:
                    #     self.act.itemRename.setDisabled(True)
                    self.act.itemDel.setDisabled(False)
                else:
                    self.act.itemDel.setDisabled(True)
                    # self.act.itemRename.setDisabled(True)
            except:
                return None

        def deleteEdgeItem(self, item: "Grapher.ItemEdge"):
            # cardA = item.itemStart.pair.card_id
            # cardB = item.itemEnd.pair.card_id
            # modifyGlobalLink = self.superior.data.graph_mode == GraphMode.normal
            self.superior.remove_edge(*item.获取关联的结点())
            pass

        def deleteRectItem(self, item: "Grapher.ItemRect"):
            self.superior.remove_node(item)
            pass

        def node_property_editor(self):
            if len(self.superior.scene.selectedItems()) > 0:
                node_items = self.superior.selected_nodes()
                edge_items = self.superior.selected_edges()
                self.superior.结点属性查看器(node_items, edge_items)
            else:
                self.superior.自身属性查看器()
            # def 结点编辑组件():
            #     主窗体 = QDialog()
            #     表单布局 = QFormLayout()
            #     确认按钮 =

            pass

        def deleteItem(self):  # 0=rect,1=line
            rectItem: "list[Grapher.ItemRect]" = [item for item in self.superior.scene.selectedItems() if isinstance(item, Grapher.ItemRect)]
            lineItem: "list[Grapher.ItemEdge]" = [item for item in self.superior.scene.selectedItems() if isinstance(item, Grapher.ItemEdge)]
            if rectItem or lineItem:
                code = QMessageBox.information(self, 译.你将删除这些结点, 译.你将删除这些结点, QMessageBox.Yes | QMessageBox.No)
                if code == QMessageBox.Yes:
                    if len(rectItem) > 0:
                        for item in rectItem:
                            self.deleteRectItem(item)
                    if len(lineItem) > 0:
                        for item in lineItem:
                            self.deleteEdgeItem(item)
            # item = self.superior.scene.selectedItems()[0]
            # if isinstance(item, Grapher.ItemRect):
            #     self.deleteRectItem(item)
            # elif isinstance(item, Grapher.ItemEdge):
            #     self.deleteEdgeItem(item)
            pass
            # self.actionGroupReviewSave = QAction(QIcon(imgDir.save),"",self)

        def saveAsNewGview(self):
            self.superior.create_view()
            pass

        # def registGviewAsGroupReview(self):
        #     self.superior.saveAsGroupReviewCondition()
        #     pass

        def openRoaming(self):
            """这是个大工程, 需要
            1一个算法计算队列,
            2一个多卡片窗口,
            3一个队列创跨
            """
            if not self.superior.roaming:
                self.superior.roaming = GrapherRoamingPreviewer(self.superior)
            self.superior.roaming.show()
            self.superior.roaming.activateWindow()
            pass

        def openConfig(self):
            """"""
            布局, 组件, 子代 = funcs.G.objs.Bricks.三元组
            视图记录 = self.superior.data.gviewdata
            配置类 = common_tools.objs.Record.GviewConfig

            配置记录 = 视图记录.config_model
            # funcs.Utils.print("打开的配置记录是",配置记录)
            # 配置记录.saveModelToDB()
            配置组件 = common_tools.funcs.GviewConfigOperation.makeConfigDialog(调用者=self, 数据=配置记录.data, 关闭时回调=视图记录.数据更新.保存配置数据)
            配置组件布局: "QVBoxLayout" = 配置组件.layout()

            def 打开配置选取窗():
                输入框 = funcs.组件定制.单行输入框(占位符=译.输入关键词并点击查询)
                结果表 = funcs.组件定制.表格()

                def 搜索关键词():
                    关键词 = 输入框.text()
                    搜索结果 = funcs.GviewConfigOperation.据关键词同时搜索视图与配置数据库表(关键词)
                    结果表模型 = funcs.组件定制.模型(["类型/type", "名称/name"])
                    项 = common_tools.baseClass.Standard.Item
                    [结果表模型.appendRow([项(类型), 项(名字, data=标识)]) for 类型, 名字, 标识 in 搜索结果 if (类型 == 译.配置 and 标识 != 配置记录.uuid) or (类型 == 译.视图 and 标识 not in 配置记录.data.appliedGview.value)]
                    结果表.setModel(结果表模型)
                    if 结果表模型.rowCount() == 0:
                        tooltip("搜索结果为空/empty result")

                def 开始更换配置():
                    if 结果表.selectedIndexes():
                        模型: "QStandardItemModel" = 结果表.model()
                        选中行: "list[QStandardItem]" = [模型.itemFromIndex(索引) for 索引 in 结果表.selectedIndexes()]
                        类型, 标识 = 选中行[0].text(), 选中行[1].data()
                        最终标识 = 标识 if 类型 == 译.配置 else funcs.GviewOperation.load(uuid=标识).config
                        新配置模型 = 配置类.readModelFromDB(最终标识)

                        funcs.GviewConfigOperation.指定视图配置(self.superior.data.gviewdata, 新配置模型)
                        self.superior.data.gviewdata = funcs.GviewOperation.load(self.superior.data.gviewdata.uuid)
                        配置记录.data.元信息.确定保存到数据库 = False
                        总组件.close()
                        配置组件.close()
                        self.openConfig()

                搜索按钮 = funcs.组件定制.按钮(funcs.G.src.ImgDir.open, "", 触发函数=搜索关键词)
                确认按钮 = funcs.组件定制.按钮(funcs.G.src.ImgDir.correct, "", 触发函数=开始更换配置)
                说明 = funcs.组件定制.文本框(文本=译.说明_同时搜索配置与视图的配置, 开启自动换行=True)
                布局树 = {布局: QVBoxLayout(), 子代: [{布局: QHBoxLayout(), 子代: [{组件: 输入框}, {组件: 搜索按钮}]}, {组件: 结果表}, {组件: 确认按钮}, {组件: 说明}]}
                总组件 = funcs.组件定制.组件组合(布局树, 容器=funcs.组件定制.对话窗口(标题=译.搜索并选择配置))
                总组件.exec()


                pass

            def 触发新建配置():
                funcs.GviewConfigOperation.指定视图配置(视图记录, None)
                配置组件.close()
                self.openConfig()

            更换配置说明 = funcs.组件定制.文本框(译.说明_视图配置与视图的区别, 开启自动换行=True)
            更换配置按钮 = funcs.组件定制.按钮(common_tools.G.src.ImgDir.refresh, 译.更换本视图的配置, 触发函数=打开配置选取窗)
            新建配置按钮 = funcs.组件定制.按钮(common_tools.G.src.ImgDir.item_plus, 译.新建配置, 触发函数=触发新建配置)
            配置组件的底部组件 = funcs.组件定制.组件组合({布局: QVBoxLayout(), 子代: [{布局: QHBoxLayout(), 子代: [{组件: 更换配置按钮}, {组件: 新建配置按钮}]}, {组件: 更换配置说明}]})
            配置组件布局.addWidget(配置组件的底部组件)
            配置组件.setLayout(配置组件布局)
            配置组件.exec()
            funcs.GviewOperation.刷新所有已打开视图的配置()

            pass

        def resetConfig(self):
            code = QMessageBox.information(self, 译.你将重置本视图的配置, 译.你将重置本视图的配置, QMessageBox.Yes | QMessageBox.No)
            if code == QMessageBox.Yes:
                funcs.GviewConfigOperation.指定视图配置(self.superior.data.gviewdata)
                self.superior.data.gviewdata.config_model = funcs.GviewConfigOperation.从数据库读(self.superior.data.gviewdata.config)
                tooltip("reset configuration ok")
            pass

        def helpFunction(self):
            """一个默认弹窗即可"""
            zh = """
如何选中卡片: 左键点击卡片,
如何选中边:  左键点击边,
如何移动卡片: 拖放选中的卡片即可,
如何移动画布: 先点击画布以取消物品选中, 此时即可用左键来拖动画布
如何多选卡片: 先点击画布以取消物品选中, 用右键在画布上拖动, 会出现矩形, 矩形覆盖到的卡片都会被选中.
如何链接卡片: 先选中卡片, 保持左键并按下ctrl不动, 再拖动鼠标, 就可拖出一条跟着鼠标走的线, 将其拖动到另一张卡片上, 最后松开左键, 就能建立两张卡片的链接.
How to select a card: Left click on the card,
How to select an edge: Left click on the edge,
How to move a card: Drag and drop the selected card,
How to move the canvas: First click on the canvas to unselect the items, then you can drag the canvas with the left button
How to select more cards: First click on the canvas to unselect the items, then drag the right click on the canvas, a rectangle will appear and all the cards covered by the rectangle will be selected.
How to link cards: First select a card, hold the left button and press ctrl, then drag the mouse to create a line that follows the mouse, drag it to another card, and finally release the left button to create a link between the two cards.
            """
            funcs.Utils.大文本提示框(zh, 取消模态=True)
            # showInfo(zh)
            pass

        @property
        def slots(self):
            return [
                    self.saveAsNewGview,
                    self.openRoaming,
                    self.openConfig,
                    self.resetConfig,
                    self.helpFunction,
                    self.deleteItem,
                    self.node_property_editor,
            ]
    # class Item(QGraphicsItem):
    #     def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem', widget: typing.Optional[QWidget] = ...) -> None:
    #     pass


class GViewAdmin(QDialog):
    """视图管理器,实现改名,复制链接,删除,打开
    TODO:
        实现视图按名称排序, 按访问频率排序, 正序逆序都要有, 以及自由排序, 自动保存展开状态, 视图管理器可以直接创建空的视图
    """

    class DisplayState:
        as_tree = 0
        as_list = 1

    def __init__(self):
        super().__init__()
        # self.search = self.SearchBar(self)
        if not funcs.G.DB.表存在(funcs.G.DB.table_Gview_cache):
            funcs.GviewOperation.更新缓存()
        self.view = self.Tree(self)
        self.bottom = self.Bottom(self)
        self.model = self.Model(self)
        self.view.setModel(self.model)
        self.data: "dict[str,Optional[GViewData]]" = {}
        self.wait_for_delete: "set[str]" = set()
        self.wait_for_update: "set[GViewData]" = set()
        self.displaystate = funcs.Config.get().gview_admin_default_display.value
        self.init_UI()
        self.init_data()
        self.view.init_UI()
        self.allevent = common_tools.objs.AllEventAdmin([
                [self.bottom.open_button.clicked, self.on_open],
                [self.bottom.rename_button.clicked, self.on_rename],
                [self.bottom.delete_button.clicked, self.on_delete],
                [self.bottom.link_button.clicked, self.on_link],
                [self.bottom.display_button.clicked, self.on_display_changed],
                [self.bottom.create_button.clicked, self.on_create],
                [self.bottom.help_button.clicked, self.on_help],
                [self.model.itemChanged, self.on_model_item_changed_handle],
                [self.view.doubleClicked, self.on_view_doubleclicked_handle],
                [self.view.customContextMenuRequested, self.on_view_contextmenu_handle],
                [common_tools.G.signals.on_card_answerd, self.on_display_changed],
                # [self.view.horizontalHeader().clicked,self.on_horizontal_header_clicked_handle],
        ]).bind()

    def on_help(self):
        funcs.Utils.大文本提示框(译.说明_视图管理器的用法)

    def on_view_contextmenu_handle(self, pos):
        # item = self.model.itemFromIndex(self.view.indexAt(pos))
        项表 = self.view.获取有效项()
        if len(项表) == 0:
            return
        # if item is None:
        #     return
        # if item.data(Qt.UserRole) is None:
        #     tooltip(Translate.请点击叶结点)
        #     return
        else:
            菜单 = self.view.contextMenu = QMenu(self.view)
            if len(项表) == 2:
                item = 项表[0]
                data = item.data(Qt.ItemDataRole.UserRole)
                菜单.addAction(译.重命名, ).triggered.connect(lambda: self.on_rename(item))
                菜单.addAction(译.设为默认视图).triggered.connect(lambda: self.on_set_as_default_view(item))
            待插视图数据表: "list[GViewData]" = [项.data(Qt.ItemDataRole.UserRole) for 项 in 项表]

            菜单.addAction(译.删除).triggered.connect(lambda: self.当_删除多个(待插视图数据表))
            菜单2 = 菜单.addMenu(译.导入到视图)
            菜单2.addAction(译.选择一个视图).triggered.connect(lambda: self.当_选择视图插入(待插视图数据表))
            已打开视图菜单 = 菜单2.addMenu(译.插入到已经打开的视图)
            for 视图编号 in funcs.GviewOperation.列出已打开的视图():
                已打开视图: Grapher = funcs.G.mw_gview[视图编号]
                已打开视图菜单.addAction(已打开视图.data.gviewdata.name).triggered.connect(lambda: self.当_插入到视图(已打开视图, 待插视图数据表))
            菜单2.addAction(译.新建视图).triggered.connect(lambda: self.当_创建视图并插入(待插视图数据表))
            菜单.popup(QCursor.pos())

    def 当_插入到视图(self, 已打开视图: Grapher, 待插视图数据表: "list[GViewData]"):
        已打开视图.load_node(待插视图数据表, 参数_视图结点类型=枚举_视图结点类型.视图)
        已打开视图.activateWindow()
        pass

    def 当_创建视图并插入(self, 待插视图数据表: "list[GViewData]"):
        视图编号 = funcs.GviewOperation.create().uuid
        视图对象: Grapher = funcs.G.mw_gview[视图编号]
        视图对象.load_node(待插视图数据表, 参数_视图结点类型=枚举_视图结点类型.视图)
        pass

    def 当_选择视图插入(self, 待插视图数据表: "list[GViewData]"):
        被插视图数据 = funcs.GviewOperation.choose_insert()
        if 被插视图数据:
            被插视图对象: Grapher = funcs.G.mw_gview[被插视图数据.uuid]
            被插视图对象.load_node(待插视图数据表, 参数_视图结点类型=枚举_视图结点类型.视图)
        pass

    def on_view_doubleclicked_handle(self, index: "QModelIndex"):
        # noinspection PyTypeChecker
        item: "GViewAdmin.Item" = self.model.itemFromIndex(index)
        if item.column() != 0:
            item = self.model.item(item.row(), 0)
        if item:
            data = item.data(Qt.UserRole)
            if data is None:
                funcs.Utils.tooltip(Translate.不存在)
                return
            funcs.Dialogs.open_grapher(gviewdata=funcs.GviewOperation.load(gviewdata=item.data(Qt.UserRole)), mode=GraphMode.view_mode)

    def on_horizontal_header_clicked_handle(self):
        print("horizontalHeader clicked")

    def on_model_item_changed_handle(self, item: "GViewAdmin.Item"):
        data: "GViewData" = item.data(Qt.UserRole)
        if not re.match(r"\S", item.text()):
            item.setText(data.name)
            funcs.Utils.tooltip(Translate.视图命名规则)
            return
        data.name = item.text()
        funcs.GviewOperation.save(data)

        pass

    def get_item(self) -> "GViewAdmin.Item":
        indxs = self.view.selectedIndexes()
        if len(indxs) == 0:
            return None
        item: "GViewAdmin.Item" = self.model.itemFromIndex(indxs[0])
        return item

    def on_display_changed(self):
        btn = self.bottom.display_button
        if self.displaystate == self.DisplayState.as_tree:
            btn.setIcon(QIcon(src.ImgDir.list))
            btn.setToolTip("display as list")
            self.displaystate = self.DisplayState.as_list
            self.build_list()

        else:
            btn.setIcon(QIcon(src.ImgDir.tree))
            btn.setToolTip("display as tree")
            self.displaystate = self.DisplayState.as_tree
            self.build_tree()

        funcs.Config.get().gview_admin_default_display.value = self.displaystate
        self.view.expandAll()

    def on_open(self):
        item = self.get_item()
        if not item: return
        data: "GViewData" = item.data(Qt.UserRole)
        funcs.Dialogs.open_grapher(gviewdata=data, mode=GraphMode.view_mode)
        pass

    def save(self):
        """关闭的时候自动保存退出, 不提供任意移动功能"""
        funcs.GviewOperation.save(data_li=self.wait_for_update)
        funcs.GviewOperation.delete(uuid_li=self.wait_for_delete)
        self.wait_for_delete = set()
        self.wait_for_update = set()

    def rebuild(self):
        self.save()
        if self.displaystate == self.DisplayState.as_tree:
            self.build_tree()
        else:
            self.build_list()
        self.view.expandAll()
        # self.view.setColumnWidth(0,400)

    def on_rename(self, it=None):
        """由于有两个不同的display所以需要弹出窗口让同学修改"""
        item: "GViewAdmin.Item" = self.get_item() if not it else it
        if not item: return
        data: "GViewData" = item.data(Qt.UserRole)
        newname, submitted = funcs.GviewOperation.get_correct_view_name_input(data.name)
        if not submitted: return
        data.name = newname
        self.wait_for_update.add(data)
        self.rebuild()
        pass

    def on_set_as_default_view(self, item=None):
        item: "GViewAdmin.Item" = self.get_item() if not item else item
        if not item: return
        data: "GViewData" = item.data(Qt.UserRole)
        funcs.GviewOperation.设为默认视图(data.uuid)
        tooltip("ok")

    def on_link(self):
        item = self.get_item()
        if not item: return
        data: "GViewData" = item.data(Qt.UserRole)
        m = QMenu()
        funcs.MenuMaker.gview_ankilink(m, data)
        l_b = self.bottom.link_button
        # pos=l_b.mapToGlobal(l_b.pos())
        m.move(QCursor.pos())
        m.exec_()
        pass

    def on_delete(self, it=None):
        item = self.get_item() if not it else it
        if not item: return
        data: "GViewData" = item.data(Qt.UserRole)
        self.wait_for_delete.add(data.uuid)
        self.data[data.uuid] = None
        self.rebuild()
        pass

    def on_create(self):
        funcs.GviewOperation.create()
        self.rebuild()
        pass

    def 当_删除多个(self, 项表: "list[GViewData]"):
        for 项 in 项表:
            self.wait_for_delete.add(项.uuid)
            self.data[项.uuid] = None
        self.rebuild()

    def init_UI(self):

        # self.view.setHorizontalHeaderLabels(["view name","due count"])
        self.setWindowTitle("gview manager")
        self.setContentsMargins(0, 0, 0, 0)
        self.setWindowIcon(QIcon(src.ImgDir.gview_admin))
        self.resize(400, 600)
        self.view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        g_layout = QVBoxLayout(self)
        g_layout.setContentsMargins(0, 0, 0, 0)
        g_layout.setSpacing(0)
        g_layout.addWidget(self.view)
        g_layout.addWidget(self.bottom)
        self.setLayout(g_layout)

    def init_data(self, data=None):
        datas = data if data is not None else funcs.GviewOperation.load_all()
        self.data = {}
        for data in datas:
            self.data[data.uuid] = data
        # list(map(lambda x: self.data.__setitem__(x.uuid, x), datas))
        self.rebuild()

    def init_model(self):
        self.model.clear()
        self.model.setHorizontalHeaderLabels(["view name", "due count"])

    def build_tree(self):
        """
        把 a::b::c 转换成树结构已经做了两遍了, 但还是不熟练,
        思路写一下: 设计一个树结点, 先给他添加invisibleRootItem, 然后构造一个栈,深度优先遍历
        """
        self.init_model()
        root = Struct.TreeNode(item=self.model.invisibleRootItem(), children={})

        for data in self.data.values():
            if not isinstance(data, GViewData):
                continue

            original_name = data.name.split("::")
            parent = root
            while original_name:
                nodename = original_name.pop(0)
                if nodename not in parent.children:
                    item = self.Item(nodename, data=None if original_name else data)
                    if funcs.G.ISLOCALDEBUG:
                        dueCountItem = self.Item("0")
                    else:
                        dueCountItem = self.Item(f"{common_tools.funcs.GviewOperation.getDueCount(data)}", data=None if original_name else data)
                    parent.item.appendRow([item, dueCountItem])
                    parent.children[nodename] = Struct.TreeNode(item=item, children={})
                parent = parent.children[nodename]
        pass

    def build_list(self):
        self.init_model()
        for data in self.data.values():
            if isinstance(data, GViewData):
                item = self.Item(data.name, data=data)
                dueCountItem = self.Item(f"{common_tools.funcs.GviewOperation.getDueCount(data)}", data=data)
                self.model.appendRow([item, dueCountItem])

        pass

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.save()
        # funcs.GviewOperation.更新缓存()
        funcs.G.GViewAdmin_window = None

    class Model(QStandardItemModel):
        def addRow(self, data: GViewData):  # 这个函数没有用的地方
            item = GViewAdmin.Item(data)
            self.appendRow(item)

    class ItemRole:
        terminal = 0
        nonterminal = 1

    class Item(QStandardItem):
        def __init__(self, name, data: GViewData = None):
            super().__init__(name)
            self.setFlags(self.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if data:
                self.setData(data, role=common_tools.compatible_import.ItemDataRole.UserRole)  # 当不设置的时候,返回的是空
                # self.setFlags(self.flags() | Qt.ItemFlag.ItemIsSelectable)

    class Tree(QTreeView):
        def __init__(self, superior: 'GViewAdmin'):
            super().__init__()
            self.superior = superior
            self.setParent(superior)

        def init_UI(self):
            self.setSelectionMode(common_tools.compatible_import.QAbstractItemViewSelectMode.ExtendedSelection)
            self.setDragDropMode(common_tools.compatible_import.DragDropMode.NoDragDrop)
            self.setAcceptDrops(False)
            self.header().setSectionResizeMode(common_tools.compatible_import.QHeaderView.ResizeMode.ResizeToContents)
            # self.setColumnWidth(0,400)

        def 获取有效项(self):
            有效结点 = []
            for idx in self.selectedIndexes():
                item = self.superior.model.itemFromIndex(idx)
                if item.data(Qt.ItemDataRole.UserRole):
                    有效结点.append(item)

            return 有效结点

    class Bottom(QWidget):
        def __init__(self, superior: 'GViewAdmin'):
            super().__init__()
            self.superior = superior
            self.setParent(superior)
            self.rename_button = QToolButton(self)
            self.delete_button = QToolButton(self)
            self.link_button = QToolButton(self)
            self.open_button = QToolButton(self)
            self.display_button = QToolButton(self)
            self.help_button = QToolButton(self)
            self.create_button = QToolButton(self)
            self.search_edit = QLineEdit(self)
            self.search_edit.setPlaceholderText(译.在此处搜索)
            h_layout = QHBoxLayout(self)
            h_layout.setContentsMargins(0, 0, 0, 0)
            h_layout.addWidget(self.search_edit)
            self.setContentsMargins(0, 0, 0, 0)
            button_li: "list[QToolButton]" = [self.display_button, self.open_button, self.rename_button, self.delete_button, self.link_button, self.create_button, self.help_button]
            icon_li = [src.ImgDir.tree, src.ImgDir.preview_open, src.ImgDir.rename, src.ImgDir.delete, src.ImgDir.link, src.ImgDir.item_plus, src.ImgDir.help]
            tooltip_li = ["display as tree", "open", "rename", "delete", "copy link", "create", "help"]
            # self.open_button.setToolTip()
            list(map(lambda x: x.setContentsMargins(0, 0, 0, 0), button_li))
            list(map(lambda x: h_layout.addWidget(x, alignment=AlignmentFlag.AlignRight), button_li))
            list(map(lambda x: x[0].setIcon(QIcon(x[1])), zip(button_li, icon_li)))
            list(map(lambda x: x[0].setToolTip(x[1]), zip(button_li, tooltip_li)))
            self.search_edit.textChanged.connect(self.on_search_edit_text_changed)
            QShortcut(Qt.Key.Key_Return, self.search_edit).activated.connect(lambda: self.searching(self.search_edit.text()))
            self.setLayout(h_layout)

        def on_search_edit_text_changed(self, text: str):
            if re.search(r"\S", text):
                # self.searching(text)
                pass
            else:
                self.table_recover()
            # self.search_edit.blockSignals(True)
            # QTimer.singleShot(250, lambda: self.search_edit.blockSignals(False))

        def searching(self, text):

            result = funcs.GviewOperation.fuzzy_search(text)
            # tooltip(result.__str__())
            self.superior.init_data(result)
            pass

        def table_recover(self):
            self.superior.init_data()
            pass


class GrapherRoamingPreviewer(QMainWindow):
    """
    点击侧边栏的复习队列上的卡片, 则渲染对应预览卡片, 回答该卡片则刷新侧边栏卡片, 刷新卡片则要自动选中第一张卡片,
    如果侧边栏是空的, 则不显示预览
    同时要保持侧边栏更新(当在其他视图里回答了相关卡片,刷新)
    漫游复习列表为空时: 弹出提示, 点击确定后关闭漫游复习, 为空时预览窗停留在最后一张卡片.
    2022年10月25日05:49:12
    TODO:    编辑卡片时,需要同步更新, 先做出来看看吧

    """

    def __init__(self, superior):

        super().__init__()

        self.superior: "Grapher" = superior
        self.当前编码 = ""
        self.导航按钮组 = self.导航组件(self)

        self.listView = self.List(self)

        self.layoutH = QHBoxLayout()  # QMainWindow的布局
        self._cardView: load.SingleCardPreviewer = None

        self.复习_视图结点展示组件 = self.复习对象_视图结点(self)
        self.container = QWidget()
        self.initUI()
        # self.initEvent()
        if self.listView.tempModel.rowCount() == 0:
            self.圆满完成()
        else:
            self.listView.selectRow(0)
        if self.superior.data.gviewdata.config_model.data.roaming_sidebar_hide.value:
            self.switch_sidebar_show_hide()
        self.初始化快捷键()
        if self.superior.data.gviewdata.config_model.data.split_screen_when_roaming.value:
            funcs.通用.窗口.半开(self.superior,"右")
            funcs.通用.窗口.半开(self)

    def 初始化快捷键(self):

        QShortcut(Qt.Key.Key_Up, self).activated.connect(self.导航按钮组.按钮_上一个.click)
        QShortcut(Qt.Key.Key_Down, self).activated.connect(self.导航按钮组.按钮_下一个.click)
        QShortcut(Qt.Key.Key_Left, self).activated.connect(self.frontSideOfCard)
        QShortcut(Qt.Key.Key_Right, self).activated.connect(self.backSideOfCard)


    def backSideOfCard(self):
        编号 = self.获取当前结点的编码()
        结点数据 = self.superior.data.gviewdata.nodes
        if 结点数据[编号].数据类型.值 == 枚举_视图结点类型.卡片:
            if self.cardView._state=="question":
                self.cardView._on_other_side()
        pass

    def frontSideOfCard(self):
        编号 = self.获取当前结点的编码()
        结点数据 = self.superior.data.gviewdata.nodes
        if 结点数据[编号].数据类型.值 == 枚举_视图结点类型.卡片:
            if self.cardView._state == "answer":
                self.cardView._on_other_side()
        pass

    def 更新结点复习(self, node_id):
        self.superior.data.gviewdata.数据更新.结点复习发生(str(node_id))

    @property
    def dueQueue(self) -> "list[str]":
        视图数据 = self.superior.data.gviewdata
        if not 视图数据.config:
            return list(视图数据.nodes.keys())
        else:

            配置数据 = self.superior.data.gviewdata.config_model
            队列 = [编号 for 编号 in 视图数据.nodes.keys() if funcs.GviewConfigOperation.满足过滤条件(视图数据, 编号, 配置数据)]
            队列2 = funcs.GviewConfigOperation.漫游路径生成(视图数据, 配置数据, 队列, [node.索引 for node in self.superior.selected_nodes() if node.isSelected() and node.索引 in 队列])
            # funcs.Utils.print(list(视图数据.nodes.keys()),队列, 队列2,配置数据.__str__())
            return 队列2

    @property
    def cardView(self)->'load.SingleCardPreviewer':
        """SingleCardPreviewer 第一个参数必须是Card对象,否则就无法启动.
        但 视图中, 很有可能没有card存在, 也有可能第一行是view,
        在切换到view显示时, cardView需要一个伪组件用来隐藏, 相关的事件也要延后
        """
        if not self._cardView and self.当前编码 != "":
            from .custom_cardwindow import SingleCardPreviewer
            initCard = common_tools.funcs.CardOperation.GetCard(self.当前编码)
            self._cardView = SingleCardPreviewer(initCard, superior=self, parent=self, mw=mw, on_close=lambda: None)
            self.initEvent()
            # self._cardView.open()
            self.layoutH.addWidget(self.cardView, stretch=1)
            self._cardView.revWidget.当完成复习.append(lambda 卡片编号, 难度, 平台: self.更新结点复习(卡片编号))
            self._cardView.revWidget.当完成复习.append(lambda 卡片编号, 难度, 平台,: self.item_finish())
            self._cardView.activateAsSubWidget()
            return self._cardView
        elif self._cardView:
            return self._cardView
        else:
            return QWidget()

    def readCard(self, card_id):
        return common_tools.funcs.CardOperation.GetCard(card_id)

    def 获取当前结点的编码(self):
        项 = self.listView.tempModel.itemFromIndex(self.listView.currentIndex())
        return 项.data()

    def item_finish(self, 自动关闭=True):
        """可以理解为 item finish 每次点击复习后调用他来到下一个对象"""
        if self.还有结点():
            选中行号 = self.listView.currentIndex().row()
            self.listView.removeCurrentItem()
            选中行号的新索引 = self.listView.tempModel.index(选中行号, 0)
            if 选中行号的新索引.row() != -1:
                self.listView.selectRow(选中行号)
            else:
                self.listView.selectRow(0)
        else:
            self.listView.removeCurrentItem()
            self.圆满完成()
            self.close()

    def last_item(self):
        """这是给向上箭头调用的, 完成复习不用这个箭头"""
        行号 = self.listView.currentIndex().row() - 1
        总行数 = self.listView.tempModel.rowCount()
        self.listView.selectRow(行号 % 总行数)
        pass

    def next_item(self):
        """这是给向下箭头调用的, 完成复习不用这个箭头"""
        行号 = self.listView.currentIndex().row() + 1
        总行数 = self.listView.tempModel.rowCount()
        self.listView.selectRow(行号 % 总行数)

    def 圆满完成(self):
        self.同时隐藏卡片与视图展示组件()
        self.导航按钮组.hide()
        showInfo(f"roaming of the view: {self.superior.data.gviewdata.name} is finished!")
        pass

    def switch_sidebar_show_hide(self):
        self.导航按钮组.切换收起展开状态()
        self.导航按钮组.更换收起展开按钮图标()
        self.导航按钮组.操作侧边栏隐藏或显示()
        pass

    def 还有结点(self):
        return self.listView.tempModel.rowCount() > 1

    def initEvent(self):
        # btns = self._cardView.revWidget.ease_button
        # [btns[i].clicked.connect(self.item_finish) for i in btns]

        pass

    def closeEvent(self, *args, **kwargs):
        self.superior.roaming = None

    def initUI(self):

        self.layoutH.addWidget(self.listView, stretch=0)
        self.layoutH.addWidget(self.导航按钮组, stretch=0, alignment=AlignmentFlag.AlignBottom)
        self.layoutH.addWidget(self.复习_视图结点展示组件, stretch=1)
        self.layoutH.setContentsMargins(0, 0, 0, 0)
        self.cardView.hide()
        self.复习_视图结点展示组件.hide()
        self.container.setLayout(self.layoutH)
        self.setCentralWidget(self.container)
        self.setWindowTitle(f"roaming review for view of {self.superior.data.gviewdata.name} ")
        self.setMinimumHeight(600)

    def 同时隐藏卡片与视图展示组件(self):
        self.cardView.hide()
        self.复习_视图结点展示组件.hide()

    def 切换到视图组件(self):
        self.cardView.hide()
        self.复习_视图结点展示组件.show()
        pass

    def 切换到卡片组件(self):
        self.cardView.show()
        self.复习_视图结点展示组件.hide()
        pass

    class 导航组件(QWidget):
        收起 = 0
        展开 = 1

        def __init__(self, 上级: "GrapherRoamingPreviewer"):
            super().__init__()
            self.当前侧边栏收起展开状态 = GrapherRoamingPreviewer.导航组件.展开  # 0
            self.上级 = 上级
            self.按钮_下一个 = QPushButton(QIcon(funcs.G.src.ImgDir.bottom_direction), "")
            self.按钮_上一个 = QPushButton(QIcon(funcs.G.src.ImgDir.top_direction), "")
            self.按钮_收起展开 = QPushButton(QIcon(self.获取收起展开的图标()), "")
            self.按钮组 = [self.按钮_上一个, self.按钮_下一个, self.按钮_收起展开]
            提示 = ["last", "next", "sidebar hide/show"]
            响应函数 = [self.上级.last_item, self.上级.next_item, self.上级.switch_sidebar_show_hide]
            垂直布局 = QVBoxLayout()
            [垂直布局.addWidget(按钮) for 按钮 in self.按钮组]
            [self.按钮组[i].setToolTip(提示[i]) for i in range(len(self.按钮组))]
            [self.按钮组[i].clicked.connect(响应函数[i]) for i in range(len(self.按钮组))]
            垂直布局.setContentsMargins(0, 0, 0, 0)
            self.setLayout(垂直布局)

        def 操作侧边栏隐藏或显示(self):
            if self.当前侧边栏收起展开状态 == GrapherRoamingPreviewer.导航组件.展开:
                self.上级.listView.show()
            else:
                self.上级.listView.hide()

        def 获取收起展开的图标(self):
            if self.当前侧边栏收起展开状态 == GrapherRoamingPreviewer.导航组件.展开:
                return funcs.G.src.ImgDir.left_direction
            else:
                return funcs.G.src.ImgDir.right_direction

        def 切换收起展开状态(self):
            if self.当前侧边栏收起展开状态 == GrapherRoamingPreviewer.导航组件.收起:
                self.当前侧边栏收起展开状态 = GrapherRoamingPreviewer.导航组件.展开

            else:
                self.当前侧边栏收起展开状态 = GrapherRoamingPreviewer.导航组件.收起

        def 更换收起展开按钮图标(self):
            self.按钮_收起展开.setIcon(QIcon(self.获取收起展开的图标()))

    class 复习对象_视图结点(QWidget):
        def __init__(self, 上级: "GrapherRoamingPreviewer"):

            super().__init__()
            self.上级 = 上级

            self.按钮1_完成复习 = QPushButton("reviewed")
            self.按钮2_打开视图 = QPushButton("open")
            self.按钮2_打开视图.clicked.connect(self.open_current_view_roaming)
            self.按钮1_完成复习.clicked.connect(self.on_review_completed)
            self.视图信息组合组件 = QWidget()
            self.视图信息组件字典 = models.类型_视图本身模型().创建UI字典()
            self.当前视图数据: "None|GViewData" = None
            self.视图信息表单布局 = QFormLayout()
            self.视图信息组件初始化()
            self.垂直布局 = QVBoxLayout()
            self.垂直布局.addWidget(self.视图信息组合组件)

            Hbox = QHBoxLayout()
            Hbox.addWidget(self.按钮1_完成复习)
            Hbox.addWidget(self.按钮2_打开视图)
            self.垂直布局.addLayout(Hbox)
            self.setLayout(self.垂直布局)

        def on_review_completed(self):
            self.当前视图数据.数据更新.视图复习发生()
            self.上级.更新结点复习(self.当前视图数据.uuid)
            self.上级.item_finish()
            pass

        def open_current_view_roaming(self):
            uuid = self.上级.获取当前结点的编码()
            funcs.Dialogs.open_view(gviewdata=funcs.GviewOperation.load(uuid=uuid))
            g: Grapher = funcs.G.mw_gview[uuid]
            g.toolbar.openRoaming()

        def 视图信息组件初始化(self):
            for 名, 值 in self.视图信息组件字典.items():
                self.视图信息表单布局.addRow(值.数据源.展示名, 值)
            # funcs.Utils.print(self.视图信息组件字典.__str__())
            self.视图信息组合组件.setLayout(self.视图信息表单布局)
            pass

        def 读取视图信息(self):
            视图编号 = self.上级.获取当前结点的编码()
            self.当前视图数据 = funcs.GviewOperation.load(uuid=视图编号)
            视图本身数据 = self.当前视图数据.meta_helper

            for 属性项 in 视图本身数据.属性字典.values():
                if 属性项.可展示:
                    self.视图信息组件字典[属性项.字段名].数据源 = 属性项
                    self.视图信息组件字典[属性项.字段名].给UI赋值(属性项.值)
            pass

    class List(QListView):
        def __init__(self, superior):

            super().__init__()

            self.superior: "GrapherRoamingPreviewer" = superior
            self.tempModel = QStandardItemModel()
            self.setModel(self.tempModel)

            self.initUI()

            self.initData()

            self.initEvent()

        def initEvent(self, ):
            self.selectionModel().selectionChanged.connect(self.handleSelectionChanged)
            pass

        def handleSelectionChanged(self, selected: "QItemSelection", deselected: "QItemSelection"):
            if selected.indexes():
                视图数据 = self.superior.superior.data.gviewdata
                编号 = self.tempModel.itemFromIndex(selected.indexes()[0]).data()
                if 视图数据.nodes[编号][本.结点.数据类型] == 枚举_视图结点类型.卡片:
                    self.superior.切换到卡片组件()
                    self.superior.当前编码 = 编号
                    self.superior.cardView.loadNewCard(common_tools.funcs.CardOperation.GetCard(编号))
                else:
                    self.superior.复习_视图结点展示组件.读取视图信息()
                    self.superior.切换到视图组件()
                    # funcs.Dialogs.open_grapher(gviewdata=funcs.GviewOperation.load(uuid=编号))
                item = self.superior.superior.data.node_dict[编号].item
                self.superior.superior.scene.clearSelection()
                item.setSelected(True)
                self.superior.superior.view.centerOn(item=item)
                # self.superior.superior.load_node()
            else:
                self.superior.同时隐藏卡片与视图展示组件()

        def initUI(self):
            self.setAlternatingRowColors(True)
            self.setMaximumWidth(300)
            self.setSelectionMode(common_tools.compatible_import.QAbstractItemViewSelectMode.ExtendedSelection)
            self.setSelectionBehavior(common_tools.compatible_import.QAbstractItemView.SelectRows)
            self.setEditTriggers(common_tools.compatible_import.QAbstractItemView.NoEditTriggers)
            # self.setCurrentIndex(self.tempModel.index(1,0))
            # self.selectRow(2)

            pass

        def initData(self):
            self.buildData()
            pass

        def buildQueue(self):
            pass

        def buildData(self):

            视图数据 = self.superior.superior.data.gviewdata

            for 结点编号 in self.superior.dueQueue:
                desc = funcs.GviewOperation.获取视图结点描述(视图数据, 结点编号)  # self.superior.superior.data.node_dict[card_id].pair.desc
                item = QStandardItem(desc)
                item.setData(结点编号)
                self.tempModel.appendRow([item])

        def selectRow(self, rownum):
            row = self.tempModel.index(rownum, 0)
            #

            self.setCurrentIndex(row)
            self.selectionModel().clearSelection()
            self.selectionModel().select(self.currentIndex(), QItemSelectionModel.Select)

        def getCurrCardId(self):
            item = self.tempModel.itemFromIndex(self.currentIndex())
            if item:
                return item.data()
            else:
                showInfo("finished!")
                return self.superior.cardView.card().id.__str__()

        def printCurrentRow(self):
            item = self.tempModel.itemFromIndex(self.currentIndex())
            print(f"current row = {item.row()}")

        def removeCurrentItem(self):
            item = self.tempModel.itemFromIndex(self.currentIndex())
            if item:
                self.tempModel.takeRow(item.row())

    pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    testdata = [LinkDataPair("1627401415334", "1"),
                LinkDataPair("1627401415333", "2"),
                LinkDataPair("1627401415332", "3"),
                LinkDataPair("1627401415331", "4"),
                LinkDataPair("1627401415335", "5"),
                LinkDataPair("1627401415336", "6"),
                LinkDataPair("1627401415337", "7"),
                LinkDataPair("1627401415338", "8"),
                LinkDataPair("1227401415335", "9"),
                LinkDataPair("1327401415336", "10"),
                LinkDataPair("1427401415337", "11"),
                LinkDataPair("1527401415338", "12"),

                LinkDataPair("0627401415334", "13"),
                LinkDataPair("2627401415333", "14"),
                LinkDataPair("3627401415332", "15"),
                LinkDataPair("4627401415331", "16"),
                LinkDataPair("5627401415335", "17"),
                LinkDataPair("6627401415336", "18"),
                LinkDataPair("7627401415337", "19"),
                LinkDataPair("8627401415338", "20"),
                LinkDataPair("9227401415335", "21"),
                LinkDataPair("10327401415336", "22"),
                LinkDataPair("11427401415337", "23"),
                LinkDataPair("12527401415338", "24"),
                ]
    p = GViewAdmin()
    p.show()
    sys.exit(app.exec_())
    pass
