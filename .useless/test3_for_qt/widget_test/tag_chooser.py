# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'tag_chooser.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2021/8/7 10:12'
"""

import sys
from dataclasses import dataclass
from typing import Optional
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QIcon, QStandardItem
from PyQt5.QtWidgets import QDialog, QTreeView, QVBoxLayout, QWidget, QLabel, QToolButton, QHBoxLayout, QApplication, \
    QHeaderView
from aqt import mw


class CascadeStr:
    @dataclass
    class Node:
        item: "QStandardItem"
        children: "dict[str,CascadeStr.Node]"


class tag_chooser(QDialog):

    def __init__(self, pair_li: "Optional[list[G.objs.LinkDataPair]]" = None):
        super().__init__()
        self.pair_li = pair_li
        self.view_left = QTreeView(self)
        self.view_right = QTreeView(self)
        self.model_left = QStandardItemModel(self)
        self.model_right = QStandardItemModel(self)
        self.model_right_rootNode: "Optional[QStandardItemModel.invisibleRootItem]" = None
        self.model_left_rootNode: "Optional[QStandardItemModel.invisibleRootItem]" = None
        self.header_left = self.Header(self, tag_name="tag from selected")
        self.header_right = self.Header(self, tag_name="tag from all")
        # self.header_left.button.clicked.connect(self.on_header_left_button_clicked_handle)
        # self.header_right.button.clicked.connect(self.on_header_right_button_clicked_handle)
        # self.view_left.clicked.connect(self.on_view_clicked_handle)
        # self.model.dataChanged.connect(self.on_model_data_changed_handle)
        self.init_UI()
        self.init_model()

    def init_UI(self):
        self.setWindowTitle("tag chooser")
        # self.setWindowIcon(QIcon(G.src.ImgDir.tag))
        v_box_left = QVBoxLayout()
        v_box_right = QVBoxLayout()
        h_box = QHBoxLayout(self)
        v_box_right.addWidget(self.header_right)
        v_box_right.addWidget(self.view_right)
        v_box_left.addWidget(self.header_left)
        v_box_left.addWidget(self.view_left)
        h_box.addLayout(v_box_left)
        h_box.addLayout(v_box_right)
        self.setLayout(h_box)

        pass

    def init_model(self):
        self.view_left.setModel(self.model_left)
        self.view_right.setModel(self.model_right)
        self.model_left.setHorizontalHeaderLabels(["tag_name", ""])
        self.model_right.setHorizontalHeaderLabels(["tag_name", ""])
        self.view_left.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.view_left.setColumnWidth(1, 30)
        self.view_right.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.view_right.setColumnWidth(1, 30)
        self.init_data_left()
        self.init_data_right()

        pass

    def get_all_tags_from_collection(self) -> 'list[str]':
        if __name__ == "__main__":
            return ['0dailynotes',
                    '0dailynotes::1随记',
                    '0dailynotes::2项目',
                    '0dailynotes::2项目::0文章',
                    '0dailynotes::2项目::hjp-bilink',
                    '0dailynotes::2项目::hjp-bilink::开发目标',
                    '0dailynotes::3笔记',
                    '0dailynotes::time::2020::12::13',
                    '0dailynotes::time::2020::12::14',
                    '总结::笔记',
                    '总结::证明方法',
                    '总结::证明方法::反证法',
                    '总结::证明方法::多项式与解空间',
                    '总结::证明方法::扩基',
                    '总结::证明方法::找同构映射的方法',
                    '总结::证明方法::数学归纳法',
                    '总结::证明方法::矩阵分解',
                    '总结::证明方法::逆射证明',
                    '总结::重要结论',
                    '总结::难点必背',
                    '总结::难点必背::不等式',
                    '总结::难点必背::中值定理',
                    '总结::难点必背::可积性定理',
                    '总结::难点必背::实数理论',
                    '总结::难点必背::等式',
                    '总结::难点必背::高代::AB可交换',
                    '总结::难点必背::高代::上下三角矩阵',
                    '总结::难点必背::高代::互素因子与直和',
                    '总结::难点必背::高代::同构（可逆）',
                    '总结::难点必背::高代::名词',
                    '总结::难点必背::高代::域扩张',
                    '总结::难点必背::高代::矩阵乘法',
                    '总结::难点必背::高代::线性空间',
                    '数学::习题',
                    '数学::习题::数学分析::华师初试题::2005',
                    '数学::习题::数学分析::华师初试题::2006',
                    '数学::习题::数学分析::华师初试题::2007',
                    '数学::习题::数学分析::华师初试题::2008',
                    '数学::习题::数学分析::华师初试题::2009',
                    '数学::习题::数学分析::华师初试题::2010',
                    '数学::习题::数学分析::华师初试题::2011',
                    '数学::习题::数学分析::华师初试题::2012',
                    '数学::习题::数学分析::华师初试题::2013',
                    '数学::习题::数学分析::华师初试题::2014',
                    '数学::习题::数学分析::华师初试题::2015',
                    '数学::习题::数学分析::华师初试题::2016',
                    '数学::习题::数学分析::华师初试题::2017',
                    '数学::习题::数学分析::华师初试题::2018',
                    '数学::习题::数学分析::华师初试题::2019',
                    '数学::习题::数学分析::华科初试题::2020',
                    '数学::习题::数学分析::湘潭大学初试题::1997',
                    '数学::习题::数学分析::湘潭大学初试题::1998',
                    '数学::习题::数学分析::湘潭大学初试题::1999',
                    '数学::习题::数学分析::湘潭大学初试题::2000',
                    '数学::习题::数学分析::湘潭大学初试题::2001',
                    '数学::习题::数学分析::湘潭大学初试题::2002',
                    '数学::习题::数学分析::湘潭大学初试题::2003',
                    '数学::习题::数学分析::湘潭大学初试题::2004',
                    '数学::习题::数学分析::湘潭大学初试题::2005',
                    '数学::习题::数学分析::湘潭大学初试题::2006',
                    '数学::习题::数学分析::湘潭大学初试题::2007',
                    '数学::习题::数学分析::湘潭大学初试题::2008',
                    '数学::习题::数学分析::湘潭大学初试题::2009',
                    '数学::习题::数学分析::湘潭大学初试题::2010',
                    '数学::习题::数学分析::湘潭大学初试题::2011',
                    '数学::习题::数学分析::湘潭大学初试题::2012',
                    '数学::习题::数学分析::湘潭大学初试题::2013',
                    '数学::习题::数学分析::湘潭大学初试题::2014',
                    '数学::习题::数学分析::湘潭大学初试题::2015',
                    '数学::习题::数学分析::湘潭大学初试题::2016',
                    '数学::习题::数学分析::湘潭大学初试题::2017',
                    '数学::习题::数学分析::湘潭大学初试题::2018',
                    '数学::习题::数学分析::湘潭大学初试题::2020',
                    '数学::习题::无答案',
                    '数学::习题::疑问',
                    '数学::习题::面试题',
                    '数学::习题::高等代数::华师初试题::2004',
                    '数学::习题::高等代数::华师初试题::2005',
                    '数学::习题::高等代数::华师初试题::2006',
                    '数学::习题::高等代数::华师初试题::2007',
                    '数学::习题::高等代数::华师初试题::2008',
                    '数学::习题::高等代数::华师初试题::2009',
                    '数学::习题::高等代数::华师初试题::2010',
                    '数学::习题::高等代数::华师初试题::2011',
                    '数学::习题::高等代数::华师初试题::2012',
                    '数学::习题::高等代数::华师初试题::2013',
                    '数学::习题::高等代数::华师初试题::2014',
                    '数学::习题::高等代数::华师初试题::2015',
                    '数学::习题::高等代数::华师初试题::2016',
                    '数学::习题::高等代数::华师初试题::2017',
                    '数学::习题::高等代数::华师初试题::2018',
                    '数学::习题::高等代数::华师初试题::2019',
                    '数学::习题::高等代数::湘潭大学初试题::1997',
                    '数学::习题::高等代数::湘潭大学初试题::1998',
                    '数学::习题::高等代数::湘潭大学初试题::1999',
                    '数学::习题::高等代数::湘潭大学初试题::2001',
                    '数学::习题::高等代数::湘潭大学初试题::2002',
                    '数学::习题::高等代数::湘潭大学初试题::2003',
                    '数学::习题::高等代数::湘潭大学初试题::2004',
                    '数学::习题::高等代数::湘潭大学初试题::2005',
                    '数学::习题::高等代数::湘潭大学初试题::2006',
                    '数学::习题::高等代数::湘潭大学初试题::2007',
                    '数学::习题::高等代数::湘潭大学初试题::2008',
                    '数学::习题::高等代数::湘潭大学初试题::2009',
                    '数学::习题::高等代数::湘潭大学初试题::2010',
                    '数学::习题::高等代数::湘潭大学初试题::2011',
                    '数学::习题::高等代数::湘潭大学初试题::2012',
                    '数学::习题::高等代数::湘潭大学初试题::2013',
                    '数学::习题::高等代数::湘潭大学初试题::2014',
                    '数学::习题::高等代数::湘潭大学初试题::2015',
                    '数学::习题::高等代数::湘潭大学初试题::2016',
                    '数学::习题::高等代数::湘潭大学初试题::2017',
                    '数学::习题::高等代数::湘潭大学初试题::2018',
                    '数学::习题::高等代数::湘潭大学初试题::2020',
                    '数学::课本::复变',
                    '数学::课本::复变::华科应用复分析',
                    '数学::课本::复变::复变函数@钟玉泉',
                    '数学::课本::复变::复变函数与积分变换_华科李红',
                    '数学::课本::复变::复变函数与积分变换_焦红伟PDF',
                    '数学::课本::复变::慕课国防科大',
                    '数学::课本::拓扑::点集拓扑讲义@熊金城::01朴素集合论',
                    '数学::课本::拓扑::点集拓扑讲义@熊金城::02拓扑空间与连续映射',
                    '数学::课本::拓扑::点集拓扑讲义@熊金城::04连通性',
                    '数学::课本::拓扑::点集拓扑讲义@熊金城::05可数性公理',
                    '数学::课本::拓扑::点集拓扑讲义@熊金城::07紧致性',
                    ]

    def get_all_tags_from_pairli(self) -> 'list[str]':
        """多张卡片要取公共的"""
        if __name__ == "__main__":
            return [
                '0dailynotes',
                '0dailynotes::1随记',
                '0dailynotes::2项目',
                '0dailynotes::2项目::0文章',
                '0dailynotes::2项目::hjp-bilink',
                '0dailynotes::2项目::hjp-bilink::开发目标',
                '0dailynotes::3笔记',
                '0dailynotes::time::2020::12::13',
                '0dailynotes::time::2020::12::14',
            ]
        pass

    def build_tag_tree(self, tag_list: "list[str]", model: "QStandardItemModel", view: "QTreeView"):
        tag_dict = CascadeStr.Node(model.invisibleRootItem(), {})
        for i in tag_list:
            tagname_li = i.split("::")
            parent = tag_dict
            while tagname_li:
                tagname = tagname_li.pop(0)
                if tagname not in parent.children:
                    item = self.Item(tagname)
                    widget = self.Item("")
                    parent.item.appendRow([item, widget])
                    button = self.build_tag_make_button(item)
                    view.setIndexWidget(widget.index(), button)
                    parent.children[tagname] = CascadeStr.Node(item, {})
                parent = parent.children[tagname]

        pass

    def build_tag_make_button(self, item):
        """为model的构建提供一个快捷操作"""
        button = QToolButton(self)
        # button.setIcon(QIcon(G.src.ImgDir.correct))
        button.setFixedWidth(25)
        button.clicked.connect(lambda: self.on_item_button_clicked_handle(item))
        return button

    def build_tag_list(self, tag_list: "list[str]", model: "QStandardItemModel", view: "QTreeView"):
        pass

    def init_data_left(self):
        model, header, view = self.model_left, self.header_left, self.view_left
        self.model_left_rootNode = model.invisibleRootItem()
        model.setHorizontalHeaderLabels(["tag_name", ""])
        tag_list = self.get_all_tags_from_pairli()
        if header.button.text() == header.tag_tree:
            self.build_tag_tree(tag_list, model, view)
        else:
            self.build_tag_list(tag_list, model, view)
        pass

    def init_data_right(self):
        model, header, view = self.model_right, self.header_right, self.view_right
        self.model_left_rootNode = model.invisibleRootItem()
        model.setHorizontalHeaderLabels(["tag_name", ""])
        tag_list = self.get_all_tags_from_collection()
        if header.button.text() == header.tag_tree:
            self.build_tag_tree(tag_list, model, view)
        else:
            self.build_tag_list(tag_list, model, view)
        pass

    @property
    def curr_tag_name(self):
        return "tag_name"

    class Attr:
        pass

    class Header(QWidget):
        tag_tree, tag_list = "tag_tree", "tag_tree"

        def __init__(self, parent, tag_name="test::test"):
            super().__init__(parent)
            self.desc = QLabel(tag_name, self)
            self.desc.setWordWrap(True)
            self.button = QToolButton(self)
            self.button.setText(self.tag_tree)
            H_layout = QHBoxLayout(self)
            H_layout.addWidget(self.desc)
            H_layout.addWidget(self.button)
            H_layout.setStretch(0, 1)
            H_layout.setStretch(1, 0)
            self.setLayout(H_layout)

    class Item(QStandardItem):
        def __init__(self, tag_name):
            super().__init__(tag_name)
            self.tag_id: "Optional[int]" = None
            self.level: "Optional[int]" = None
            self.setFlags(self.flags() & ~Qt.ItemIsDragEnabled & ~Qt.ItemIsDropEnabled)

        @property
        def tag_name(self):
            return self.text()

    @dataclass
    class Id_tag:
        tag: "str"
        ID: "int"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    f = tag_chooser()
    f.show()
    sys.exit(app.exec_())
