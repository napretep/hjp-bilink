from .basic_widgets import *


# class 新建视图(QDialog):
#     def __init__(self):
#         super().__init__()
#         self.视图的名字 = ""
#         self.选中的配置 = None
#         self.确认建立 = False
#
#         # def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
class 属性项组件:
    class 基类_项组件基础(QWidget):
        def __init__(self, 上级):
            super().__init__()
            self.上级: G.safe.models.函数库_UI生成.组件 = 上级
            self.当完成赋值 = G.safe.hookers.当模型的属性项组件_完成赋值()

        @abstractmethod
        def setValue(self, value):
            raise NotImplementedError()

    class 基本选择类(基类_项组件基础):
        def __init__(self, 上级):
            super().__init__(上级)

            self.ui组件 = G.safe.funcs.组件定制.文本框(开启自动换行=True)
            self.修改按钮 = G.safe.funcs.组件定制.按钮_修改()
            self.修改按钮.clicked.connect(self.on_edit_button_clicked)

            G.safe.funcs.组件定制.组件组合({框: QHBoxLayout(), 子: [
                {件: self.ui组件, 占: 1}, {件: self.修改按钮, 占: 0}]},
                                           self)
            self.ui组件.setText(self.get_name(self.上级.数据源.值))
            self.不选信息 = 译.不选等于全选

        def on_edit_button_clicked(self):
            w = self.chooser()
            w.exec()
            if w.结果 is None or (type(w.结果) in [int, float] and w.结果 < 0) or \
                    (type(w.结果) == list and len(w.结果) == 0):
                showInfo(self.不选信息)

            self.setValue(w.结果)

        def setValue(self, value):
            self.ui组件.setText(self.get_name(value))
            new_value = value if type(value) in [int, float, bool, str, complex] else value.copy() if "copy" in value.__dir__() else value
            self.上级.数据源.设值(new_value)
            self.当完成赋值(self, new_value)
            # funcs.Utils.print(self,new_value)
            pass

        def chooser(self) -> "QDialog":
            raise NotImplementedError()  # """打开某一种选择器"""

        def get_name(self, value): raise NotImplementedError()

    class 角色多选(基本选择类):
        """卡片角色多选"""

        def __init__(self, 上级):
            super().__init__(上级)
            self.属性项: "G.safe.models.类型_视图结点属性项" = self.上级.数据源
            self.配置模型 = self.属性项.上级.数据源.模型.上级.config_model
            self.角色表 = eval(self.配置模型.data.node_role_list.value)
            self.值修正()
            self.不选信息 = 译.不选角色等于不选
            self.ui组件.setText(self.get_name(self.上级.数据源.值))

        def 值修正(self):
            角色选中表: 'list[str]' = self.属性项.值
            新表 = [角色 for 角色 in 角色选中表 if 角色 in range(len(self.角色表))]
            self.属性项.设值(新表)

        def chooser(self):
            """需要获取到config,所以需要获取到view uuid"""
            return 导入.selector_widgets.role_chooser_for_node(self.属性项.值, self.角色表)
            pass

        def get_name(self, value):
            return G.safe.funcs.逻辑.缺省值(value, lambda x: [self.角色表[idx] for idx in x if
                                                               idx in range(len(self.角色表))],
                                             f"<img src='{G.src.ImgDir.cancel}' width=10 height=10> no role").__str__()

    class 牌组选择(基本选择类):

        def chooser(self): return 导入.selector_widgets.universal_deck_chooser()

        def get_name(self, value): return mw.col.decks.name_if_exists(value) if value > 0 else "ALL DECKS"

        # def __init__(self, 上级):
        #     super().__init__(上级)
        #     self.ui组件.setText(self.get_name(self.上级.数据源.值))

    class 模板选择(基本选择类):

        def get_name(self, value): return mw.col.models.get(value)["name"] if value > 0 else "ALL TEMPLATES"

        def chooser(self): return 导入.selector_widgets.universal_template_chooser()

        # def __init__(self, 上级):
        #     super().__init__(上级)
        #     self.ui组件.setText(self.get_name(self.上级.数据源.值))

    class 字段选择(基本选择类):
        def __init__(self, 上级, 模板编号):
            self.模板编号 = -1
            super().__init__(上级)
            self.检查模板编号合法性(模板编号)

        def 检查模板编号合法性(self, value):
            self.模板编号 = value
            if self.模板编号 < 0:
                self.修改按钮.setEnabled(False)
            else:
                self.修改按钮.setEnabled(True)
            self.ui组件.setText(self.get_name(self.上级.数据源.值))

        def chooser(self):
            return 导入.selector_widgets.universal_field_chooser(self.模板编号)

        def get_name(self, value):
            return G.safe.funcs.卡片字段操作.获取字段名(self.模板编号, value, "ALL FIELDS")

    class 标签选择(基本选择类):
        def chooser(self):
            return 导入.selector_widgets.universal_tag_chooser(self.上级.数据源.值)
            pass

        def get_name(self, value):
            return G.safe.funcs.逻辑.缺省值(value, lambda x: x, "ALL TAGS").__str__()
            # if len(value)==0:
            #     return "ALL TAGS"
            # return value.__str__()
            # pass

    class 视图配置选择(基本选择类):
        def chooser(self) -> "QDialog":
            return 导入.selector_widgets.view_config_chooser()

        def get_name(self, value):
            value:G.safe.baseClass.IdName = value
            return G.safe.funcs.逻辑.缺省值(value, lambda x:x.name if x else None,
                                             f"<img src='{G.src.ImgDir.config}' width=16 height=16> new config").__str__()

        def __init__(self, 上级):
            super().__init__(上级)
            self.不选信息 = 译.不选等于新建
