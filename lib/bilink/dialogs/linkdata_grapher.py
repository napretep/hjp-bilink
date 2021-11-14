# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'linkdata_grapher.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2021/8/10 21:18'
"""
import math
import random
import sys
from dataclasses import dataclass, field

import typing
from typing import Optional

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QPointF, QRectF, QLineF, pyqtSignal
from PyQt5.QtGui import QPainterPath, QPainter, QPen, QColor, QBrush, QIcon
from PyQt5.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsItem, QDialog, QHBoxLayout, \
    QGraphicsLineItem, QMenu, QGraphicsRectItem, QWidget, QGraphicsSceneMouseEvent, QStyleOptionGraphicsItem, \
    QApplication
from aqt.utils import showInfo, tooltip

if __name__ == "__main__":
    from lib import common_tools
    pass
else:
    from ..imports import common_tools

LinkDataPair = common_tools.objs.LinkDataPair

class Grapher(QDialog):
    on_card_updated = pyqtSignal(object)
    def __init__(self,pair_li:"list[LinkDataPair]"=None):
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose, on=True)
        self.data = self.Entity(self)
        self.data.node_dict = pair_li
        self.view=self.View(self)
        self.scene = self.Scene(self)
        self.view.setScene(self.scene)
        self.init_UI()
        self.init_graph_item()
        self.all_event = common_tools.objs.AllEventAdmin([
            [self.scene.selectionChanged,self.on_scene_selectionChanged_handle],
            [self.view.verticalScrollBar().valueChanged, self.on_view_verticalScrollBar_valueChanged_handle],
            [self.view.horizontalScrollBar().valueChanged, self.on_view_horizontalScrollBar_valueChanged_handle],
            [self.on_card_updated,self.on_card_updated_handle],
        ]).bind()
    # event

    def on_card_updated_handle(self,event):
        for node in self.data.node_dict.values():
            node.pair.update_desc()
            node.item.pair.update_desc()

    def on_view_verticalScrollBar_valueChanged_handle(self,value):
        rect = self.view.sceneRect()
        if value == self.view.horizontalScrollBar().maximum():
            rect.setRight(rect.right() + 50)
        elif value == self.view.horizontalScrollBar().minimum():
            rect.setLeft(rect.left() - 50)
        self.view.setSceneRect(rect)
        # print("on_view_verticalScrollBar_valueChanged_handle")
        pass

    def on_view_horizontalScrollBar_valueChanged_handle(self,value):
        rect = self.view.sceneRect()
        if value == self.view.verticalScrollBar().maximum():
            rect.setBottom(rect.bottom() + 50)
            # self.pdfview.setSceneRect(rect.x(), rect.y(), rect.width(), rect.height() + 10)
        elif value <= self.view.verticalScrollBar().minimum() + 1:
            rect.setTop(rect.top() - 50)
            # self.pdfview.verticalScrollBar().setMinimum(self.pdfview.verticalScrollBar().value()-50)
        self.view.setSceneRect(rect)
        pass

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:

        common_tools.G.mw_grapher=None

    def reject(self) -> None:
        self.close()
        super().reject()

    def on_scene_selectionChanged_handle(self):
        print("on_scene_selectionChanged_handle")
        self.switch_edge_highlight()

    # node

    def add_node(self,pair:"LinkDataPair"):
        item = self.ItemRect(self,pair)
        self.data.node_dict[pair.card_id].item=item
        self.scene.addItem(item)
        return item

    def load_node(self,pair_li:"list[LinkDataPair]",begin_item=None,selected_as_center=True):
        item_li = []
        last_item = None
        if len(self.data.node_dict)>0:
            last_item = self.data.node_dict[(list(self.data.node_dict.keys())[-1])].item

        for pair in pair_li:
            if pair.card_id in self.data.node_dict:
                continue
            self.data.node_dict[pair.card_id]=self.data.Node(pair)
            item = self.add_node(pair)
            item_li.append(pair.card_id)
            if begin_item:
                self.arrange_node(item,begin_item)
            elif selected_as_center:
                self.arrange_node(item)
            else:
                self.arrange_node(item,last_item)
                begin_item = item
            last_item = item
        if last_item:
            self.view.centerOn(last_item)
        self.load_edges_from_linkdata()

    def arrange_node(self,new_item:"Grapher.ItemRect",center_item=None):
        def get_random_p(center_item,radius,part):
            total = radius / self.data.default_radius * 6
            a_part = 360/total
            angle = (part*a_part) / 180 * math.pi
            x, y = math.cos(angle) * radius, math.sin(angle) * radius
            center_p = center_item.pos() if center_item else QPointF(0,0)
            p = center_p + QPointF(x, y)
            return p
        if center_item is None and len(self.data.node_dict)>0:
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
            new_item.setPos(get_random_p(center_item,radius,count))
            if new_item.collidingItems():
                print("重叠")
            else:
                break
            count+=1
            if count == 6*radius/self.data.default_radius:
                radius+=self.data.default_radius
                count = 0


    def hide_selected_node(self):
        item_li: "list[Grapher.ItemRect]" = self.selected_nodes()
        card_id_li = list(self.data.node_dict.keys())
        edges = self.data.edge_dict
        for item in item_li:
            card_idA = item.pair.card_id
            for card_idB in card_id_li:
                if card_idA in edges and  card_idB in edges[card_idA]:
                    self.remove_edge(card_idA,card_idB)
            self.scene.removeItem(item)
            del self.data.node_dict[card_idA]

        pass

    def selected_nodes(self):
        item_li: "list[Grapher.ItemRect]" = [item for item in self.scene.selectedItems() if
                                             isinstance(item, Grapher.ItemRect)]

        return item_li
    # egde

    def load_edges_from_linkdata(self,card_li:"list[str]"=None):
        if __name__ == "__main__":
            from lib.bilink.imports import common_tools
            pass
        else:
            from ..imports import common_tools
        DB = common_tools.funcs.LinkDataOperation
        if card_li is None:
            card_li = list(self.data.node_dict.keys())
        for card_idA in card_li:
            cardA_dict = DB.read(card_idA).link_dict
            for card_idB in card_li:
                if card_idB==card_idA:
                    continue
                if card_idB in cardA_dict:
                    self.add_edge(card_idA,card_idB)

    def update_all_edges_posi(self):
        updated=set()
        for card_idA,card_idB_dict in self.data.edge_dict.items():
            for _,edge in card_idB_dict.items():
                if edge is not None and edge not in updated:
                    edge.update_line()
                    updated.add(edge)


    def switch_edge_highlight(self):
        # noinspection PyTypeChecker
        item_li: "list[Grapher.ItemRect]" = self.scene.selectedItems()
        card_li: "list[str]" = [item.pair.card_id for item in item_li]
        edges = self.data.edge_dict
        modified = set()
        for cardA, cardB_edge_dict in edges.items():
            for cardB, edge in cardB_edge_dict.items():
                if edge not in modified:
                    if cardA in card_li or cardB in card_li:
                        edge.highlight()
                    else:
                        edge.unhighlight()
                modified.add(edge)

    def add_edge(self,card_idA:"str",card_idB:"str",add_bilink=False):
        edges=self.data.edge_dict
        if card_idA in edges and card_idB in edges[card_idA] and edges[card_idA][card_idB] is not None:
            return
        itemB=self.data.node_dict[card_idB].item
        itemA=self.data.node_dict[card_idA].item
        edge=self.ItemEdge(self,itemA,itemB)
        self.data.node_dict[card_idB].edges.append(edge)
        self.data.node_dict[card_idA].edges.append(edge)
        if card_idB not in self.data.edge_dict:
            self.data.edge_dict[card_idB]={}
        self.data.edge_dict[card_idB][card_idA]=edge
        if card_idA not in self.data.edge_dict:
            self.data.edge_dict[card_idA] = {}
        self.data.edge_dict[card_idA][card_idB] = edge
        self.scene.addItem(edge)

        if add_bilink:
            self.add_bilink(card_idA,card_idB)

        pass


    def remove_edge(self,card_idA,card_idB,remove_bilink=False):
        edges = self.data.edge_dict
        nodes = self.data.node_dict
        edge=edges[card_idA][card_idB]
        self.scene.removeItem(edges[card_idA][card_idB])
        nodes[card_idA].edges.remove(edge)
        nodes[card_idB].edges.remove(edge)
        del edges[card_idA][card_idB]
        del edges[card_idB][card_idA]
        if remove_bilink:
            self.remove_bilink(card_idA,card_idB)
        pass

    # bilink

    def remove_bilink(self,card_idA,card_idB):
        common_tools.funcs.LinkDataOperation.unbind(card_idA, card_idB)
        common_tools.funcs.LinkPoolOperation.both_refresh()
        print("remove_bilink")
        pass

    def add_bilink(self,card_idA,card_idB):
        common_tools.funcs.LinkDataOperation.bind(card_idA, card_idB)
        common_tools.funcs.LinkPoolOperation.both_refresh()
        print("add_bilink")
        pass

    # init

    def init_graph_item(self):
        last_card_id:""=None
        last_item = None
        for card_id,node in self.data.node_dict.items():
            item = self.add_node(node.pair)
            #     self.add_edge(last_card_id,card_id)
            self.arrange_node(item)
            last_item = item
        self.update_all_edges_posi()
        if last_item:
            # last_item.setSelected(True)
            self.view.centerOn(last_item)
        if not __name__ == "__main__":
            self.load_edges_from_linkdata()

    def init_UI(self):
        self.setWindowTitle("link data Grapher")
        self.setWindowIcon(QIcon(common_tools.G.src.ImgDir.link2))
        self.setWindowFlags(Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        self.resize(800,600)
        Hbox = QHBoxLayout(self)
        Hbox.setContentsMargins(0,0,0,0)
        Hbox.addWidget(self.view)
        self.setLayout(Hbox)
        pass



    # class

    class Entity:
        default_radius = 180
        default_rect = QRectF(0, 0, 150, 100)
        def __init__(self,superior:"Grapher"):
            self.superior = superior
            self.root=superior
            self._node_dict:"Optional[dict[str,Optional[Grapher.Entity.Node]]]"= {}
            self._edge_dict:"Optional[dict[str,dict[str,Optional[Grapher.ItemEdge]]]]"={}

        @property
        def node_dict(self)->'dict[str,Grapher.Entity.Node]':
            return self._node_dict

        @node_dict.setter
        def node_dict(self,pair_li:"list[LinkDataPair]"):
            for pair in pair_li:
                self._node_dict[pair.card_id]=self.Node(pair)

        @property
        def edge_dict(self):
            return self._edge_dict


        @dataclass
        class Node:
            pair:"LinkDataPair"
            item:"Optional[Grapher.ItemRect]"=None
            edges:"list[Grapher.ItemEdge]"=field(default_factory=list)

        @dataclass
        class Edge:
            nodes:"set[Grapher.ItemRect]"
            item:"Grapher.ItemEdge"

    class View(QGraphicsView):
        def __init__(self,parent:"Grapher"):
            super().__init__(parent)
            self.ratio = 1
            self.superior = parent
            self.setDragMode(self.ScrollHandDrag)
            self.setRenderHints(QPainter.Antialiasing |  # 抗锯齿
                                QPainter.HighQualityAntialiasing |  # 高精度抗锯齿
                                QPainter.SmoothPixmapTransform)  # 平滑过渡 渲染设定
            self.setViewportUpdateMode(self.FullViewportUpdate)
            self.Auxiliary_line:"Optional[QGraphicsLineItem]" = QGraphicsLineItem()
            self.Auxiliary_line.setZValue(-1)
            self.Auxiliary_line.setPen(Grapher.ItemEdge.normal_pen)
            self.clicked_pos:"Optional[QPointF]" = None
            self.draw_line_start_item :"Optional[Grapher.ItemRect]" = None
            self.draw_line_end_item: "Optional[Grapher.ItemRect]" = None

        def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:

            if event.buttons() == Qt.LeftButton :
                if self.superior.scene.selectedItems() and self.itemAt(event.pos()):
                    self.superior.update_all_edges_posi()
                if event.modifiers() == Qt.ControlModifier:
                    choose1=len(self.superior.scene.selectedItems())==1
                    if isinstance(self.draw_line_start_item, Grapher.ItemRect) and choose1:
                        self.draw_line_end_item = self.itemAt(event.pos())
                        line = self.Auxiliary_line.line()
                        line.setP2(self.mapToScene(event.pos()))
                        self.Auxiliary_line.setLine(line)
                        return

            super().mouseMoveEvent(event)



        def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
            if event.buttons() == Qt.LeftButton:
                if event.modifiers() == Qt.ControlModifier:
                    select_1 = len(self.superior.scene.selectedItems())==1
                    if isinstance(self.itemAt(event.pos()), Grapher.ItemRect) and select_1:
                        # noinspection PyTypeChecker
                        self.draw_line_start_item:"Grapher.ItemRect" = self.itemAt(event.pos())
                        # self.draw_line_start_item.setFlag(self.draw_line_start_item.ItemIsMovable,False)
                        center =self.draw_line_start_item.mapToScene(self.draw_line_start_item.rect().center())
                        self.Auxiliary_line.setLine(QLineF(center,center))
                        self.superior.scene.addItem(self.Auxiliary_line)
                pass

            if event.buttons() == Qt.RightButton:
                self.setDragMode(QGraphicsView.RubberBandDrag)

            super().mousePressEvent(event)

        def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
            self.superior.scene.removeItem(self.Auxiliary_line)
            end_item,begin_item = self.draw_line_end_item,self.draw_line_start_item
            if isinstance(end_item,Grapher.ItemRect) and begin_item != end_item:
                self.superior.add_edge(begin_item.pair.card_id,end_item.pair.card_id,add_bilink=True)
            self.draw_line_end_item, self.draw_line_start_item = None,None
            super().mouseReleaseEvent(event)
            self.setDragMode(self.ScrollHandDrag)

        pass

    class Scene(QGraphicsScene):




        pass

    class ItemEdge(QGraphicsLineItem):
        highlight_pen = QPen(QColor(255,215,0), 6.0, Qt.DashLine)
        normal_pen = QPen(QColor(127, 127, 127), 6.0, Qt.DashLine)
        pdflink_pen = QPen(QColor(255, 255,127), 6.0, Qt.DashLine)
        intextlink_pen = QPen(QColor(255, 255,127), 6.0, Qt.DashLine)
        normal,pdflink,intextlink = 0,1,2
        def __init__(self,superior:"Grapher",itemA:"Grapher.ItemRect",itemB:"Grapher.ItemRect",edge_type=0):
            super().__init__()
            self.edge_type=edge_type
            self.superior = superior
            self.itemA:"Grapher.ItemRect"=itemA
            self.itemB:"Grapher.ItemRect"=itemB
            self.update_line()
            self.setZValue(-1)
            self.setPen(self.normal_pen)

        def update_line(self):

            p1 = self.itemA.mapToScene(self.itemA.boundingRect().center())
            p2 = self.itemB.mapToScene(self.itemB.boundingRect().center())
            line = QLineF(p1,p2)

            self.setLine(line)

        def highlight(self):
            self.setPen(self.highlight_pen)

        def unhighlight(self):
            self.setPen(self.normal_pen)


        def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
            if event.buttons() == Qt.RightButton:
                menu = QMenu()
                menu.addAction("删除边").triggered.connect(
                    lambda: self.superior.remove_edge(self.itemA.pair.card_id, self.itemB.pair.card_id,remove_bilink=True))
                menu.exec(event.screenPos())
            super().mousePressEvent(event)

        pass

    class ItemRect(QGraphicsRectItem):
        class MODE:
            all=0
            pdf=1
            intext=2
            outext=3

        def __init__(self,superior:"Grapher",pair:"LinkDataPair"):
            super().__init__()

            self.superior=superior
            self.pair:"LinkDataPair"=pair
            self.setPen(QPen(QColor(30, 144, 255)))
            self.setBrush(QBrush(QColor(30, 144, 255)))
            self.setRect(self.superior.data.default_rect)
            self.setFlag(self.ItemIsMovable, True)
            self.setFlag(self.ItemIsSelectable, True)
            self.setFlag(self.ItemSendsGeometryChanges, True)
            self.setAcceptHoverEvents(True)
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

        # def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        #     super().mousePressEvent(event)

        def load_linked_card(self,mode=3):
            cardinfo = common_tools.funcs.LinkDataOperation.read(self.pair.card_id)
            pair_li = [ pair for pair in cardinfo.link_list]
            self.superior.load_node(pair_li,begin_item=self)

        def collide_handle(self,item_li:"list[Grapher.ItemRect]"=None):
            if item_li is None:
                item_li = self.get_collide_rect()

            myL,myR,myT,myB=self.rect().left(),self.rect().right(),self.rect().top(),self.rect().bottom()

            for item in  item_li :
                L,R,T,B = item.rect().left(),item.rect().right(),item.rect().top(),item.rect().bottom()

                if myL<R:# item在左边
                    item.moveBy(myL-R,0)
                elif myR>L:# item在右边
                    item.moveBy(myR-L, 0)
                elif myB>T:# item在下边
                    item.moveBy(0,myB-T)
                elif myT<B:# item在上边
                    item.moveBy(0,myT-B)
        def get_collide_rect(self):
            return [ i for i in self.collidingItems() if isinstance(i,Grapher.ItemRect)]

        def check_collide_rect_position(self,item:"Grapher.ItemRect"):
            target = self.mapFromScene(item.pos())

        def mouseDoubleClickEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
            if event.buttons()==Qt.LeftButton:
                common_tools.funcs.Dialogs.open_custom_cardwindow(self.pair.card_id)
            super().mouseDoubleClickEvent(event)

        def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
            # if event.buttons() == Qt.LeftButton:
            #     if event.modifiers() == Qt.ControlModifier:
            #         self.setFlag(self.ItemIsMovable, False)
            #         return
            if event.buttons() == Qt.RightButton:
                if event.modifiers()!=Qt.ControlModifier:
                    self.setSelected(True)
                    self.setFlag(self.ItemIsMovable,False)
                    menu = QMenu()
                    menu.addAction("选中隐藏").triggered.connect(self.superior.hide_selected_node)
                    # noinspection PyUnresolvedReferences
                    pair_li:"list[LinkDataPair]" = [ item.pair for item in self.scene().selectedItems()]
                    common_tools.menu.maker(common_tools.menu.T.grapher_node_context)(pair_li,menu,self.superior,needPrefix=False)
                    menu.closeEvent = lambda x:self.setSelected(True)
                    loadlinkcard=menu.addMenu("加载链接卡片")
                    for name,action in [
                      # ("加载全部链接卡片",lambda: self.superior.load_linkcard(mode=self.MODE.all)),
                      # ("加载全部PDF链接卡片", lambda: self.superior.load_linkcard(mode=self.MODE.pdf)),
                      # ("加载全部文内链接卡片", lambda: self.superior.load_linkcard(mode=self.MODE.intext)),
                      ("加载全部文外链接卡片", lambda: self.load_linked_card(mode=self.MODE.outext))
                    ]:
                        loadlinkcard.addAction(name).triggered.connect(action)

                    # pdflinkmenu=loadlinkcard.addMenu("选择PDF链接卡片")
                    # intextmenu=loadlinkcard.addMenu("选择文内链接卡片")
                    outtextmenu=loadlinkcard.addMenu("选择文外链接卡片加载")
                    link_list = common_tools.funcs.LinkDataOperation.read(self.pair.card_id).link_list
                    shorten = common_tools.funcs.str_shorten

                    for pair in link_list:
                        action =lambda pair: lambda : self.superior.load_node([pair],begin_item=self)
                        outtextmenu.addAction(f"""card_id={pair.card_id},desc={shorten(pair.desc)}""").triggered.connect(
                            action(pair)
                        )
                    menu.exec(event.screenPos())
                    return

            super().mousePressEvent(event)

            pass

        def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
            # self.collide_handle()
            self.prepareGeometryChange()
            edges = self.superior.data.node_dict[self.pair.card_id].edges
            for edge in edges:
                edge.update_line()
            super().mouseMoveEvent(event)

        def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
            super().mouseReleaseEvent(event)
            self.setFlag(self.ItemIsMovable,True)


        def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem',
                  widget: typing.Optional[QWidget] = ...) -> None:
            super().paint(painter, option, widget)
            self.prepareGeometryChange()  # 这个 非常重要. https://www.cnblogs.com/ybqjymy/p/13862382.html

            # painter.setFont(QFont('SimSun', pointSize=15, weight=300))
            painter.setPen(QColor(50, 205, 50))
            painter.setBrush(QBrush(QColor(50, 205, 50)))
            header_height = 20
            header_rect = QRectF(0,0, int(self.rect().width()), header_height)
            body_rect = QRectF(0,header_height, int(self.rect().width()), int(self.rect().height()))
            painter.drawRect(header_rect)
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(header_rect.adjusted(5,5,-5,-5),Qt.TextWordWrap,self.pair.card_id)
            painter.drawText(body_rect.adjusted(5,5,-5,-5), Qt.TextWordWrap, f"""{self.pair.desc}""")

            if self.isSelected():
                path = QPainterPath()
                path.addRect(self.rect())
                painter.strokePath(path,Grapher.ItemEdge.highlight_pen)
                self.setZValue(10)
            else:
                self.setZValue(0)



        pass


    # class Item(QGraphicsItem):
    #     def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem', widget: typing.Optional[QWidget] = ...) -> None:
    #     pass

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
    p = Grapher(testdata)
    p.show()
    sys.exit(app.exec_())
    pass