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
from dataclasses import dataclass, field

import typing
from enum import Enum, unique
from typing import Optional, Union

from ..imports import *

from aqt.utils import showInfo, tooltip

from ..linkdata_admin import read_card_link_info

if __name__ == "__main__":
    from lib import common_tools

    pass
else:
    from ..imports import common_tools

LinkDataPair = common_tools.objs.LinkDataPair
GraphMode = common_tools.configsModel.GraphMode
GViewData = common_tools.configsModel.GViewData
Translate = common_tools.language.Translate
Struct = common_tools.objs.Struct
funcs = common_tools.funcs
src = common_tools.G.src


class Grapher(QDialog):
    """所有的个性化数据都储存在Entity对象中"""
    on_card_updated = pyqtSignal(object)
    on_card_reviewed = pyqtSignal(str)
    def __init__(self, pair_li: "list[LinkDataPair]" = None, mode=GraphMode.normal, gviewdata: "GViewData" = None):
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose, on=True)
        self.data = self.Entity(self)
        self.data.gviewdata = gviewdata
        self.data.node_dict = pair_li
        if gviewdata:
            self.data.node_dict = [LinkDataPair(card_id, funcs.CardOperation.desc_extract(card_id)) for card_id in gviewdata.nodes.keys() if funcs.CardOperation.exists(card_id)]
        self.data.graph_mode = mode
        self.view = self.View(self)
        self.scene = self.Scene(self)
        self.view.setScene(self.scene)
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
        # if self.data.graph_mode == GraphMode.normal:
        #     self.init_graph_item()
        # elif self.data.graph_mode == GraphMode.view_mode:
        #     self.load_view()

    def card_edit_desc(self, item: "Grapher.ItemRect"):
        text, okPressed = common_tools.compatible_import.QInputDialog.getText(self, "get new description", "", text=item.pair.desc)
        if okPressed:
            item.pair.desc = text
            common_tools.funcs.LinkDataOperation.update_desc_to_db(item.pair)
            common_tools.funcs.CardOperation.refresh()
        pass

    def on_card_updated_handle(self, event):
        for node in self.data.node_dict.values():
            node.pair.update_desc()
            node.item.pair.update_desc()

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
        mode = self.data.graph_mode
        if mode == GraphMode.normal:
            common_tools.G.mw_grapher = None
        elif mode == GraphMode.view_mode:
            node, edge = self.data.node_edge_packup()
            data = GViewData(self.data.gviewdata.uuid, self.data.gviewdata.name, node, edge)
            if funcs.GviewOperation.exists(data):
                funcs.GviewOperation.save(data)
            else:
                correction = QMessageBox.warning(self, "warning", Translate.本视图已被删除_确定退出么, QMessageBox.Yes | QMessageBox.No)
                if correction == QMessageBox.No:
                    a0.ignore()
                    return
            common_tools.G.mw_gview[self.data.gviewdata.uuid] = None
            # common_tools.G.GViewAdmin_window

    def reject(self) -> None:
        self.close()
        super().reject()

    def on_scene_selectionChanged_handle(self):
        self.switch_edge_highlight()

    # view
    def load_view(self, gviewdata=None):
        """从外部读取布局事先确定好的内容
        目前有一个bug, 初始化调用的时候
        """
        LinkDataPair = common_tools.funcs.LinkDataPair
        CardOperation = common_tools.funcs.CardOperation
        if gviewdata is None: gviewdata = self.data.gviewdata
        last_card = ""
        for card_id, posi in gviewdata.nodes.items():
            if card_id not in self.data.node_dict or posi[0] is None:
                pair = LinkDataPair(card_id=card_id, desc=CardOperation.desc_extract(card_id))
                item = self.add_node(pair)
                self.arrange_node(item)
            else:
                item = self.add_node(self.data.node_dict[card_id].pair)
                item.setSelected(True)
                last_card = card_id
                item.setPos(*posi)
        for cardA, cardB in gviewdata.edges:
            # data = read_card_link_info(cardA)
            # if LinkDataPair(card_id=cardB) in data.link_list:
            self.add_edge(cardA, cardB, add_bilink=self.data.graph_mode == GraphMode.normal)
        if last_card: self.view.centerOn(item=self.data.node_dict[last_card].item)
        pass

    def insert(self, pair_li: "list[LinkDataPair]"):
        """根据填入的pair 点亮,聚焦到对应的卡片上"""
        if pair_li is None:
            return
        self.scene.clearSelection()
        for pair in pair_li:
            if pair.card_id not in self.data.node_dict \
                    or not isinstance(self.data.node_dict[pair.card_id], Grapher.Entity.Node):
                funcs.write_to_log_file(pair.todict().__str__(), need_timestamp=True)
                item = self.add_node(pair)
                self.arrange_node(item)
        list(map(lambda x: self.data.node_dict[x.card_id].item.setSelected(True), pair_li))
        card_id = pair_li[-1].card_id
        self.view.centerOn(item=self.data.node_dict[card_id].item)

    def create_view(self, node=None, edge=None):
        name, submitted = funcs.GviewOperation.get_correct_input()
        if not submitted: return
        uuid = funcs.UUID.by_random()
        node, edge = self.data.node_edge_packup()
        data = GViewData(uuid, name, node, edge)
        # 去检查一下scene变大时,item的scene坐标是否会改变
        common_tools.funcs.GviewOperation.save(data)
        common_tools.funcs.Dialogs.open_grapher(gviewdata=data, mode=funcs.GraphMode.view_mode)

    # node

    def add_node(self, pair: "LinkDataPair"):
        """
        add_node 只是单纯地添加, 不会对位置作修改,
        如果你没有位置数据,那就调用默认的 arrange_node函数来排版位置
        如果你有位置数据, 那就用 item自己的setPos
        """
        if pair.card_id not in self.data.node_dict:
            self.data.node_dict = [pair]
        item = self.ItemRect(self, pair)
        self.data.node_dict[pair.card_id].item = item
        self.scene.addItem(item)
        return item

    def load_node(self, pair_li: "list[LinkDataPair]", begin_item=None, selected_as_center=True):
        """load_node从外部直接读取,并且要完成排版任务, 比较复杂 建议用add_node,add_node比较单纯"""
        item_li = []
        last_item = None
        if len(self.data.node_dict) > 0:
            last_item = self.data.node_dict[(list(self.data.node_dict.keys())[-1])].item

        for pair in pair_li:
            if pair.card_id in self.data.node_dict:
                continue
            self.data.node_dict[pair.card_id] = self.data.Node(pair)
            item = self.add_node(pair)  # 我就单纯读
            item_li.append(pair.card_id)
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
        self.load_edges_from_linkdata()

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

    def del_selected_node(self):
        item_li: "list[Grapher.ItemRect]" = self.selected_nodes()
        card_id_li = list(self.data.node_dict.keys())
        edges = self.data.edge_dict
        for item in item_li:
            card_idA = item.pair.card_id
            for card_idB in card_id_li:
                if card_idA in edges and card_idB in edges[card_idA]:
                    self.remove_edge(card_idA, card_idB)
            self.scene.removeItem(item)
            self.data.node_dict.pop(card_idA)

        pass

    def selected_nodes(self):
        item_li: "list[Grapher.ItemRect]" = [item for item in self.scene.selectedItems() if
                                             isinstance(item, Grapher.ItemRect)]

        return item_li

    def load_edges_from_linkdata(self, card_li: "list[str]" = None):
        if self.data.graph_mode == GraphMode.debug_mode:
            return
        if __name__ == "__main__":
            from lib.bilink.imports import common_tools
            pass
        else:
            from ..imports import common_tools
        DB = common_tools.funcs.LinkDataOperation
        if card_li is None:
            card_li = list(self.data.node_dict.keys())
        for card_idA in card_li:
            cardA_dict = DB.read_from_db(card_idA).link_dict
            for card_idB in card_li:
                if card_idB == card_idA:
                    continue
                if card_idB in cardA_dict:
                    self.add_edge(card_idA, card_idB, add_bilink=self.data.graph_mode == GraphMode.normal)

    def update_all_edges_posi(self):
        updated = set()
        for card_idA, card_idB_dict in self.data.edge_dict.items():
            for _, edge in card_idB_dict.items():
                if edge is not None and edge not in updated:
                    edge.update_line()
                    updated.add(edge)

    def switch_edge_highlight(self):
        # noinspection PyTypeChecker
        item_li: "list[Grapher.ItemRect]" = self.scene.selectedItems()
        card_li: "list[str]" = [item.pair.card_id for item in item_li]
        edges = self.data.edge_dict
        modified = set()
        for nodeA in edges.keys():
            for nodeB in edges[nodeA].keys():
                edge = edges[nodeA][nodeB]
                if edge is None:
                    continue
                if edge not in modified:
                    if nodeA in card_li:
                        edge.highlight()
                    else:
                        edge.unhighlight()
                modified.add(edge)

    def add_edge(self, card_idA: "str", card_idB: "str", add_bilink=False):
        """A->B, 反过来不成立"""
        edges = self.data.edge_dict
        if card_idA in edges and card_idB in edges[card_idA] and edges[card_idA][card_idB] is not None:
            return
        itemA = self.data.node_dict[card_idA].item
        itemB = self.data.node_dict[card_idB].item
        edge = self.ItemEdge(self, itemA, itemB)
        # self.data.node_dict[card_idB].edges.append(edge)
        self.data.node_dict[card_idA].edges.append(edge)
        if card_idA not in self.data.edge_dict:  # 如果边集里不存在
            self.data.edge_dict[card_idA] = {}
        self.data.edge_dict[card_idA][card_idB] = edge
        self.scene.addItem(edge)

        if add_bilink:
            self.add_bilink(card_idA, card_idB)

        pass

    def remove_edge(self, card_idA, card_idB, remove_bilink=False):
        edges = self.data.edge_dict
        nodes = self.data.node_dict
        edge = edges[card_idA][card_idB]
        self.scene.removeItem(edges[card_idA][card_idB])
        nodes[card_idA].edges.remove(edge)
        # nodes[card_idB].edges.remove(edge)
        edges[card_idA][card_idB] = None
        if remove_bilink:
            self.remove_bilink(card_idA, card_idB)
        pass

    # bilink

    def remove_bilink(self, card_idA, card_idB):
        common_tools.funcs.LinkDataOperation.unbind(card_idA, card_idB)
        common_tools.funcs.LinkPoolOperation.both_refresh()
        print("remove_bilink")
        pass

    def add_bilink(self, card_idA, card_idB):
        common_tools.funcs.LinkDataOperation.bind(card_idA, card_idB)
        common_tools.funcs.LinkPoolOperation.both_refresh()
        print("add_bilink")
        pass

    # init

    def init_graph_item(self):
        last_card_id: "" = None
        last_item = None
        for card_id, node in self.data.node_dict.items():
            item = self.add_node(node.pair)
            if self.data.graph_mode == GraphMode.view_mode and card_id in self.data.gviewdata.nodes \
                    and self.data.gviewdata.nodes[card_id][0] is not None:
                item.setPos(*self.data.gviewdata.nodes[card_id])
            else:
                self.arrange_node(item)
            last_item = item
        self.update_all_edges_posi()
        if last_item:
            # last_item.setSelected(True)
            self.view.centerOn(item=last_item)
        if self.data.graph_mode == GraphMode.normal:
            self.load_edges_from_linkdata()
        elif self.data.graph_mode == GraphMode.view_mode:
            for cardA, cardB in self.data.gviewdata.edges:
                self.add_edge(cardA, cardB)

    def init_UI(self):
        if self.data.graph_mode == GraphMode.normal:
            self.setWindowTitle("temporary view")
        elif self.data.graph_mode == GraphMode.view_mode:
            self.setWindowTitle("view of " + self.data.gviewdata.name)
        self.setWindowIcon(QIcon(common_tools.G.src.ImgDir.link2))
        self.setWindowFlags(Qt.WindowType.WindowMinMaxButtonsHint | Qt.WindowType.WindowCloseButtonHint)

        self.resize(800, 600)
        Hbox = QHBoxLayout(self)
        Hbox.setContentsMargins(0, 0, 0, 0)
        Hbox.addWidget(self.view)
        self.setLayout(Hbox)
        pass

    def saveAsGroupReviewCondition(self):

        common_tools.funcs.GroupReview.saveGViewAsGroupReviewCondition(self.data.gviewdata.uuid)

    # class

    class Entity:
        default_radius = 180
        default_rect = QRectF(0, 0, 150, 100)

        def __init__(self, superior: "Grapher"):
            self.superior = superior
            self.root = superior
            self.graph_mode = GraphMode.normal
            self.gviewdata: "Optional[GViewData]" = None
            self._node_dict: "Optional[dict[str,Optional[Grapher.Entity.Node]]]" = {}
            self._edge_dict: "Optional[dict[str,dict[str,Optional[Grapher.ItemEdge]]]]" = {}

        @property
        def node_dict(self) -> 'dict[str,Grapher.Entity.Node]':
            return self._node_dict

        @node_dict.setter
        def node_dict(self, pair_li: "list[LinkDataPair]"):
            if pair_li is None:
                return
            for pair in pair_li:
                self._node_dict[pair.card_id] = self.Node(pair)
            self.updateNodeDueAll()
        def updateNodeDue(self, card_id):
            last_, next_ = funcs.CardOperation.getLastNextRev(card_id)
            self.node_dict[card_id].due = next_ <= datetime.datetime.now()

        def updateNodeDueAll(self):
            for card_id in self.node_dict.keys():
                self.updateNodeDue(card_id)

        @property
        def edge_dict(self) -> 'dict[str,dict[str,Optional[Grapher.ItemEdge]]]':
            return self._edge_dict

        def node_edge_packup(self) -> "dict[str,list[Union[float,int],Union[float,int]]],tuple[list[list[str,str]],]":
            """

            """

            def get_edgeinfo_list() -> "list[list[str,str]]":
                edge_list = []
                edge_list2 = []
                for cardA in self.edge_dict.keys():
                    for cardB in self.edge_dict[cardA].keys():
                        if self.edge_dict[cardA][cardB] is not None:
                            edge = [cardA, cardB]
                            if edge not in edge_list:
                                edge_list.append(edge)
                                edge_list2.append([cardA, cardB])
                return edge_list2

            def get_nodeinfo_list() -> 'dict[str,list[Union[float,int],Union[float,int]]]':
                d = {}

                def get_card_id(node: 'Grapher.Entity.Node'):
                    return node.pair.card_id

                def get_posi(node: 'Grapher.Entity.Node'):
                    return [node.item.scenePos().x(), node.item.scenePos().y()]

                list(map(lambda x: d.__setitem__(get_card_id(x), get_posi(x)), self.node_dict.values()))
                return d

            node_info_list = get_nodeinfo_list()
            edge_info_list = get_edgeinfo_list()

            return (node_info_list, edge_info_list)

        @dataclass
        class Node:
            "一个node就是一个结点, 他有图形表示的item, 和数据表示的pair"
            pair: "LinkDataPair"
            due: bool = False
            item: "Optional[Grapher.ItemRect]" = None
            edges: "list[Grapher.ItemEdge]" = field(default_factory=list)

        @dataclass
        class Edge:
            nodes: "set[Grapher.ItemRect]"
            item: "Grapher.ItemEdge"

            def as_card(self) -> 'set':
                return set([int(item.pair.card_id) for item in self.nodes])

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
            self.superior.data.mouse_moved = True
            if event.buttons() == Qt.MouseButton.LeftButton:
                if self.superior.scene.selectedItems() and self.itemAt(event.pos()):
                    self.superior.update_all_edges_posi()
                if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                    choose1 = len(self.superior.scene.selectedItems()) == 1
                    if isinstance(self.draw_line_start_item, Grapher.ItemRect) and choose1:
                        self.draw_line_end_item = self.itemAt(event.pos())
                        line = self.Auxiliary_line.line()
                        p1 = line.p1()#self.draw_line_start_item.mapToScene(self.draw_line_start_item.rect().center())
                        p2 = self.mapToScene(event.pos())
                        rect = self.draw_line_start_item.mapRectToScene(self.draw_line_start_item.rect())
                        # self.draw_line_start_item.mapRectToScene()
                        # p1_1 = common_tools.funcs.Geometry.IntersectPointByLineAndRect(QLineF(p1, p2), rect)
                        # if p1_1 is not None:
                        #     p1 = p1_1
                        line.setP2(p2)
                        line.setP1(p1)
                        self.Auxiliary_line.setLine(line)
                        # print(f"p1={p1}")
                        return

            super().mouseMoveEvent(event)

        def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
            self.superior.data.mouse_moved = False

            if event.buttons() == Qt.MouseButton.LeftButton:
                self.superior.data.mouse_left_clicked = True
                self.superior.data.mouse_right_clicked = False
                if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                    select_1 = len(self.superior.scene.selectedItems()) == 1
                    if isinstance(self.itemAt(event.pos()), Grapher.ItemRect) and select_1:
                        self.draw_line_start_item: "Grapher.ItemRect" = self.itemAt(event.pos())
                        startItemCenter = self.draw_line_start_item.mapToScene(self.draw_line_start_item.rect().center())
                        self.Auxiliary_line.setLine(QLineF(startItemCenter, startItemCenter))
                        # print(self.Auxiliary_line.line().p1())
                        self.superior.scene.addItem(self.Auxiliary_line)
            elif event.buttons() == Qt.MouseButton.RightButton:
                self.superior.data.mouse_left_clicked = False
                self.superior.data.mouse_right_clicked = True

                pass

            if event.buttons() == Qt.MouseButton.RightButton:
                self.setDragMode(common_tools.compatible_import.DragMode.RubberBandDrag)

            super().mousePressEvent(event)

        def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
            self.superior.scene.removeItem(self.Auxiliary_line)
            end_item, begin_item = self.draw_line_end_item, self.draw_line_start_item
            if isinstance(end_item, Grapher.ItemRect) and begin_item != end_item:
                add_bilink = self.superior.data.graph_mode == GraphMode.normal
                self.superior.add_edge(begin_item.pair.card_id, end_item.pair.card_id, add_bilink=add_bilink)
            if not self.itemAt(event.pos()) \
                    and not self.superior.data.mouse_moved \
                    and self.superior.data.mouse_right_clicked:
                self.make_context_menu(event)
            self.draw_line_end_item, self.draw_line_start_item = None, None
            super().mouseReleaseEvent(event)
            self.setDragMode(common_tools.compatible_import.DragMode.ScrollHandDrag)
            self.superior.update()
            self.superior.data.mouse_right_clicked = False
            self.superior.data.mouse_left_clicked = False
            self.superior.data.mouse_moved = False

        def make_context_menu(self, event: QtGui.QMouseEvent):
            pairli = funcs.AnkiLinks.get_card_from_clipboard()
            menu = QMenu()
            menu.addAction(Translate.创建为视图).triggered.connect(lambda: self.superior.create_view(*self.superior.data.node_edge_packup()))
            if len(pairli) > 0:
                menu.addAction(Translate.粘贴卡片).triggered.connect(lambda: self.superior.insert(pairli))
            if self.superior.data.graph_mode==GraphMode.view_mode:
                menu.addAction(Translate.保存当前视图为群组复习条件).triggered.connect(lambda: self.superior.saveAsGroupReviewCondition())
            pos = event.globalPosition() if common_tools.compatible_import.Anki.isQt6 else event.screenPos()
            menu.exec(pos.toPoint())

        pass

    class Scene(QGraphicsScene):
        pass

    class ItemEdge(common_tools.baseClass.Geometry.ArrowLine):
        highlight_pen = QPen(QColor(255, 215, 0), 8.0, PenStyle.DashLine)
        normal_pen = QPen(QColor(127, 127, 127, 160), 8.0, PenStyle.DashLine)
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
            self.setZValue(-10)
            self.setPen(self.normal_pen)

        def update_line(self):
            p1 = self.itemStart.mapToScene(self.itemStart.boundingRect().center())
            p2 = self.itemEnd.mapToScene(self.itemEnd.boundingRect().center())
            rectA = self.itemStart.mapRectToScene(self.itemStart.rect())
            rectB = self.itemEnd.mapRectToScene(self.itemEnd.rect())
            # pA = common_tools.funcs.Geometry.IntersectPointByLineAndRect(QLineF(p1, p2), rectA)
            # pB = common_tools.funcs.Geometry.IntersectPointByLineAndRect(QLineF(p1, p2), rectB)

            # if pA is not None: p1=pA
            # if pB is not None: p2=pB
            line = QLineF(p1, p2)
            self.setLine(line)

        def highlight(self):
            self.setPen(self.highlight_pen)
            self.setZValue(-1)

        def unhighlight(self):
            self.setPen(self.normal_pen)
            self.setZValue(-10)

        def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
            if event.buttons() == Qt.MouseButton.RightButton:
                menu = QMenu()
                remove_bilink = self.superior.data.graph_mode == GraphMode.normal
                menu.addAction(Translate.删除边).triggered.connect(
                        lambda: self.superior.remove_edge(self.itemStart.pair.card_id, self.itemEnd.pair.card_id,
                                                          remove_bilink=remove_bilink))

                pos = event.screenPos()  # if common_tools.compatible_import.Anki.isQt6 else event.screenPosition()
                menu.exec(pos)

            super().mousePressEvent(event)

        pass

    class ItemRect(QGraphicsRectItem):
        class MODE:
            all = 0
            pdf = 1
            intext = 2
            outext = 3

        def __init__(self, superior: "Grapher", pair: "LinkDataPair"):
            super().__init__()

            self.superior = superior
            self.pair: "LinkDataPair" = pair

            self.setPen(QPen(QColor(30, 144, 255)))
            self.setBrush(QBrush(QColor(30, 144, 255)))
            self.setRect(self.superior.data.default_rect)
            self.setFlag(common_tools.compatible_import.QGraphicsRectItemFlags.ItemIsMovable, True)
            self.setFlag(common_tools.compatible_import.QGraphicsRectItemFlags.ItemIsSelectable, True)
            self.setFlag(common_tools.compatible_import.QGraphicsRectItemFlags.ItemSendsGeometryChanges, True)
            self.setAcceptHoverEvents(True)
            w, h = self.boundingRect().width(), self.boundingRect().height()
            self.contextMenuOpened = False
            self.collide_LeftTop = QRectF(0, 0, w / 4, h / 4)
            self.collide_LeftBot = QRectF(0, h * 3 / 4, w / 4, h / 4)
            self.collide_RightTop = QRectF(w * 3 / 4, 0, w / 4, h / 4)
            self.collide_RightBot = QRectF(w * 3 / 4, h * 3 / 4, w / 4, h / 4)
            self.collide_center = QRectF(w * 1 / 4, h * 1 / 4, w / 2, h / 2)
            self.collide_left = QRectF(0, h * 1 / 4, w / 4, h / 2)
            self.collide_right = QRectF(w * 3 / 4, h * 1 / 4, w / 4, h / 2)
            self.collide_top = QRectF(w / 4, 0, w / 2, h / 4)
            self.collide_bottom = QRectF(w / 4, h * 3 / 4, w / 2, h / 4)

        @property
        def node(self):
            return self.superior.data.node_dict[self.pair.card_id]

        def load_linked_card(self, mode=3):
            cardinfo = common_tools.funcs.LinkDataOperation.read_from_db(self.pair.card_id)
            pair_li = [pair for pair in cardinfo.link_list]
            self.superior.load_node(pair_li, begin_item=self)

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

            menu.addAction(Translate.删除).triggered.connect(self.superior.del_selected_node)
            # noinspection PyUnresolvedReferences
            menu.addAction(Translate.修改描述).triggered.connect(lambda: self.superior.card_edit_desc(self))

            pair_li: "list[LinkDataPair]" = [item.pair for item in self.scene().selectedItems()]
            common_tools.menu.maker(common_tools.menu.T.grapher_node_context)(pair_li, menu, self.superior,
                                                                              needPrefix=False)

            def menuCloseEvent():
                self.setSelected(True)
                self.setFlag(common_tools.compatible_import.QGraphicsRectItemFlags.ItemIsMovable, True)
                self.contextMenuOpened = False

            menu.closeEvent = lambda x: menuCloseEvent()
            if self.superior.data.graph_mode == GraphMode.normal:
                loadlinkcard = menu.addMenu("加载链接卡片")
                for name, action in [
                        ("加载全部文外链接卡片", lambda: self.load_linked_card(mode=self.MODE.outext))
                ]:
                    loadlinkcard.addAction(name).triggered.connect(action)
                outtextmenu = loadlinkcard.addMenu("选择文外链接卡片加载")
                link_list = common_tools.funcs.LinkDataOperation.read_from_db(self.pair.card_id).link_list
                shorten = common_tools.funcs.str_shorten

                for pair in link_list:
                    action = lambda pair: lambda: self.superior.load_node([pair], begin_item=self)
                    outtextmenu.addAction(
                            f"""card_id={pair.card_id},desc={shorten(pair.desc)}""").triggered.connect(
                            action(pair)
                    )
            self.contextMenuOpened = True
            self.setFlag(common_tools.compatible_import.QGraphicsRectItemFlags.ItemIsMovable, False)
            return menu

        def mouseDoubleClickEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
            if event.buttons() == Qt.MouseButton.LeftButton:
                common_tools.funcs.Dialogs.open_custom_cardwindow(self.pair.card_id)
            super().mouseDoubleClickEvent(event)

        def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:

            if event.buttons() == Qt.MouseButton.RightButton:
                if event.modifiers() != Qt.KeyboardModifier.ControlModifier:
                    self.make_context_menu().exec(event.screenPos())
            # if not self.contextMenuOpened:
            super().mousePressEvent(event)

            pass

        def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
            self.prepareGeometryChange()
            edges = self.superior.data.node_dict[self.pair.card_id].edges
            for edge in edges:
                edge.update_line()
            # if not self.contextMenuOpened:
            super().mouseMoveEvent(event)

            # print(self.scenePos().__str__())

        def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:

            if not self.contextMenuOpened:
                super().mouseReleaseEvent(event)
                self.setFlag(common_tools.compatible_import.QGraphicsRectItemFlags.ItemIsMovable, True)

        # def drawRedDot(self):


        def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem',
                  widget: typing.Optional[QWidget] = ...) -> None:
            super().paint(painter, option, widget)

            painter.setPen(QColor(50, 205, 50))
            painter.setBrush(QBrush(QColor(50, 205, 50)))
            header_height = 20
            header_rect = QRectF(0, 0, int(self.rect().width()), header_height)
            body_rect = QRectF(0, header_height, int(self.rect().width()), int(self.rect().height()))
            painter.drawRect(header_rect)

            painter.setPen(QColor(255, 255, 255))
            painter.drawText(header_rect.adjusted(5, 5, -5, -5), Qt.TextFlag.TextWordWrap, str(self.pair.card_id))
            painter.drawText(body_rect.adjusted(5, 5, -5, -5), Qt.TextFlag.TextWordWrap, f"""{self.node.pair.desc}""")

            if self.isSelected():
                path = QPainterPath()
                path.addRect(self.rect())
                painter.strokePath(path, Grapher.ItemEdge.highlight_pen)
                self.setZValue(10)
            else:
                self.setZValue(0)

            if self.node.due:
                print("self.node.due")
                painter.setPen(QColor(255, 0, 0))
                painter.setBrush(QBrush(QColor(255, 0, 0)))
                painter.drawEllipse(header_rect.right()-5,0,5,5)

        pass

    # class Item(QGraphicsItem):
    #     def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem', widget: typing.Optional[QWidget] = ...) -> None:
    #     pass


