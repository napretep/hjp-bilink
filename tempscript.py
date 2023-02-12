# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'tempscript.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2022/8/17 0:57'
本文件用于将 linkinfo.db中的全部对象修改其sync行为
"""
# from lib.common_tools import funcs, G
# from lib.common_tools.compatible_import import *
# from lib.common_tools.objs import LinkDataPair
# from lib.common_tools import G, baseClass,funcs
# from lib.common_tools.widgets import ConfigWidget
# from lib.bilink.dialogs.linkdata_grapher import GViewAdmin, Grapher, GViewData
# from PyQt5.QtCore import
import sys
import faulthandler
import sqlite3
import abc
# from lib.clipper3.httpserver import Resquest,HTTPServer
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QPushButton, QVBoxLayout, QTextEdit

if __name__ == "__main__":
    faulthandler.enable()
    app = QApplication(sys.argv)
    # 关键词 = "1"
    # G.DB.go(G.DB.table_GviewConfig).excute_queue.append(f"""
    #         select "视图",name,uuid from GRAPH_VIEW_TABLE  where name like "%{关键词}%"
    #         union
    #         select "配置",name,uuid from GRAPH_VIEW_CONFIG where name like "%{关键词}%"
    #         order by name
    #         """)
    # result = G.DB.commit()
    # print(list(result))
    # p=GViewAdmin()
    # p.show()
    # a = Grapher(gviewdata=GViewData(uuid="aaa", name="123",
    #                                 nodes={"absdsdjf": funcs.GviewOperation.默认视图结点数据类型模板(),
    #                                         "1234678": funcs.GviewOperation.默认卡片结点数据类型模板()
    #                                 },
    #                                 edges={}
    #                                 )
    #
    #             , mode=2)
    # a.show()
    # a=[GViewData(uuid="1234",name="basdbasd",nodes={},edges={}),GViewData(uuid="555",name="xxxx",nodes={},edges={})]
    # print("1234" in a)
    class A(QDialog):
        def __init__(self):
            super().__init__()
            self.help_text="""
The list of strings you enter into Python syntax in the text box will be converted into a list of tags to be selected in the node_tag property of the view node
Example: 
After you enter ["apple", "banana", "orange"] in the text box, then the node_tag of other nodes will be in the Selected tab
apple banana orange 
Note:
1. The Python string list type format must be strictly observed, otherwise an error will be reported, which will be forcibly overwritten by an empty list, and the empty list means no optional tags.
2. The order of the elements is meaningful, with greater weight in front of the ranking, used for weighting calculations.
            """
            self.text_input = QTextEdit()
            self.help_label=QLabel()
            self.help_label.setWordWrap(True)
            self.help_btn = QPushButton("help")
            self.cust_layout = QVBoxLayout()
            self.cust_layout.addWidget(self.text_input)
            self.cust_layout.addWidget(self.help_btn)
            self.cust_layout.addWidget(self.help_label)
            self.help_btn.clicked.connect(self.help_switch)
            self.setLayout(self.cust_layout)
        def help_switch(self):
            if self.help_label.text()!=self.help_text:
                self.help_label.setText(self.help_text)
            else:
                self.help_label.setText("")


    # funcs.Dialogs.open_configuration()
    test = A()
    test.exec()
    app.exec()
    sys.exit()
