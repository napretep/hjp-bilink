# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'global_config_desc_extract_models.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2023/2/27 6:07'


重要 这个地方用于全局配置中的一些配置,他们用表格展示数据.

"""

from .basic_models import *

类型_数据源_提取规则 = NewType("类型_数据源_提取规则", dict)
类型_数据源_pdf预设表 = NewType("类型_数据源_pdf预设表",dict)





@dataclass
class 基类_属性项_所有的表格行的列项(基类_属性项):
    从上级读数据:int = 1,
    保存到上级:int = 1,
    可展示:int = 1,
    可展示中编辑:int = 1,

    @property
    def 值(self):
        if self.上级 and self.上级.数据源:
            return self.上级.数据源[self.字段名]
        else:
            return self.默认值
        pass

    def 设值(self, value):
        if self.上级 and self.上级.数据源:

            self.上级.数据源[self.字段名] = value
        else:
            print("设值失败")
        pass

    def __eq__(self, other):
        return self.值 == other
        pass


@dataclass
class 基类_模型_所有的表格行模型(基类_模型):
    pass



@dataclass
class 类型_属性项_描述提取规则(基类_属性项_所有的表格行的列项):
    上级: "类型_模型_描述提取规则" = None

@dataclass
class 类型_模型_描述提取规则(基类_模型_所有的表格行模型):
    数据源: "类型_数据源_提取规则" = field(default_factory=lambda:baseClass.枚举命名.全局配置.描述提取规则.默认规则())

    牌组: 类型_属性项_描述提取规则 = field(default_factory=lambda: 类型_属性项_描述提取规则(
            字段名=枚举.全局配置.描述提取规则.牌组,
            展示名=译.描述提取规则_牌组,
            值类型=枚举.值类型.整数,
            默认值=-1,
            组件类型=枚举.组件类型.customize,
            # 自定义组件=widgets.自定义组件.牌组选择,
            自定义组件=lambda 组件生成器:函数库_UI生成.自定义().属性项组件.牌组选择(组件生成器),
            函数_传值到组件=lambda 项: funcs.牌组操作.获取牌组名(项.值, "ALL DECKS"),
            属性项排序位置=0,

    ))
    模板: 类型_属性项_描述提取规则 = field(default_factory=lambda: 类型_属性项_描述提取规则(
            字段名=枚举.全局配置.描述提取规则.模板,
            展示名=译.描述提取规则_模板,
            值类型=枚举.值类型.整数,
            默认值=-1,
            组件类型=枚举.组件类型.customize,
            # 自定义组件=widgets.自定义组件.模板选择,
            自定义组件=lambda 组件生成器:函数库_UI生成.自定义().属性项组件.模板选择(组件生成器),
            函数_传值到组件=lambda 项: funcs.卡片模板操作.获取模板名(项.值, "ALL TEMPLATES"),
            属性项排序位置=1,
    ))
    字段: 类型_属性项_描述提取规则 = field(default_factory=lambda: 类型_属性项_描述提取规则(
            字段名=枚举.全局配置.描述提取规则.字段,
            展示名=译.描述提取规则_字段,
            值类型=枚举.值类型.整数,
            默认值=-1,
            组件类型=枚举.组件类型.customize,
            # 自定义组件=lambda 上级:widgets.自定义组件.字段选择(上级,上级.数据源.上级.模板.值),
            自定义组件=lambda 上级:函数库_UI生成.自定义().属性项组件.字段选择(上级,上级.数据源.上级.模板.值),
            函数_传值到组件=lambda 项: funcs.卡片字段操作.获取字段名(项.上级.模板.值, 项.值, "ALL FIELDS"),
            属性项排序位置=2,
    ))
    标签: 类型_属性项_描述提取规则 = field(default_factory=lambda: 类型_属性项_描述提取规则(
            字段名=枚举.全局配置.描述提取规则.标签,
            展示名=译.描述提取规则_标签,
            值类型=枚举.值类型.文本,
            默认值=[],
            组件类型=枚举.组件类型.customize,
            自定义组件=lambda 组件生成器:函数库_UI生成.自定义().属性项组件.标签选择(组件生成器),
            # 自定义组件=widgets.自定义组件.标签选择,
            函数_传值到组件=lambda 项: funcs.逻辑.缺省值(项.值, lambda x: x.__str__() if len(x)>0 else None, "ALL TAGS"),
            属性项排序位置=3,
    ))
    正则: 类型_属性项_描述提取规则 = field(default_factory=lambda: 类型_属性项_描述提取规则(
            字段名=枚举.全局配置.描述提取规则.正则,
            展示名=译.描述提取规则_正则,
            值类型=枚举.值类型.文本,
            默认值="",
            组件类型=枚举.组件类型.editable_label,
            有校验=1,
            函数_赋值校验=lambda 项, 值: funcs.Utils.正则合法性(值),
            属性项排序位置=4,
    ))
    长度: 类型_属性项_描述提取规则 = field(default_factory=lambda: 类型_属性项_描述提取规则(
            字段名=枚举.全局配置.描述提取规则.长度,
            展示名=译.描述提取规则_长度,
            默认值=0,
            值类型=枚举.值类型.整数,
            组件类型=枚举.组件类型.spin,
            有组件限制=1,
            组件限制=[0, 65535],
            属性项排序位置=5,
            # 自定义组件=lambda 组件生成器:widgets,

    ))
    同步: 类型_属性项_描述提取规则 = field(default_factory=lambda: 类型_属性项_描述提取规则(
            字段名=枚举.全局配置.描述提取规则.同步,
            展示名=译.描述提取规则_同步,
            值类型=枚举.值类型.布尔,
            默认值=True,
            组件类型=枚举.组件类型.checkbox,
            属性项排序位置=6,
            # 自定义组件=lambda 组件生成器:widgets,
    ))





@dataclass
class 类型_属性项_pdf预设表(基类_属性项_所有的表格行的列项):
    上级: "类型_模型_pdf预设表" = None
    pass

@dataclass
class 类型_模型_pdf预设表(基类_模型_所有的表格行模型):
    数据源:"类型_数据源_pdf预设表" = field(default_factory=lambda: 枚举.全局配置.PDF链接.预设pdf表_单行信息.默认数据())

    路径:类型_属性项_pdf预设表= field(default_factory=lambda:类型_属性项_pdf预设表(
            字段名=枚举.全局配置.PDF链接.预设pdf表_单行信息.路径,
            展示名=译.PDF链接_预设pdf表单行列名_pdf路径,
            值类型=枚举.值类型.文件,
            默认值="",
            组件类型=枚举.组件类型.text,
            属性项排序位置=0,
    ))

    名称:类型_属性项_pdf预设表= field(default_factory=lambda:类型_属性项_pdf预设表(
            字段名=枚举.全局配置.PDF链接.预设pdf表_单行信息.显示名,
            展示名=译.PDF链接_预设pdf表单行列名_展示名,
            值类型=枚举.值类型.文本,
            默认值="",
            组件类型=枚举.组件类型.text,
            属性项排序位置=1,
    ))
    样式:类型_属性项_pdf预设表= field(default_factory=lambda:类型_属性项_pdf预设表(
            字段名=枚举.全局配置.PDF链接.预设pdf表_单行信息.样式,
            展示名=译.PDF链接_预设pdf表单行列名_样式,
            值类型=枚举.值类型.文本,
            默认值="",
            组件类型=枚举.组件类型.text,
            属性项排序位置=2,
    ))
    是否显示页码:类型_属性项_pdf预设表= field(default_factory=lambda:类型_属性项_pdf预设表(
            字段名=枚举.全局配置.PDF链接.预设pdf表_单行信息.是否显示页码,
            展示名=译.PDF链接_预设pdf表单行列名_显示页码,
            值类型=枚举.值类型.布尔,
            默认值=True,
            组件类型=枚举.组件类型.radio,
            属性项排序位置=3,
    ))