class GViewAdmin(QDialog):
    """视图管理器,实现改名,复制链接,删除,打开"""

    class DisplayState:
        as_tree = 0
        as_list = 1

    def __init__(self):
        super().__init__()
        self.view = self.Tree(self)
        self.bottom = self.Bottom(self)
        self.model = self.Model(self)
        self.view.setModel(self.model)
        self.data: "dict[str,Optional[GViewData]]" = {}
        self.wait_for_delete: "list[str]" = []
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
                [self.model.itemChanged, self.on_model_item_changed_handle],
                [self.view.doubleClicked, self.on_view_doubleclicked_handle],
                [self.view.customContextMenuRequested, self.on_view_contextmenu_handle],

                # [self.view.horizontalHeader().clicked,self.on_horizontal_header_clicked_handle],
        ]).bind()

    def on_view_contextmenu_handle(self, pos):
        item = self.model.itemFromIndex(self.view.indexAt(pos))
        if item is None:
            return
        if item.data(Qt.UserRole) is None:
            tooltip(Translate.请点击叶结点)
            return

        data = item.data(Qt.UserRole)
        menu = self.view.contextMenu = QMenu(self.view)
        menu.addAction(Translate.重命名, ).triggered.connect(lambda: self.on_rename(item))
        menu.addAction(Translate.删除).triggered.connect(lambda: self.on_delete(item))
        menu_copy_as = menu.addMenu(Translate.复制为)
        funcs.MenuMaker.gview_ankilink(menu_copy_as, data)
        menu.popup(QCursor.pos())
        # menu.popup(pos)

    def on_view_doubleclicked_handle(self, index: "QModelIndex"):
        # noinspection PyTypeChecker
        item: "GViewAdmin.Item" = self.model.itemFromIndex(index)
        data: "GViewData" = funcs.GviewOperation.load(gviewdata=item.data(Qt.UserRole))
        if data is None:
            tooltip(Translate.请点击叶结点)
            return
        funcs.Dialogs.open_grapher(gviewdata=data, mode=GraphMode.view_mode)

    def on_horizontal_header_clicked_handle(self):
        print("horizontalHeader clicked")

    def on_model_item_changed_handle(self, item: "GViewAdmin.Item"):
        data: "GViewData" = item.data(Qt.UserRole)
        if not re.match(r"\S", item.text()):
            item.setText(data.name)
            funcs.Utils.tooltip(Translate.视图命名规则)
            return
        data.name = item.text()
        funcs.GviewOperation.update(data)

        pass

    def get_item(self) -> "GViewAdmin.Item":
        indxs = self.view.selectedIndexes()
        if len(indxs) == 0:
            return False
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

    def rebuild(self):
        if self.displaystate == self.DisplayState.as_tree:
            self.build_tree()
        else:
            self.build_list()
        self.view.expandAll()

    def on_rename(self, it=None):
        """由于有两个不同的display所以需要弹出窗口让同学修改"""
        item: "GViewAdmin.Item" = self.get_item() if not it else it
        if not item: return
        data: "GViewData" = item.data(Qt.UserRole)
        newname, submitted = funcs.GviewOperation.get_correct_input(data.name)
        if not submitted: return
        data.name = newname
        self.wait_for_update.add(data)
        self.rebuild()
        pass

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
        self.wait_for_delete.append(data.uuid)
        self.data[data.uuid] = None
        self.rebuild()
        pass

    def init_UI(self):
        self.model.setHorizontalHeaderLabels(["view name"])
        self.setWindowTitle("gview manager")
        self.setContentsMargins(0, 0, 0, 0)
        self.setWindowIcon(QIcon(src.ImgDir.gview_admin))
        self.resize(300, 400)
        self.view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        g_layout = QGridLayout(self)
        g_layout.setContentsMargins(0, 0, 0, 0)
        g_layout.setSpacing(0)
        g_layout.addWidget(self.view, 0, 0, 1, 5)
        g_layout.addWidget(self.bottom, 1, 4, 1, 1)
        self.setLayout(g_layout)

    def init_data(self):
        datas = funcs.GviewOperation.load_all()
        list(map(lambda x: self.data.__setitem__(x.uuid, x), datas))
        self.rebuild()

    def init_model(self):
        self.model.clear()
        self.model.setHorizontalHeaderLabels(["view name"])

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
                    parent.item.appendRow([item])
                    parent.children[nodename] = Struct.TreeNode(item=item, children={})
                parent = parent.children[nodename]
        pass

    def build_list(self):
        self.init_model()
        for data in self.data.values():
            if isinstance(data, GViewData):
                item = self.Item(data.name, data=data)
                self.model.appendRow([item])

        pass

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.save()
        funcs.G.GViewAdmin_window = None

    class Model(QStandardItemModel):
        def addRow(self, data: GViewData):
            item = GViewAdmin.Item(data)
            self.appendRow(item)

    class ItemRole:
        terminal = 0
        nonterminal = 1

    class Item(QStandardItem):
        def __init__(self, name, data: GViewData = None):
            super().__init__(name)
            self.setFlags(self.flags() & ~Qt.ItemFlag.ItemIsSelectable & ~Qt.ItemFlag.ItemIsEditable)
            if data:
                self.setData(data, role=Qt.UserRole)  # 当不设置的时候,返回的是空
                self.setFlags(self.flags() | Qt.ItemFlag.ItemIsSelectable)

    class Tree(QTreeView):
        def __init__(self, superior: 'GViewAdmin'):
            super().__init__()
            self.superior = superior
            self.setParent(superior)

        def init_UI(self):
            self.setSelectionMode(common_tools.compatible_import.QAbstractItemViewSelectMode.SingleSelection)
            self.setDragDropMode(common_tools.compatible_import.DragDropMode.NoDragDrop)
            self.setAcceptDrops(False)

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
            h_layout = QHBoxLayout(self)
            h_layout.setContentsMargins(0, 0, 0, 0)
            self.setContentsMargins(0, 0, 0, 0)
            button_li: "list[QToolButton]" = [self.display_button, self.open_button, self.rename_button, self.delete_button, self.link_button]
            icon_li = [src.ImgDir.tree, src.ImgDir.open, src.ImgDir.rename, src.ImgDir.delete, src.ImgDir.link]
            tooltip_li = ["display as tree", "open", "rename", "delete", "copy link"]
            # self.open_button.setToolTip()
            list(map(lambda x: x.setContentsMargins(0, 0, 0, 0), button_li))
            list(map(lambda x: h_layout.addWidget(x, alignment=AlignmentFlag.AlignRight), button_li))
            list(map(lambda x: x[0].setIcon(QIcon(x[1])), zip(button_li, icon_li)))
            list(map(lambda x: x[0].setToolTip(x[1]), zip(button_li, tooltip_li)))

            self.setLayout(h_layout)


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
