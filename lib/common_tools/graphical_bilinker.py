# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'graphical_linker.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2023/2/17 14:01'
"""
import math
import typing
from dataclasses import dataclass, field
from typing import Optional

from .compatible_import import *
from . import funcs, baseClass, language

本 = baseClass.枚举命名
译 = language.Translate
LinkDataPair = funcs.objs.LinkDataPair


class VisualBilinker(QMainWindow):
    """TempGraph是临时视图, 专门用来添加全局链接的.
    """
    on_card_updated = pyqtSignal(object)

    def __init__(self, pair_li: "list[LinkDataPair]" = None, ):  # 直接导入卡片描述对儿

        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, on=True)
        self.data = self.Entity(self)
        self.data.node_dict = pair_li
        self.scene = self.Scene(self)
        self.view = self.View(self)
        self.view.setScene(self.scene)
        self.toolbar = self.ToolBar(self)
        r = self.rect()
        self.scene.setSceneRect(-float(r.width() / 2), -float(r.height() / 2), float(r.width() * 4),
                                float(r.height() * 4))
        self.init_UI()
        self.all_event = funcs.objs.AllEventAdmin([
                [self.scene.selectionChanged, self.on_scene_selectionChanged_handle],
                [self.view.verticalScrollBar().valueChanged, self.on_view_verticalScrollBar_valueChanged_handle],
                [self.view.horizontalScrollBar().valueChanged, self.on_view_horizontalScrollBar_valueChanged_handle],
                # [self.on_card_updated, self.on_card_updated_handle],
        ]).bind()
        self.init_graph_item()

    def card_edit_desc(self, item: "VisualBilinker.ItemRect"):
        结果 = funcs.组件定制.长文本获取(funcs.CardOperation.desc_extract(item.索引), "get new description", "",)
        if 结果:
            item.node.desc=结果[0]
            funcs.GlobalLinkDataOperation.update_desc_to_db(LinkDataPair(item.索引, 结果[0]))
            funcs.CardOperation.refresh()
        pass

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
        funcs.G.mw_grapher = None

    def close(self):
        self.scene.blockSignals(True)
        super().close()

    def reject(self) -> None:
        self.close()
        super().reject()

    def on_scene_selectionChanged_handle(self):
        self.switch_edge_highlight()


    def create_view(self):
        name, submitted = funcs.GviewOperation.get_correct_view_name_input()
        if not submitted:
            return
        nodes, edges = self.data.node_edge_packup()
        uuid = funcs.GviewOperation.create(nodes, edges, name)
        funcs.Dialogs.open_view(gviewdata=funcs.GviewOperation.load(uuid))

    # node
    def create_node(self, pair: "LinkDataPair|str"):
        """
        create_node 只是单纯地添加, 不会对位置作修改,
        如果你没有位置数据,那就调用默认的 arrange_node函数来排版位置
        如果你有位置数据, 那就用 item自己的setPos
        注意, create_node, 添加的是view中的图形结点, 请在外部完成gviewdata中数据的添加.
        """
        card_id = pair if type(pair) == str else pair.card_id
        if card_id not in self.data.node_dict:
            self.data.node_dict = [card_id]
            item = self.ItemRect(self, card_id)
            self.data.node_dict[card_id].item = item
            self.scene.addItem(item)
        elif self.data.node_dict[card_id] is None or self.data.node_dict[card_id].item is None:
            item = self.ItemRect(self, card_id)
            self.data.node_dict[card_id].item = item
            self.scene.addItem(item)
        else:
            raise ValueError("未知情况")
        return item

    def load_node(self, pair_li: "list[LinkDataPair|str|None]" = None, begin_item=None, selected_as_center=True):
        """
        load_node 2023年1月20日05:48:58 目前暂时针对card结点使用, 不针对view结点使用
        load_node从外部直接读取,并且要完成排版任务, 比较复杂 建议用create_node,create_node比较单纯"""
        if pair_li is None:
            return
        item_li = []
        last_item = None

        if len(self.data.node_dict) > 0:
            last_item = self.data.node_dict[(list(self.data.node_dict.keys())[-1])].item
        for pair in pair_li:
            card_id: "str" = pair if type(pair) == str else pair.card_id
            if card_id in self.data.node_dict:
                continue
            else:
                self.data.node_dict[card_id] = self.data.Node(card_id)

                item = self.create_node(card_id)  # 我就单纯读
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
        self.load_edges_from_linkdata()

        # self.data.updateNodeDueAll()

    def arrange_node(self, new_item: "VisualBilinker.ItemRect", center_item=None):
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
        item_li: "list[VisualBilinker.ItemRect]" = self.selected_nodes()
        # card_id_li = list(self.data.node_dict.keys())
        # edges = self.data.edge_dict
        for item in item_li:
            self.remove_node(item)

        pass

    def selected_nodes(self):
        item_li: "list[VisualBilinker.ItemRect]" = [item for item in self.scene.selectedItems() if isinstance(item, VisualBilinker.ItemRect)]

        return item_li

    def load_edges_from_linkdata(self, card_li: "list[str]" = None):

        DB = funcs.GlobalLinkDataOperation
        if card_li is None:
            card_li = list(self.data.node_dict.keys())
        for card_idA in card_li:
            cardA_dict = DB.read_from_db(card_idA).link_dict
            for card_idB in card_li:
                if card_idB == card_idA:
                    continue
                if card_idB in cardA_dict:
                    self.add_edge(card_idA, card_idB, add_bilink=False)

    def update_all_edges_posi(self):
        updated = set()

        for card_idA, card_idB_dict in self.data.edge_dict.items():
            for card_idB, edge in card_idB_dict.items():
                if edge is not None and f"{card_idA},{card_idB}" not in updated:
                    edge.item.update_line()
                    updated.add(f"{card_idA},{card_idB}")

    def switch_edge_highlight(self):
        # noinspection PyTypeChecker
        # item_li: "list[Grapher.ItemRect]" = self.selected_nodes()  # item for item in self.scene.selectedItems() if isinstance(item,Grapher.ItemRect)]
        card_li: "list[str]" = [item.索引 for item in self.selected_nodes()]
        edges = self.data.edge_dict
        modified = set()
        for nodeA in edges.keys():
            for nodeB in edges[nodeA].keys():
                edge = edges[nodeA][nodeB]
                if edge is None:
                    continue
                边结点 = ",".join(edge.item.获取关联的结点())
                if 边结点 not in modified:
                    if nodeA in card_li:
                        edge.item.highlight()
                    else:
                        edge.item.unhighlight()
                modified.add(边结点)

    def add_edge(self, A: "str", B: "str", add_bilink=False, 描述=""):
        """A->B, 反过来不成立
        add_bilink 用来判断是否要修改全局链接.
        """
        def fun(card_idA: "str", card_idB: "str", add_bilink=False, 描述=""):
            edges = self.data.edge_dict
            if card_idA in edges and card_idB in edges[card_idA] and edges[card_idA][card_idB] is not None:
                return
            nodeA = self.data.node_dict[card_idA]
            nodeB = self.data.node_dict[card_idB]

            edgeItem = self.ItemEdge(self, nodeA.item, nodeB.item)
            # self.data.node_dict[card_idB].edges.append(edge)

            if card_idA not in self.data.edge_dict:  # 如果边集里不存在
                self.data.edge_dict[card_idA] = {}
            self.data.edge_dict[card_idA][card_idB] = self.data.Edge(item=edgeItem, nodes=[nodeA, nodeB], 描述=描述)
            self.data.node_dict[card_idA].edges.append(self.data.edge_dict[card_idA][card_idB])
            self.scene.addItem(edgeItem)

        fun(A,B)
        fun(B,A)

        if add_bilink:
            self.add_bilink(A, B)
        # self.add_edge(card_idB, card_idA)
        pass

    def remove_edge(self, card_idA, card_idB, remove_globalLink=False):
        """
        remove_globalLink 用来判断是否要修改全局链接.
        """
        edges = self.data.edge_dict
        nodes = self.data.node_dict
        edge = edges[card_idA][card_idB]
        back_edge = edges[card_idB][card_idA]
        if edge:
            self.scene.removeItem(edge.item)
            nodes[card_idA].safe_remove(edge)
            edge.item.hide()
        if back_edge:
            self.scene.removeItem(back_edge.item)
            nodes[card_idA].safe_remove(back_edge)
            back_edge.item.hide()
        # nodes[card_idB].edges.remove(edge)
        edges[card_idA][card_idB] = None
        edges[card_idB][card_idA] = None
        if remove_globalLink:
            self.remove_globalLink(card_idA, card_idB)
        pass

    # bilink
    def remove_node(self, item: "VisualBilinker.ItemRect|str"):
        if type(item)==str:
            item = self.data.node_dict[item].item
        card_id_li = self.data.node_dict.keys()
        edges = self.data.edge_dict
        card_idA = item.索引
        for card_idB in card_id_li:
            if card_idB == card_idA: continue
            if card_idA in edges and card_idB in edges[card_idA]:
                self.remove_edge(card_idA, card_idB) # 此时移除就同时移除双向
            # elif card_idB in edges and card_idA in edges[card_idA]:
            #     self.remove_edge(card_idB, card_idA)

        self.scene.removeItem(item)
        self.data.node_dict.pop(card_idA)

    def remove_globalLink(self, card_idA, card_idB):
        """globallink就是全局的链接"""
        funcs.GlobalLinkDataOperation.unbind(card_idA, card_idB)
        funcs.LinkPoolOperation.both_refresh()
        print("remove_globalLink")
        pass

    def add_bilink(self, card_idA, card_idB):
        funcs.GlobalLinkDataOperation.bind(card_idA, card_idB)
        funcs.LinkPoolOperation.both_refresh()
        print("add_bilink")
        pass

    # init

    def init_graph_item(self):
        """用于初始化"""
        last_card_id: "" = None
        last_item = None
        for card_id, node in self.data.node_dict.items():
            item = self.create_node(card_id)
            self.arrange_node(item)
            last_item = item
        self.update_all_edges_posi()
        if last_item:
            self.view.centerOn(item=last_item)
        self.load_edges_from_linkdata()


    def init_UI(self):
        self.setWindowTitle("VISUAL bilinker")
        self.setWindowIcon(QIcon(funcs.G.src.ImgDir.box))
        self.setWindowFlags(Qt.WindowType.WindowMinMaxButtonsHint | Qt.WindowType.WindowCloseButtonHint)

        self.resize(800, 600)
        self.setCentralWidget(self.view)
        self.addToolBar(self.toolbar)

        self.scene.selectionChanged.connect(self.toolbar.checkAction)
        self.scene.setBackgroundBrush(QColor(143,188,143))
        pass


    class Entity:

        """Entity的价值在于把数据独立出来,itemrect和itemedge只用管展示的部分, 数据保存在entity中"""
        default_radius = 180
        default_rect = QRectF(0, 0, 150, 100)

        def __init__(self, superior: "VisualBilinker"):
            self.superior = superior
            self.root = superior
            # self.graph_mode = GraphMode.normal
            # self.gviewdata: Optional[GViewData] = None
            self._node_dict: "Optional[dict[str,Optional[VisualBilinker.Entity.Node]]]" = {}
            self._edge_dict: "Optional[dict[str,dict[str,Optional[VisualBilinker.Entity.Edge]]]]" = {}
            self.currentSelectedEdge: "list[VisualBilinker.ItemEdge]" = []
            self.state = VisualBilinker.Entity.State()

        @property
        def node_dict(self) -> 'dict[str,VisualBilinker.Entity.Node]':
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
            # if not G.ISLOCALDEBUG:
            #     self.updateNodeDueAll()



        @property
        def edge_dict(self) -> 'dict[str,dict[str,Optional[VisualBilinker.Entity.Edge]]]':
            return self._edge_dict

        def node_edge_packup(self):
            """
            这是为了获取边与顶点的最新信息, 然后打包存储
            """

            def get_edgeinfo_list():
                新边集 = {}
                for cardA in self.edge_dict.keys():
                    for cardB in self.edge_dict[cardA].keys():
                        if self.edge_dict[cardA][cardB] is not None and self.edge_dict[cardA][cardB].item is not None:
                            边 = f"{cardA},{cardB}"
                            新边集[边]=funcs.GviewOperation.默认视图边数据模板()
                return 新边集

            def get_nodeinfo_list():
                d = {}
                for 索引, 值 in self.node_dict.items():
                    d[索引] = funcs.GviewOperation.依参数确定视图结点数据类型模板(数据={
                            本.结点.位置:[值.item.scenePos().x(),值.item.scenePos().y()]
                    },编号=索引)
                return d

            return get_nodeinfo_list(), get_edgeinfo_list()

        @dataclass
        class Node:
            """一个node就是一个结点, 他有图形表示的item, 和数据表示的pair"""
            # pair: "LinkDataPair"
            索引: "str"
            due: bool = False
            item: "Optional[VisualBilinker.ItemRect]" = None
            edges: "list[VisualBilinker.Entity.Edge]" = field(default_factory=list)
            desc=""
            def __init__(self, 索引: "str|LinkDataPair", due=False, item=None, edges=None):
                self.索引 = 索引 if type(索引) == str else 索引.card_id
                self.due = due
                self.item = item
                self.edges = [] if edges is None else edges
                self.desc = funcs.CardOperation.desc_extract(self.索引)

            def safe_remove(self,value):
                if value in self.edges:
                    self.edges.remove(value)


        @dataclass
        class Edge:
            item: "VisualBilinker.ItemEdge" = None
            nodes: "list[VisualBilinker.Entity.Node]" = None
            描述: "str" = ""

            def as_card(self) -> 'set':
                return set([int(item.索引) for item in self.nodes])

        @dataclass
        class State:
            mouseIsMoving: bool = False
            mouseIsMovingAndRightClicked: bool = False
            mouseIsMovingAndLeftClicked: bool = False
            mouseRightClicked: bool = False
            mouseLeftClicked: bool = False

    class View(QGraphicsView):
        def __init__(self, parent: "VisualBilinker"):
            super().__init__(parent)
            self.ratio = 1
            self.superior: "VisualBilinker" = parent
            self.setDragMode(DragMode.ScrollHandDrag)
            self.setRenderHints(QPainter.RenderHint.Antialiasing |  # 抗锯齿
                                QPainter.RenderHint.LosslessImageRendering |  # 高精度抗锯齿
                                QPainter.RenderHint.SmoothPixmapTransform)  # 平滑过渡 渲染设定
            self.setViewportUpdateMode(ViewportUpdateMode.FullViewportUpdate)
            self.Auxiliary_line: "Optional[QGraphicsLineItem]" = baseClass.Geometry.ArrowLine()
            self.Auxiliary_line.setZValue(-1)
            self.Auxiliary_line.setPen(VisualBilinker.ItemEdge.normal_pen)
            self.clicked_pos: "Optional[QPointF]" = None
            self.draw_line_start_item: "Optional[VisualBilinker.ItemRect]" = None
            self.draw_line_end_item: "Optional[VisualBilinker.ItemRect]" = None


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
                    self.superior.update_all_edges_posi()
                if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                    choose1 = len(self.superior.scene.selectedItems()) == 1
                    if isinstance(self.draw_line_start_item, VisualBilinker.ItemRect) and choose1:
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
                    if isinstance(self.itemAt(event.pos()), VisualBilinker.ItemRect) and select_1:
                        self.startLine(event.pos())
                        # self.draw_line_start_item: "Grapher.ItemRect" = self.itemAt(event.pos())
                        # startItemCenter = self.draw_line_start_item.mapToScene(self.draw_line_start_item.rect().center())
                        # self.Auxiliary_line.setLine(QLineF(startItemCenter, startItemCenter))
                        # # print(self.Auxiliary_line.line().p1())
                        # self.superior.scene.addItem(self.Auxiliary_line)
            elif event.buttons() == Qt.MouseButton.RightButton:
                self.superior.data.state.mouseLeftClicked = False
                self.superior.data.state.mouseRightClicked = True
                self.setDragMode(DragMode.RubberBandDrag)
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
            self.setDragMode(DragMode.ScrollHandDrag)
            self.superior.update()
            self.superior.data.state.mouseLeftClicked = False
            self.superior.data.state.mouseRightClicked = False
            self.superior.data.state.mouseIsMovingAndLeftClicked = False
            self.superior.data.state.mouseIsMovingAndRightClicked = False

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
            self.draw_line_start_item: "VisualBilinker.ItemRect" = self.itemAt(pos)
            startItemCenter = self.draw_line_start_item.mapToScene(self.draw_line_start_item.rect().center())
            self.Auxiliary_line.setLine(QLineF(startItemCenter, startItemCenter))
            # print(self.Auxiliary_line.line().p1())
            self.Auxiliary_line.show()
            self.superior.scene.addItem(self.Auxiliary_line)
            pass

        def makeLine(self):
            self.superior.scene.removeItem(self.Auxiliary_line)
            end_item, begin_item = self.draw_line_end_item, self.draw_line_start_item
            if isinstance(end_item, VisualBilinker.ItemRect) and begin_item != end_item:
                self.superior.add_edge(begin_item.索引, end_item.索引, add_bilink=True)
            self.superior.data.state.mouseIsMoving = False
            self.Auxiliary_line.hide()

        def make_context_menu(self, event: QtGui.QMouseEvent):
            pairli = funcs.AnkiLinks.get_card_from_clipboard()
            menu = QMenu()
            menu.addAction(译.创建为视图).triggered.connect(lambda: self.superior.create_view())
            if len(pairli) > 0:
                menu.addAction(译.粘贴卡片).triggered.connect(lambda: self.superior.load_node(pairli))
            # if self.superior.data.graph_mode == GraphMode.view_mode:
            #     menu.addAction(Translate.保存当前视图为群组复习条件).triggered.connect(lambda: self.superior.saveAsGroupReviewCondition())
            pos = event.globalPosition() if Anki.isQt6 else event.screenPos()
            menu.exec(pos.toPoint())

        def clearSelection(self):
            if self.superior.data.currentSelectedEdge:
                self.superior.data.currentSelectedEdge[0].unsaveSelect()
            pass

        pass

    class Scene(QGraphicsScene):
        pass

    class ItemEdge(baseClass.Geometry.ArrowLine):
        highlight_pen = QPen(QColor(255, 215, 0), 8.0, PenStyle.DashLine)
        selected_pen = QPen(QColor(102, 255, 230), 8.0, PenStyle.DashLine)
        normal_pen = QPen(QColor(127, 127, 127, 160), 8.0, PenStyle.DashLine)
        pdflink_pen = QPen(QColor(255, 255, 127), 6.0, PenStyle.DashLine)
        intextlink_pen = QPen(QColor(255, 255, 127), 6.0, PenStyle.DashLine)
        normal, pdflink, intextlink = 0, 1, 2

        def __init__(self, superior: "VisualBilinker", itemStart: "VisualBilinker.ItemRect", itemEnd: "VisualBilinker.ItemRect", edge_type=0):
            super().__init__()
            self.edge_type = edge_type
            self.superior = superior
            self.itemStart: "VisualBilinker.ItemRect" = itemStart
            self.itemEnd: "VisualBilinker.ItemRect" = itemEnd
            self.update_line()
            self.setZValue(1)
            self.setPen(self.normal_pen)
            self.setFlag(QGraphicsLineItem.GraphicsItemFlag.ItemIsSelectable, True)

            # * Done:2022年12月27日00:13:23 设计边名的显示

        def update_line(self):
            p1 = self.itemStart.mapToScene(self.itemStart.boundingRect().center())
            p2 = self.itemEnd.mapToScene(self.itemEnd.boundingRect().center())
            # rectA = self.itemStart.mapRectToScene(self.itemStart.rect())
            # rectB = self.itemEnd.mapRectToScene(self.itemEnd.rect())
            # pA = common_tools.funcs.Geometry.IntersectPointByLineAndRect(QLineF(p1, p2), rectA)
            # pB = common_tools.funcs.Geometry.IntersectPointByLineAndRect(QLineF(p1, p2), rectB)

            # if pA is not None: p1=pA
            # if pB is not None: p2=pB
            line = QLineF(p1, p2)
            self.setLine(line)
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
                # remove_globalLink = self.superior.data.graph_mode == GraphMode.normal
                menu.addAction(译.删除边).triggered.connect(lambda: self.superior.remove_edge(self.itemStart.索引, self.itemEnd.索引, remove_globalLink=True))
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
                  widget: Optional[QWidget] = ...) -> None:
            option.state &= ~QStyle_StateFlag.State_Selected
            super().paint(painter, option, widget)

            if self.isSelected():
                self.setPen(self.selected_pen)
                self.setZValue(5)

            elif not self.isSelected() and not self.superior.scene.selectedItems():
                self.setPen(self.normal_pen)
                self.setZValue(1)

            # 文本 = self.获取实体数据().描述 if self.获取实体数据().描述 != "" \
            #     else "debug hello world world hello" \
            #     if self.superior.data.state == GraphMode.debug_mode \
            #     else ""
            #
            # if 文本 != "" and self.pen() == self.selected_pen or self.pen() == self.highlight_pen:
            #     painter.setPen(QColor(50, 205, 50))
            #     painter.setBrush(QBrush(QColor(50, 205, 50)))
            #     painter.drawText(QRectF(center, QSizeF(100.0, 100.0)), Qt.TextFlag.TextWordWrap, 文本)

        def 获取关联的结点(self):
            return self.itemStart.索引, self.itemEnd.索引

        def 获取实体数据(self):
            A, B = self.获取关联的结点()
            return self.superior.data.edge_dict[A][B]

        pass

    class ItemRect(QGraphicsRectItem):
        card_body_style = QColor(197, 224, 235)
        card_title_style = QColor(114, 154, 189)
        view_body_style = QColor(239, 220, 118)
        view_title_style = QColor(95, 142, 172)
        due_dot_style = QColor(255, 0, 0)

        current_title_style = card_title_style
        current_body_style = card_body_style

        class 所属类型:
            卡片 = 0
            视图 = 1

        class MODE:
            all = 0
            pdf = 1
            intext = 2
            outext = 3

        def __init__(self, superior: "VisualBilinker", 索引: "str|LinkDataPair"):
            super().__init__()

            self.superior = superior
            self.索引: "str" = 索引 if type(索引) == str else 索引.card_id
            # if self.结点类型() == 枚举_视图结点类型.视图:
            #     self.current_title_style = self.view_title_style
            #     self.current_body_style = self.view_body_style
            self.setPen(QPen(self.current_body_style))
            self.setBrush(QBrush(self.current_body_style))
            self.setRect(self.superior.data.default_rect)
            self.setFlag(QGraphicsRectItemFlags.ItemIsMovable, True)
            self.setFlag(QGraphicsRectItemFlags.ItemIsSelectable, True)
            self.setFlag(QGraphicsRectItemFlags.ItemSendsGeometryChanges, True)
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

        @property
        def node(self):
            return self.superior.data.node_dict[self.索引]

        def load_linked_card(self, mode=3):
            cardinfo = funcs.GlobalLinkDataOperation.read_from_db(self.索引)
            pair_li = [pair for pair in cardinfo.link_list]
            self.superior.load_node(pair_li, begin_item=self)

        def collide_handle(self, item_li: "list[VisualBilinker.ItemRect]" = None):
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
            return [i for i in self.collidingItems() if isinstance(i, VisualBilinker.ItemRect)]

        def check_collide_rect_position(self, item: "VisualBilinker.ItemRect"):
            target = self.mapFromScene(item.pos())

        def make_context_menu(self):
            menu = QMenu()

            menu.addAction(译.移除).triggered.connect(self.superior.del_selected_node)
            # noinspection PyUnresolvedReferences
            menu.addAction(译.修改描述).triggered.connect(lambda: self.superior.card_edit_desc(self))

            # if self.superior.data.gviewdata.nodes[self.索引][本.结点.数据类型] == baseClass.视图结点类型.卡片:
            #     pair_li: "list[LinkDataPair]" = [LinkDataPair(item.索引, funcs.CardOperation.desc_extract(item.索引)) for item in self.superior.selected_nodes() if funcs.CardOperation.exists(item.索引)]
            #     menu.maker(menu.T.grapher_node_context)(pair_li, menu, self.superior,
            #                                                                       needPrefix=False)

            def menuCloseEvent():
                self.setSelected(True)
                self.setFlag(QGraphicsRectItemFlags.ItemIsMovable, True)
                self.contextMenuOpened = False

            menu.closeEvent = lambda x: menuCloseEvent()

            loadlinkcard = menu.addMenu(译.加载文外链接卡片)
            for name, action in [
                    (译.加载全部文外链接卡片, lambda: self.load_linked_card(mode=self.MODE.outext))
            ]:
                loadlinkcard.addAction(name).triggered.connect(action)
            outtextmenu = loadlinkcard.addMenu(译.选择文外链接卡片加载)
            link_list = funcs.GlobalLinkDataOperation.read_from_db(self.索引).link_list
            shorten = funcs.str_shorten

            for pair in link_list:
                action = lambda pair: lambda: self.superior.load_node([pair], begin_item=self)
                outtextmenu.addAction(
                        f"""card_id={pair.card_id},desc={shorten(pair.desc)}""").triggered.connect(
                        action(pair)
                )
            self.contextMenuOpened = True
            self.setFlag(QGraphicsRectItemFlags.ItemIsMovable, False)
            return menu

        def mouseDoubleClickEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:

            if event.buttons() == Qt.MouseButton.LeftButton:
                funcs.Dialogs.open_custom_cardwindow(self.索引)
                # self.superior.结点访问记录更新(self.索引)

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
            edges = self.superior.data.node_dict[self.索引].edges
            for edge in edges:
                edge.item.update_line()
            # if not self.contextMenuOpened:
            super().mouseMoveEvent(event)

            # print(self.scenePos().__str__())

        def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:

            if not self.contextMenuOpened:
                super().mouseReleaseEvent(event)
                self.setFlag(QGraphicsRectItemFlags.ItemIsMovable, True)

        def 结点描述(self):
            return self.superior.data.node_dict[self.索引].desc

        def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem',
                  widget: typing.Optional[QWidget] = ...) -> None:
            super().paint(painter, option, widget)

            painter.setPen(self.current_title_style)
            painter.setBrush(QBrush(self.current_title_style))
            header_height = 24
            header_rect = QRectF(0, 0, int(self.rect().width()), header_height)
            body_rect = QRectF(0, header_height, int(self.rect().width()), int(self.rect().height()-header_height))
            painter.drawRect(header_rect)

            painter.setPen(QColor(255, 255, 255))
            painter.drawText(header_rect.adjusted(5, 5, -5, -5), Qt.TextFlag.TextWordWrap, str(self.索引))
            painter.drawText(body_rect.adjusted(5, 5, -5, -5), Qt.TextFlag.TextWordWrap, f"""{self.结点描述()}""")

            if self.isSelected():
                path = QPainterPath()
                path.addRect(self.rect())
                painter.strokePath(path, VisualBilinker.ItemEdge.highlight_pen)
                self.setZValue(20)
            else:
                self.setZValue(10)
        pass

    class ToolBar(QToolBar):
        """这是一个工具栏
        """

        class Actions:
            def __init__(self, parent: "VisualBilinker.ToolBar"):
                self.superior = parent
                imgDir = funcs.G.src.ImgDir
                self.save = QAction(QIcon(imgDir.save), "", parent)
                self.dueQueue = QAction(QIcon(imgDir.box2), "", parent)
                self.config = QAction(QIcon(imgDir.config), "", parent)
                self.reConfig_Btn = QAction(QIcon(imgDir.config_reset), "", parent)
                self.help = QAction(QIcon(imgDir.help), "", parent)
                self.itemDel = QAction(QIcon(imgDir.delete), "", parent)
                self.itemRename = QAction(QIcon(imgDir.rename), "", parent)
                self.insert_item = QMenu()
                self.initUI()

            def initUI(self):
                [self.li[i].setToolTip(self.tooltips[i]) for i in range(len(self.li))]

            @property
            def tooltips(self):
                T = language.Translate
                return [
                        T.另存视图,
                        # T.开始漫游复习,
                        # T.打开配置表,
                        # T.重置配置表,
                        "help",
                        T.删除,
                        T.重命名,
                ]

            @property
            def li(self):
                return [
                        self.save,
                        # self.dueQueue,
                        # self.config,
                        # self.reConfig_Btn,
                        self.help,
                        self.itemDel,
                        self.itemRename
                ]

        def __init__(self, parent: "VisualBilinker"):
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
            self.act.itemRename.setDisabled(True)
            pass

        def 生成图元插入菜单(self):
            引入图标 = QPushButton()
            引入图标.setIcon(QIcon(funcs.G.src.ImgDir.item_plus))
            主菜单 = QMenu()
            新建菜单 = 主菜单.addMenu(译.新建)
            新建菜单.addAction(译.卡片).triggered.connect(self.create_card)
            # 新建菜单.addAction(译.视图).triggered.connect(self.create_view)
            # 主菜单.addAction(译.导入).triggered.connect(self.import_item)
            引入图标.setMenu(主菜单)
            self.addWidget(引入图标)
            pass

        def create_card(self):
            """
            调用原生的卡片创建窗口,并在完成后返回卡片id到当前视图id
            """
            funcs.G.常量_当前等待新增卡片的视图索引 = -1
            mw.onAddCard()
            pass

        def create_view(self):
            视图索引 = funcs.GviewOperation.create()
            # self.superior.load_node([视图索引], 参数_视图结点类型=枚举_视图结点类型.视图)
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
                    if len(items) == 1 and (isinstance(items[0], VisualBilinker.ItemRect) or isinstance(items[0], VisualBilinker.ItemEdge)):
                        self.act.itemRename.setDisabled(False)
                    else:
                        self.act.itemRename.setDisabled(True)
                    self.act.itemDel.setDisabled(False)
                else:
                    self.act.itemDel.setDisabled(True)
                    self.act.itemRename.setDisabled(True)
            except:
                return None

        def deleteEdgeItem(self, item: "VisualBilinker.ItemEdge"):
            # cardA = item.itemStart.pair.card_id
            # cardB = item.itemEnd.pair.card_id
            # modifyGlobalLink = self.superior.data.graph_mode == GraphMode.normal
            self.superior.remove_edge(*item.获取关联的结点(), True)
            pass

        def deleteRectItem(self, item: "VisualBilinker.ItemRect"):
            self.superior.remove_node(item)
            pass

        def node_property_editor(self):
            item: "VisualBilinker.ItemRect|VisualBilinker.ItemEdge" = self.superior.scene.selectedItems()[0]
            if isinstance(item, VisualBilinker.ItemRect):
                # self.superior.card_edit_desc(item)
                # self.superior.data.gviewdata.node_helper[item.索引].创建结点UI().exec()
                # common_tools.widgets.ConfigWidget.GviewNodeProperty(self.superior.data.gviewdata,item.索引,self.superior).exec()
                self.superior.card_edit_desc(item)

            pass

        def deleteItem(self):  # 0=rect,1=line
            rectItem: "list[VisualBilinker.ItemRect]" = list(filter(lambda item: isinstance(item, VisualBilinker.ItemRect), self.superior.scene.selectedItems()))
            lineItem: "list[VisualBilinker.ItemEdge]" = list(filter(lambda item: isinstance(item, VisualBilinker.ItemEdge), self.superior.scene.selectedItems()))

            code = QMessageBox.information(self, 译.你将删除这些结点, 译.你将删除这些结点, QMessageBox.Yes | QMessageBox.No)
            if code == QMessageBox.Yes:
                if len(rectItem) > 0:
                    for item in rectItem:
                        self.deleteRectItem(item)
                elif len(lineItem) > 0:
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
            showInfo(zh)
            pass

        @property
        def slots(self):
            return [
                    self.saveAsNewGview,
                    # self.openRoaming,
                    # self.openConfig,
                    # self.resetConfig,
                    self.helpFunction,
                    self.deleteItem,
                    self.node_property_editor,
            ]
    # class Item(QGraphicsItem):
    #     def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem', widget: typing.Optional[QWidget] = ...) -> None:
    #     pass
