# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'global_config_desc_extract_models.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2023/2/27 6:07'
"""

from .basic_models import *

@dataclass
class 类型_属性项_描述提取规则(基类_属性项):
    上级: "类型_模型_描述提取规则" = None

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
        pass

    def __eq__(self, other):
        return self.值 == other
        pass


@dataclass
class 类型_模型_描述提取规则(基类_模型):
    数据源: "类型_数据源_提取规则" = field(default_factory=lambda:baseClass.枚举命名.全局配置.描述提取规则.默认规则())

    牌组: 类型_属性项_描述提取规则 = field(default_factory=lambda: 类型_属性项_描述提取规则(
            字段名=枚举.全局配置.描述提取规则.牌组,
            展示名=译.描述提取规则_牌组,
            默认值=-1,
            从上级读数据=1,
            保存到上级=1,
            可展示=1,
            可展示中编辑=1,
            组件类型=枚举.组件类型.customize,
            自定义组件=widgets.自定义组件.牌组选择,
            组件传值方式=lambda 项: funcs.牌组操作.获取牌组名(项.值, "ALL DECKS"),
            属性项排序位置=0,

    ))
    模板: 类型_属性项_描述提取规则 = field(default_factory=lambda: 类型_属性项_描述提取规则(
            字段名=枚举.全局配置.描述提取规则.模板,
            展示名=译.描述提取规则_模板,
            默认值=-1,
            从上级读数据=1,
            保存到上级=1,
            可展示=1,
            可展示中编辑=1,
            组件类型=枚举.组件类型.customize,
            自定义组件=widgets.自定义组件.模板选择,
            组件传值方式=lambda 项: funcs.卡片模板操作.获取模板名(项.值, "ALL TEMPLATES"),
            属性项排序位置=1,
    ))
    字段: 类型_属性项_描述提取规则 = field(default_factory=lambda: 类型_属性项_描述提取规则(
            字段名=枚举.全局配置.描述提取规则.字段,
            展示名=译.描述提取规则_字段,
            默认值=-1,
            从上级读数据=1,
            保存到上级=1,
            可展示=1,
            可展示中编辑=1,
            组件类型=枚举.组件类型.customize,
            自定义组件=lambda 上级:widgets.自定义组件.字段选择(上级,上级.数据源.上级.模板.值),
            组件传值方式=lambda 项: funcs.卡片字段操作.获取字段名(项.上级.模板.值, 项.值, "ALL FIELDS"),
            属性项排序位置=2,
    ))
    标签: 类型_属性项_描述提取规则 = field(default_factory=lambda: 类型_属性项_描述提取规则(
            字段名=枚举.全局配置.描述提取规则.标签,
            展示名=译.描述提取规则_标签,
            默认值=[],
            从上级读数据=1,
            保存到上级=1,
            可展示=1,
            可展示中编辑=1,
            组件类型=枚举.组件类型.customize,
            自定义组件=widgets.自定义组件.标签选择,
            组件传值方式=lambda 项: funcs2.逻辑.缺省值(项.值, lambda x: x.__str__() if len(x)>0 else None, "ALL TAGS"),
            属性项排序位置=3,
    ))
    正则: 类型_属性项_描述提取规则 = field(default_factory=lambda: 类型_属性项_描述提取规则(
            字段名=枚举.全局配置.描述提取规则.正则,
            展示名=译.描述提取规则_正则,
            默认值="",
            从上级读数据=1,
            保存到上级=1,
            可展示=1,
            可展示中编辑=1,
            组件类型=枚举.组件类型.editable_label,
            有校验=1,
            校验函数=lambda 项, 值: funcs.Utils.正则合法性(值),
            属性项排序位置=4,
    ))
    长度: 类型_属性项_描述提取规则 = field(default_factory=lambda: 类型_属性项_描述提取规则(
            字段名=枚举.全局配置.描述提取规则.长度,
            展示名=译.描述提取规则_长度,
            默认值=0,
            从上级读数据=1,
            保存到上级=1,
            可展示=1,
            可展示中编辑=1,
            组件类型=枚举.组件类型.spin,
            有限制=1,
            限制=[0, 65535],
            属性项排序位置=5,
            # 自定义组件=lambda 组件生成器:widgets,

    ))
    同步: 类型_属性项_描述提取规则 = field(default_factory=lambda: 类型_属性项_描述提取规则(
            字段名=枚举.全局配置.描述提取规则.同步,
            展示名=译.描述提取规则_同步,
            默认值=True,
            从上级读数据=1,
            保存到上级=1,
            可展示=1,
            可展示中编辑=1,
            组件类型=枚举.组件类型.checkbox,
            属性项排序位置=6,
            # 自定义组件=lambda 组件生成器:widgets,
    ))
