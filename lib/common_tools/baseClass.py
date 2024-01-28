# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'ABC.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2022/7/15 23:09'

这个文件用于提供基类,
"""
import typing, re, dataclasses

from .compatible_import import *
import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .configsModel import *

布局, 组件, 子代 = 0, 1, 2


@dataclass
class IdName:
    name: "str" = ""
    ID: "int|str|None" = None


class 视图结点类型:
    卡片 = "card"
    视图 = "view"




class 枚举命名:
    class 结点:
        # 结点推算所得信息
        出度 = "node_out_degree"
        入度 = "node_in_degree"
        数据源 = "node_role_list"  # 角色数据源用于提供角色的选择范围
        全局上次复习 = "global_last_review"
        上次复习 = "node_last_review"
        名称 = "node_name"
        描述 = "node_desc"
        边名 = "edge_name"
        角色名 = "node_role_name"
        已到期 = "is_due"  # 视图结点总是到期
        # 结点自身保存信息
        角色 = "node_role"
        上次编辑 = "node_last_edit"
        上次访问 = "node_last_visit"
        访问次数 = "node_visit_count"
        数据类型 = "node_data_type"
        主要结点 = "node_major_node"
        创建时间 = "node_created_time"
        位置 = "node_position"
        优先级 = "node_priority"
        需要复习 = "node_need_review"
        必须复习 = "node_must_review"
        漫游起点 = "node_roaming_start"
        结构结点= "node_structural_node"
        预览可见 = "node_visible_in_previewer"

        pass

    class 视图:
        # 保存得
        编号 = "view_id"
        名称 = "view_name"
        配置 = "view_config"
        创建时间 = "view_created_time"
        上次访问 = "view_last_visit"
        上次编辑 = "view_last_edit"
        上次复习 = "view_last_review"
        访问次数 = "view_visit_count"
        # 推算得
        到期结点数 = "view_due_node_count"
        主要结点 = "view_major_nodes"
        视图卡片内容缓存 = "card_content_cache"

    class 视图配置:
        结点角色表 = "node_role_list"
        ascending = "ascending"
        descending = "descending"

        class 图排序模式:
            深度优先遍历 = 0
            广度优先遍历 = 1

        class roamingStart:
            随机选择卡片开始 = 0
            手动选择卡片开始 = 1



    class 时间:
        转时间戳 = "to_timestamp"
        今日 = "time_today"
        昨日 = "time_yesterday"
        上周 = "time_last_week"
        本周 = "time_this_week"
        一个月前 = "time_last_month"
        本月 = "time_this_mohth"
        三天前 = "time_three_day_ago"
        三个月前 = "time_three_month_ago"
        六个月前 = "time_six_month_ago"

    class 边:
        名称 = "edge_name"
        pass

    class 组件类型:
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
        slider = 11
        checkbox = 12
        time = 13
        editable_label = 14

    class 值类型:
        整数 = "int"
        数值 = "number"
        时间戳 = "timestamp"
        布尔 = "bool"
        枚举 = "enum:"
        文本 = "text"
        列表 = "list"
        表格 = "table" # 当你的数据结构是表格时, 必须遵循如下的结构: list[dict[列名,值]]
        枚举_结点类型 = "enum_node_type",
        ID_name = "ID_name"
        路径 = "directory"
        文件 = "filepath"
        未知 = "unknown"
        字典 = {
                整数:     [int],
                数值     : [int, float],
                时间戳    : [int, float],
                布尔     : [bool],
                文本     : [str],
                列表     : [list],
                枚举_结点类型: ["card", "view"],
                表格: [dict,list],
                ID_name:[IdName],
                路径 :[str],
                文件:[str],
                未知:[],

        }
        具备默认校验函数的类型=[整数,数值,时间戳,布尔,路径,文件,]

    class 砖:
        布局, 组件, 子代 = 0, 1, 2
        框, 件, 子 = 0, 1, 2

    class 路径生成模式:
        随机排序 = 0
        多级排序 = 1
        加权排序 = 2
        图排序 = 3

    class 全局配置:
        class 描述提取规则:
            牌组= "deck_id"
            模板= "model_id"
            字段= "field_id"
            标签= "tag_list"
            正则= "regexp"
            同步 = "sync"
            长度 = "length"

            @staticmethod
            def 默认规则():
                return {
                        枚举命名.全局配置.描述提取规则.牌组: -1,
                        枚举命名.全局配置.描述提取规则.模板: -1,
                        枚举命名.全局配置.描述提取规则.字段: -1,
                        枚举命名.全局配置.描述提取规则.标签: [],
                        枚举命名.全局配置.描述提取规则.正则: "",
                        枚举命名.全局配置.描述提取规则.长度: 0,
                        枚举命名.全局配置.描述提取规则.同步: True,
                }

            @staticmethod
            def 规则校验(待校验规则):
                if type(待校验规则)!=dict:
                    return False
                默认规则 = 枚举命名.全局配置.描述提取规则.默认规则()
                for 键,值 in 默认规则.items():
                    if 键 not in 待校验规则:
                        return False
                    if type(待校验规则[键]) != type(默认规则[键]):
                        return False
                return True



        class 视图管理器与视图:
            默认的排版方式="gview_admin_default_display"
            默认视图 =  "set_default_view"

            @dataclass
            class 排版方式:
                树形:IdName = field(default_factory=lambda: IdName(ID=0,name=译.树形))
                列表形:IdName = field(default_factory=lambda: IdName(ID=1, name=译.列表形))

        class 描述提取:
            长度限制="length_of_desc"
            同步描述="desc_sync"
            规则表 = "descExtractTable"
            移除文内链接 = "delete_intext_link_when_extract_desc"
            新卡片默认同步描述 = "new_card_default_desc_sync"

        class 全局双链:
            加标签 = "add_link_tag"
            链接后打开浏览器 = "open_browser_after_link"
            默认双链模式 = "default_link_mode"
            默认解绑模式 = "default_unlink_mode"
            默认插入模式 = "default_insert_mode"
            默认复制模式 = "default_copylink_mode"
            链接快捷键 = "shortcut_for_link"
            解绑快捷键 = "shortcut_for_unlink"
            收集快捷键 = "shortcut_for_insert"
            复制链接快捷键 = "shortcut_for_copylink"
            收集器快捷键 = "shortcut_for_openlinkpool"

            @dataclass
            class 双链模式:
                完全图:IdName = field(default_factory=lambda: IdName(ID=0,name=译.完全图绑定))
                组到组:IdName = field(default_factory=lambda:IdName(ID=1,name=译.组到组绑定))

            @dataclass
            class 解绑模式:
                按结点:IdName = field(default_factory=lambda: IdName(ID=0, name=译.按结点解绑))
                按路径:IdName = field(default_factory=lambda: IdName(ID=1, name=译.按路径解绑))

            @dataclass
            class 插入模式:
                清空后插入:IdName = field(default_factory=lambda: IdName(ID=0, name=译.清空后插入))
                直接插入:IdName = field(default_factory=lambda:IdName(ID=1,name=译.直接插入))
                编组插入:IdName = field(default_factory=lambda:IdName(ID=2,name=译.编组插入))

            @dataclass
            class 复制模式:
                文内链接:IdName = field(default_factory=lambda:IdName(ID=0,name=译.文内链接))
                文内链接_html:IdName = field(default_factory=lambda:IdName(ID=1, name=译.文内链接+"(html)"))
                html链接:IdName = field(default_factory=lambda:IdName(ID=2, name=译.html链接))
                orgmode链接:IdName = field(default_factory=lambda:IdName(ID=3, name=译.orgmode链接))
                markdown链接:IdName = field(default_factory=lambda:IdName(ID=4, name=译.markdown链接))




        class 卡片元信息:
            链接菜单样式文本 = "LinkMenu_style_text"
            链接菜单样式文件 = "LinkMenu_style_file"
            链接菜单样式预设 = "LinkMenu_style_preset"
            @dataclass
            class 链接菜单样式预设模式:
                手风琴式:IdName=field(default_factory=lambda :IdName(ID=0,name=译.手风琴式))
                直铺式:IdName=field(default_factory=lambda :IdName(ID=1,name=译.直铺式))


        class 备份:
            开启自动备份 = "auto_backup"
            自动备份间隔 = "auto_backup_interval"
            自动备份路径 = "auto_backup_path"
            上次备份时间 = "last_backup_time"
        class PDF链接:
            样式 = "PDFLink_style"
            命令 = "PDFLink_cmd"
            页码显示开启 = "PDFLink_show_pagenum"
            页码显示样式 = "PDFLink_pagenum_str"
            预设pdf  = "PDFLink_presets"

            @dataclass
            class PDFLink:
                url: "str" = "pdfurl"
                path: "str" = "pdfpath"
                page: "str" = "pagenum"


            class 预设pdf表_单行信息:
                # [["PDFpath", "name", "style", "showPage"]...]
                路径="path"
                显示名 = "name"
                样式 = "style"
                是否显示页码="showPage"
                @staticmethod
                def 默认数据():
                    return {
                            枚举命名.全局配置.PDF链接.预设pdf表_单行信息.路径:"",
                            枚举命名.全局配置.PDF链接.预设pdf表_单行信息.显示名:"",
                            枚举命名.全局配置.PDF链接.预设pdf表_单行信息.样式:"",
                            枚举命名.全局配置.PDF链接.预设pdf表_单行信息.是否显示页码:True
                    }

    范围 = "range"
    组件 = "widget"
    值 = "value"
    # 数据源 = "data_source"
    # 位置 = "position"  # 用于gviewdata中结点的位置
    # 边名 = "edge_name"  # 用于gviewdata中边名的描述
    独立卡片预览器 = "independent previewer"
    # 数据类型 = "node_data_type"
    # 主要结点 = "major_node"
    # 创建时间 = "created_time"
    # 上次访问 = "last_visit"
    # 上次编辑 = "last_edit"
    # 访问次数 = "visit_count"
    视图卡片内容缓存 = "card_content_cache"
    # 结点访问次数 = "node_vist_count"
    # 结点上次访问 = "node_last_vist"
    # 结点上次编辑 = "node_last_edit"
    # 优先级 = "node_priority"
    # 需要复习 = "need_review"
    # 必须复习 = "must_review"
    # 上次复习 = "last_review"
    # 漫游起点 = "roaming_start"
    # 结点描述 = "node_desc"
    上升 = "ascending"
    下降 = "descending"

class 漫游预设:
    默认过滤规则 = f"max({枚举命名.结点.上次复习},{枚举命名.结点.全局上次复习})<{枚举命名.时间.今日}+86400 or {枚举命名.结点.已到期}"
    默认多级排序规则 = f"[[{枚举命名.结点.优先级}, {枚举命名.下降}]]"
    默认加权排序规则 = f"{枚举命名.结点.优先级}"




# class ConfigTableNewRowFormView:
#     """
#     一个表格, 新增一行的时候, 调用这个组件会出来一个用户填写的表单, 填完点确定, 就会插入新的一行
#     第一个参数superior是自己的调用方,
#     第二个参数colItems当不为空,则代表修改一行, 将该行数据获取填入, 为空则代表新建一行, 使用默认数据填入,
#     第三个参数colWidgets表示每个列所对应的组件, 如果没有提供, 则需要自己继承后__init__新建的时候创建
#     """
#     def __init__(self, superior:"ConfigTableView", colItems: "list[ConfigTableView.TableItem]" = None, colWidgets: "list[QWidget]" = None):
#         self.superior: "ConfigTableView" = superior
#         from . import funcs
#         self.layout = QFormLayout()
#         # self.mainLayout = QVBoxLayout()
#         self.ok = False
#         self.isNew = False
#         self.okbtn = funcs.组件定制.按钮_确认()
#         self.widget = QDialog()
#         self.widget.setWindowTitle("new")
#         # self.widget.resize(500, 300)
#         if not colItems:
#             from . import funcs
#             colItems = funcs.Map.do(superior.defaultRowData, lambda data: superior.TableItem(superior, *data))
#             self.isNew = True
#         # colItems 是 配置项对应的table的Item, 在查看行组件中, 当完成操作点击确定, 会把 colItem对应的项加入到配置项对应的table中
#         self.colItems: "list[ConfigTableView.TableItem]" = colItems
#         self.colWidgets: "list[QWidget]"=colWidgets
#
#         self.SetupUI()
#         self.SetupWidget()
#         self.SetupEvent()
#
#     def SetupUI(self):
#         """在这里,每一列按照QFormLayout以名字-组件的方式添加,最后加上ok按钮"""
#         from . import G
#         # hlayout = QHBoxLayout()
#
#         # self.mainLayout.addLayout(self.layout)
#         # hlayout.addWidget(self.okbtn)
#         # self.mainLayout.addLayout(hlayout)
#         # self.mainLayout.setAlignment(Qt.AlignRight)
#         self.okbtn.clicked.connect(self.OnOkClicked)
#         if self.colWidgets:
#             self.setUpColWidgets()
#         self.layout.addRow("",self.okbtn)
#         self.widget.setLayout(self.layout)
#
#     def setUpColWidgets(self):
#         [self.layout.addRow(self.superior.colnames[i], self.colWidgets[i]) for i in range(len(self.superior.colnames))]
#
#     def OnOkClicked(self):
#         from . import funcs
#         self.ok = True
#         self.setValueToTableRowFromForm()
#         # funcs.Utils.print("OnOkClicked",need_logFile=True)
#         self.widget.close()
#
#     @abc.abstractmethod
#     def SetupEvent(self):
#         """建立链接"""
#         raise NotImplementedError()
#
#     @abc.abstractmethod
#     def SetupWidget(self):
#         """布置新行的widget,把item的值转换成可在组件中展示的值."""
#         pass
#
#     @abc.abstractmethod
#     def setValueToTableRowFromForm(self):
#         """将值保存到行(self.colItems)中,他需要重载的原因是不同的表提取保存的数据类型形式各有不同"""
#         pass
#
#     def InitLayout(self, d: "dict"):
#         """
#
#         """
#         from . import G
#         B = G.objs.Bricks
#         layout, widget, kids = B.triple
#         if layout in d:
#             the_layout: "QHBoxLayout|QVBoxLayout|QGridLayout" = d[layout]
#             for kid in d[kids]:
#                 d1 = self.InitLayout(kid)
#                 if layout in d1:
#                     the_layout.addLayout(d1[layout])
#                 else:
#                     the_layout.addWidget(d1[widget])
#         return d


