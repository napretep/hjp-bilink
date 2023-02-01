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
from lib.common_tools.compatible_import import *
from lib.common_tools.objs import LinkDataPair
from lib.common_tools import G, baseClass,funcs
from lib.common_tools.widgets import ConfigWidget
from lib.bilink.dialogs.linkdata_grapher import GViewAdmin, Grapher, GViewData
import sys
import faulthandler
import sqlite3

# from lib.clipper3.httpserver import Resquest,HTTPServer
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
    p=GViewAdmin()
    p.show()
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


    app.exec()
    # class A:
    #     colnames = ["name"]
    # w = ConfigWidget.GviewConfigApplyTable.NewRowFormWidget(A())
    # w.widget.exec() \
    # server = HTTPServer(host, Resquest)
    # print("Starting server, listen at: %s:%s" % host)
    # print(G.src.path.user)
    # server.serve_forever()
    sys.exit()
