# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'tempscript.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2022/8/17 0:57'
本文件用于将 linkinfo.db中的全部对象修改其sync行为
"""
from lib.common_tools import funcs, G
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
    # app = QApplication(sys.argv)
    # print(funcs.组件定制.长文本获取())
    #
    # sys.exit(app.exec_())

    # class A:
    #     def __add__(self, other):
    #
    import sys
    from functools import cmp_to_key


    # def 漫游路径生成之深度优先遍历():
    栈 = ["1"]
    结点集 = set(["1","2","3","4","5","6"])
    已访问 = []
    边集 = ["1,2","2,3","2,4","4,5","5,6","6,2"]
    while 结点集:
        if not 栈:
            栈.append(结点集.pop())
        while 栈:
            结点 = 栈.pop()
            已访问.append(结点)
            结点为起点的边集 = [边 for 边 in 边集 if 边.startswith(结点)]
            for 边 in 结点为起点的边集:
                终点 = 边.split(",")[1]
                if 终点 not in 已访问:
                    栈.append(终点)
        结点集 -= set(已访问)
    print(已访问)

    # class 值类型:
    #     数值="number"
    #     时间戳="timestamp"
    #     布尔 = "bool"
    #     枚举 = lambda 枚举表:"enum:"+枚举表.__str__()
    #
    # print(值类型.枚举(["1","2","3"]))


    pass
    # def 播报(内容):
    #     return lambda :print(内容)
    # 播报 = lambda 内容:lambda:print(内容)
    #     # def 内置():
    #     #     print(内容)
    #     #
    #     # return 内置
    # c =  ["1","2","3"]
    # e=[]
    # [e.append((lambda :lambda:print(i))()) for i in c]
    # # [lambda :e.append(lambda k=i:print(i)) for s in ["1","2","3"]]
    # # list(map( lambda i: e.append(lambda:print(i)) , ["1","2","3"]))
    # [e[i]() for i in range(3)]

    # sys.exit()

    # class A:
    #     def B(self):
    #         print("I'm A")

    # C = A()
    # print()