# class CustomConfigItemView(metaclass=abc.ABCMeta):
#     """提供了最基础的功能, 即访问父类,访问对应的配置项,以及访问UI组件"""
#
#     @abc.abstractmethod
#     def SetupView(self):
#         """这个用来规定View如何被组合"""
#         raise NotImplementedError()
#         pass
#
#     @abc.abstractmethod
#     def SetupData(self, raw_data):
#         """raw_data是指保存下来的配置表项的值
#         setupData的目标是将raw_data存储为ViewUI可以接受的值.
#
#         """
#         raise NotImplementedError()
#         pass
#
#     @property
#     def View(self) -> "QWidget":
#         """view 是 model item 对应的展示UI"""
#         return self._view
#
#     @View.setter
#     def View(self, value: "QWidget"):
#         self._view = value
#
#     def __init__(self, configItem: "ConfigModelItem" = None, 上级: "Standard.配置表容器" = None, *args, **kwargs):
#         self.ConfigModelItem: "ConfigModelItem" = configItem
#         self.上级: "Standard.配置表容器" = 上级
#         self.View: "QWidget" = QWidget(上级)


# class 基类_配置项_表格型(CustomConfigItemView):
#
#
#     pass

# class ConfigTableView(CustomConfigItemView, metaclass=abc.ABCMeta):
#     """只提供基础的表格功能, 双击修改行, 点加号增加空记录, 点减号减去对应行
#     这个类自定义了配置表的基本功能, 把很多设置提前设置好减少代码量
#     2023年2月6日18:31:46 这个东西非常复杂, 我后面需要写一个调用的结构图
#     这个东西是表格型配置项的UI,
#     需要考虑的东西:
#     1 设计列名, 缺省行数据
#     2 判断表格形式, 单列表,/单选表
#     数据加载:
#     3 数据从 配置项上保存的raw_data 转换成 表格展示的值 需要通过setupData实现
#         3.1 setupdata 中 需要用到 GetRowFromData 来具体地转换数据源为一行数据的形式,
#         3.2 GetRowFromData 中 需要指定 表格的项(TableItem) 如果有特殊需要, 需要指定, 没有特殊需要, 可以用预置的
#     新建/修改数据:
#     4 点击加号新建数据, 会调用 NewRow->NewRowFormWidget(superior, colitems, colWidgets)->setValueToTableRowFromForm->SaveDataToConfigModel
#         4.1 NewRowFormWidget 通常继承自 ConfigTableNewRowFormView
#         4.2 NewRowFormWidget 通常需要三个参数, 1 调用者, 2 colitems 行数据, 3 colWidgets 行数据对应的组件, 你需要把这三个都传入
#         4.3 新建时, colitems 为None, 函数会调用默认的行来创建, 修改时, 直接把行对应的组件保存到 colitems中即可.
#         4.4 保存时, 点击ok按钮会发生,
#         4.4.1 先调用 setValueToTableRowFromForm 将colWidgets的值转移到colitems中, 然后关闭自己
#         4.4.2 再在NewRow函数中,用函数 SaveDataToConfigModel 保存到配置模型上
#
#     """
#     colnames = []
#     defaultRowData = []  # 默认行数据用来新建行,  (dataformat.templateId, dataformat.fieldId), dataformat.fieldName, colType.field)
#     IsList = False  # 如果是列表, 则要改造成二维表实现表格.
#     IsSelectTable = False
#
#     def __init__(self, configItem: "ConfigModelItem" = None, 上级: "Standard.配置表容器" = None, *args, **kwargs):
#         super().__init__(configItem, 上级)
#         self.btnLayout = QHBoxLayout()
#         self.viewTable = QTableView(self.View)
#         self.table_model = QStandardItemModel()
#         self.modelRoot = self.table_model.invisibleRootItem()
#         self.btnAdd = QPushButton("+")
#         self.btnDel = QPushButton("-")
#         self.rowEditor = QDialog()
#         self.rowEditor.resize(300, 600)
#         self.SetupData(self.ConfigModelItem.value)
#         self.SetupView()
#         self.SetupEvent()
#
#     # def 值替换(self, 值):
#     #     """直接换一套值, 通常发生在参数模型改变的情况下"""
#     #
#     #     pass
#
#     def SetupView(self):
#         self.SetupLayout()
#         self.viewTable.verticalHeader().setHidden(True)
#         self.viewTable.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
#         self.viewTable.horizontalHeader().setStretchLastSection(True)
#         self.viewTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
#         self.viewTable.setSelectionMode(QAbstractItemViewSelectMode.SingleSelection)
#         self.viewTable.setSelectionBehavior(QAbstractItemViewSelectionBehavior.SelectRows)
#         pass
#
#     def SetupLayout(self):
#         self.btnLayout.addWidget(self.btnAdd)
#         self.btnLayout.addWidget(self.btnDel)
#         viewLayout = QVBoxLayout()
#         viewLayout.addWidget(self.viewTable, stretch=0)
#         viewLayout.addLayout(self.btnLayout, stretch=0)
#         self.View.setLayout(viewLayout)
#         self.View.layout()
#
#     def SetupData(self, raw_data:"list[Any]"):
#         from . import funcs
#         # funcs.Utils.print(raw_data)
#         self.viewTable.setModel(self.table_model)
#         self.table_model.clear()
#         if self.IsList:
#             list(map(lambda row: self.AppendRow(self.GetRowFromData([row])), raw_data))
#         elif self.IsSelectTable:
#             [self.AppendRow(self.GetRowFromData(["", row])) for row in raw_data[0]]
#             if raw_data[1] > -1:
#                 item = self.table_model.item(raw_data[1], 0)
#                 if item: item.setText("✔")
#         else:
#             list(map(lambda row: self.AppendRow(self.GetRowFromData(row)), raw_data))
#         self.table_model.setHorizontalHeaderLabels(self.colnames)
#         pass
#
#     def SetupEvent(self):
#         self.btnAdd.clicked.connect(lambda: self.NewRow())
#         self.btnDel.clicked.connect(lambda: self.RemoveRow())
#         self.viewTable.doubleClicked.connect(self.OnViewTableDoubleClicked)
#         pass
#
#     def OnViewTableDoubleClicked(self, index: "QModelIndex"):
#         row = index.row()
#         self.ShowRowEditor([self.table_model.item(row, col) for col in range(self.colnames.__len__())])
#
#     def AppendRow(self, row: "list[ConfigTableView.Item]"):
#         self.table_model.appendRow(row)
#         pass
#
#     def SelectRow(self, rownum):
#         row = self.table_model.index(rownum, 1)
#
#         self.viewTable.setCurrentIndex(row)
#         self.viewTable.selectionModel().clearSelection()
#         self.viewTable.selectionModel().select(self.viewTable.currentIndex(), QItemSelectionModel.Select)
#
#     def RemoveRow(self):
#         idx = self.viewTable.selectedIndexes()
#         if len(idx) == 0:
#             return
#         self.table_model.removeRow(idx[0].row(), idx[0].parent())
#         self.SaveDataToConfigModel()
#
#     def GetRowFromData(self, data: "list[str]"):
#         """
#         make TableRow from raw_data
#         根据所获取的数据生成行, 由于这个组件通常用于列表类型的配置, 因此data通常是list结构
#         如果有特殊结构请自己处理
#         """
#         # return list(map(lambda itemname: self.TableItem(self, itemname), data))
#         return [self.TableItem(self, 项名) for 项名 in data]
#
#     @abc.abstractmethod
#     def NewRow(self):
#         """点击+号调用的这个函数,
#         调用后一般要弹出一个表单, 让用户填写
#         目前, 解决方案已经很成熟,
#         新行和双击读取的编辑器可以一致使用NewRowFormWidget
#         NewRowFormWidget当初始化参数为空时, 就可以看做是新行
#         全部记录保存在NewRowFormWidget.colItems中, 再从外部读取
#         colItems 存的是表项值
#         colWidgets 存的是用户交互的组件
#         """
#         raise NotImplementedError()
#
#     @abc.abstractmethod
#     def ShowRowEditor(self, row: "list[ConfigTableView.Item]"):
#         """
#         双击弹出行修改编辑器
#         接受参数是一行的数据, 显示一个组件, 用来编辑这一行的数据"""
#         raise NotImplementedError()
#
#     @abc.abstractmethod
#     def SaveDataToConfigModel(self):
#         """保存到self.ConfigModelItem中, 而非数据库或json文件之类的内存之外的东西中"""
#         raise NotImplementedError()
#
#     class TableItem(QStandardItem,):
#
#         def __init__(self, superior:"ConfigTableView", name, value=None):
#             if not isinstance(superior, ConfigTableView):
#                 raise ValueError(f"superior must be instance of Configtableview not {superior}")
#             self.superior: "ConfigTableView" = superior
#
#             if type(name) != str:
#                 name = name.__str__()
#             super().__init__(name)
#             self.setToolTip(name)
#             self.setEditable(False)
#             self.widget = QWidget()
#             self.innerWidget = QWidget()
#             if value:
#                 self.setData(value)
#
#         def ShowAsWidget(self):
#             """这个数据项要展示为用户可操作的交互对象时,所用的组件,
#             这个功能现在已经废弃了
#             """
#             return None
#
#         def copySelf(self):
#             return ConfigTableView.TableItem(self.superior, self.text())
#
#         def SetValue(self, text, value=None):
#             self.setText(text)
#             self.setToolTip(text)
#             self.setData(value)
#
#         def GetData(self):
#             raise NotImplementedError()
#
#
# class ConfigItemLabelView(CustomConfigItemView):
#     """这个东西,是当配置项需要表示为
#     一个Label + 一个edit按钮而设计的.
#     Label读取保存的值, edit按钮点击后修改, 这样做的目的是用于检查输入的合法性.
#     """
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.label = QLabel()
#         self.edit_Btn = QPushButton("edit")
#         self.SetupView()
#         self.SetupEvent()
#         self.SetupData(self.ConfigModelItem.value)
#
#     def SetupView(self):
#         layout = QVBoxLayout()
#         layout.addWidget(self.label, stretch=0)
#         layout.addWidget(self.edit_Btn, stretch=0)
#         self.View.setLayout(layout)
#         pass
#
#     def SetupData(self, raw_data):
#         if re.search(r"\S", raw_data):
#             self.label.setText(raw_data)
#         else:
#             self.label.setText("[]")
#         pass
#
#     def SetupEvent(self):
#         self.edit_Btn.clicked.connect(self.on_edit_btn_clicked)
#
#     @abc.abstractmethod
#     def on_edit_btn_clicked(self):
#         raise NotImplementedError()


