# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'view_batch_node_models.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2023/2/27 6:04'
"""

from .basic_models import *
from .view_node_models import 类型_视图结点模型,类型_视图结点数据源,类型_视图结点集模型

@dataclass
class 类型_视图批量结点数据源:
    视图数据:"类型_视图数据"=None
    结点编号集:"list[类型_结点编号]"=None
    pass


class 类型_集模型_批量视图结点(类型_视图结点集模型):
    """批量修改"""
    def __init__(self,批量结点:"list[str]",*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.批量结点=批量结点

    def 创建UI(self):
        伪数据 = 类型_视图结点集模型(self.上级,{"test_node":funcs.GviewOperation.依参数确定视图结点数据类型模板()})
        # 伪数据 = funcs.GviewOperation.create(nodes={"test_node":{}},name="test gview",need_open=False,need_save=False)
        对话框 = funcs.组件定制.对话窗口(译.结点批量编辑)
        表单布局 =QFormLayout()
        # def 执行函数():
        #     return
        组件名修改 = lambda 属性,组件名:lambda x, y: 组件名.setText(属性.展示名 + f"({译.已修改})")
        批量结点赋值 = lambda 属性,组件名:lambda x, y:[self[结点编号][属性.字段名].设值(y) for 结点编号 in self.批量结点]
        # 打印观察 = lambda 属性,组件名:lambda x, y:funcs.Utils.print([self[结点编号] for 结点编号 in self.批量结点])
        for 属性名,属性 in 伪数据["test_node"].属性字典.items():
            if 属性.可批量编辑:
                组件名 = funcs.组件定制.文本框(属性.展示名,True)
                组件 = 函数库_UI生成.组件(属性)
                组件.当完成赋值.append(组件名修改(属性,组件名))
                组件.当完成赋值.append(批量结点赋值(属性,组件名))
                组件.当完成赋值.append(lambda x,y:对话框.adjustSize())
                # 组件.当完成赋值.append(lambda x, y:funcs.Utils.print([self[结点编号].__str__() for 结点编号 in self.批量结点]))
                表单布局.addRow(组件名,组件)

        对话框.setLayout(表单布局)
        return 对话框
        pass