# def __init__(self):
#     pass


class Standard:
    class TableView(QTableView):
        def __init__(self, itemIsmovable=False, editable=False, itemIsselectable=False, title_name=""):
            super().__init__()
            if not editable:
                self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

            self.horizontalHeader().setStretchLastSection(True)

    class Item(QStandardItem):
        def __init__(self, name, data=None, movable=False, editable=False, selectable=False):
            super().__init__(name)
            if data:
                self.setData(data)

    class 配置表容器(QDialog):

        def __init__(我, 配置参数模型: "BaseConfigModel", 调用者=None):
            我.参数模型 = 配置参数模型
            我.调用者 = 调用者
            super().__init__()

class Geometry:
    class ArrowLine(QGraphicsLineItem):
        def __init__(self):
            super().__init__()
            self.triangle: "list[QPointF]" = []
            # self.arrowPoint= QPointF()

        def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem',
                  widget: typing.Optional[QWidget] = ...) -> None:
            super().paint(painter, option, widget)
            painter.setPen(self.pen())
            line = self.line()
            v = line.unitVector()  # 同向单位向量
            v.setLength(40)  # 设置单位向量长度
            v.translate(QPointF(line.dx() * 2 / 7, line.dy() * 2 / 7))  # dx,dy是直线作为向量的分解向量, 此步骤移动单位向量到 长2/5处

            n = v.normalVector()  # 获取到单位向量的法向量
            n.setLength(n.length() * 0.6)  # 设置法向量为原来的0.4倍
            n2 = n.normalVector().normalVector()  # 法向量的法向量,再求法向量,得到相反方向的法向量

            p1 = v.p2()  # 单位向量的终点
            p2 = n.p2()  # 法向量的终点
            p3 = n2.p2()  # 第二个法向量的终点
            self.triangle = [v.p2(), n.p2(), n2.p2()]
            painter.drawLine(line)
            painter.drawPolygon(p1, p2, p3)

        # def shape(self) -> QtGui.QPainterPath:
        #     super().shape()
        #     path = QPainterPath()
        #     path.addPolygon(QPolygonF(self.triangle))
        #     return path
