# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'view_self_models.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2023/2/27 5:56'
"""


from .basic_models import *

@dataclass
class 类型_视图本身属性项(基类_属性项):
    上级: "类型_视图本身模型" = None

    @property
    def 值(self):
        if self.上级 and self.上级.数据源:
            if self.从上级读数据:
                return self.上级.数据源.meta[self.字段名]
            elif self._读取函数:
                return self.读取函数(self)
            else:
                raise NotImplementedError()
        else:
            return self.默认值

    def 设值(self, value):
        if self.上级:
            if self.从上级读数据:
                self.上级.数据源.meta[self.字段名] = value
            elif self._保存值的函数:
                self.保存值的函数(self, value)
            else:
                raise NotImplementedError()

            if self.上级.UI创建完成:
                self.上级.数据源.数据更新.视图编辑发生()
            if self._保存后执行:
                self.保存后执行(self)
            funcs.GviewOperation.save(self.上级.数据源)

    def __eq__(self, other):
        return self.值 == other


@dataclass
class 类型_视图本身模型(基类_模型):
    数据源: "类型_视图数据" = None

    # def __post_init__(self):
    #     for key in self.__dict__.keys():
    #         if isinstance(self.__dict__[key], 类型_视图本身属性项):
    #             项: 类型_视图本身属性项 = self.__dict__[key]
    #             项.上级 = self

    # def 初始化(self, 视图数据):
    #     self.数据源: "类型_视图数据" = 视图数据
    #     for key in self.__dict__.keys():
    #         if isinstance(self.__dict__[key], 类型_视图本身属性项):
    #             项: 类型_视图本身属性项 = self.__dict__[key]
    #             项.上级 = self
    #     return self

    编号: 类型_视图本身属性项 = field(default_factory=lambda: 类型_视图本身属性项(
            字段名=枚举.视图.编号,
            展示名=译.视图编号,
            说明="",
            从上级读数据=0,  # 从上级读数据的意思是从上级读数据到视图数据中,
            保存到上级=0,
            可展示=1,  # 需要对应的展示组件, 这里的展示是指展示在卡片详情中
            可展示中编辑=0,  # 需要对应的可展示中编辑组件, 与可展示联合判断
            用户可访=1,  # 用户可以用自定义的python语句访问到这个变量的值
            组件类型=枚举.组件类型.label,  # 展示用的组件

            _读取函数=lambda 项: 项.上级.数据源.uuid,
            _保存值的函数=None,
            默认值="4b9556bb",
            值类型=枚举.值类型.文本,
            值解释="'4b9556bb' or '6acc4bde'"
    ))

    名称: 类型_视图本身属性项 = field(default_factory=lambda: 类型_视图本身属性项(
            字段名=枚举.视图.名称,
            展示名=译.视图名,
            说明="",
            从上级读数据=0,  # 从上级读数据的意思是从上级读数据到视图数据中,
            保存到上级=0,
            可展示=1,  # 需要对应的展示组件, 这里的展示是指展示在卡片详情中
            可展示中编辑=1,  # 需要对应的可展示中编辑组件, 与可展示联合判断
            用户可访=1,  # 用户可以用自定义的python语句访问到这个变量的值
            组件类型=枚举.组件类型.editable_label,  # 展示用的组件

            _读取函数=lambda 项: 项.上级.数据源.name,
            _保存值的函数=lambda 项, 新值: funcs.GviewOperation.重命名(项.上级.数据源, 新值),
            # _保存后执行=,
            默认值="",
            值类型=枚举.值类型.文本,
            值解释="'abc' or 'apple'"
    ))

    创建时间: 类型_视图本身属性项 = field(default_factory=lambda: 类型_视图本身属性项(
            字段名=枚举.视图.创建时间,
            展示名=译.视图创建时间,
            从上级读数据=1,  # 从上级读数据的意思是从上级读数据到视图数据中,
            保存到上级=1,
            可展示=1,  # 需要对应的展示组件, 这里的展示是指展示在卡片详情中
            用户可访=1,  # 用户可以用自定义的python语句访问到这个变量的值
            组件类型=枚举.组件类型.time,  # 展示用的组件
            默认值=int(time.time()),
            值类型=枚举.值类型.时间戳,
            值解释="1676747497 or 1676661096",
    ))
    上次访问: 类型_视图本身属性项 = field(default_factory=lambda: 类型_视图本身属性项(
            字段名=枚举.视图.上次访问,
            展示名=译.视图上次访问,
            从上级读数据=1,  # 从上级读数据的意思是从上级读数据到视图数据中,
            保存到上级=1,
            可展示=1,  # 需要对应的展示组件, 这里的展示是指展示在卡片详情中
            用户可访=1,  # 用户可以用自定义的python语句访问到这个变量的值
            组件类型=枚举.组件类型.time,  # 展示用的组件
            默认值=int(time.time()),
            值类型=枚举.值类型.时间戳,
            值解释="1676747497 or 1676661096",
    ))
    上次编辑: 类型_视图本身属性项 = field(default_factory=lambda: 类型_视图本身属性项(
            字段名=枚举.视图.上次编辑,
            展示名=译.视图上次编辑,
            从上级读数据=1,  # 从上级读数据的意思是从上级读数据到视图数据中,
            保存到上级=1,
            可展示=1,  # 需要对应的展示组件, 这里的展示是指展示在卡片详情中
            用户可访=1,  # 用户可以用自定义的python语句访问到这个变量的值
            组件类型=枚举.组件类型.time,  # 展示用的组件
            默认值=int(time.time()),
            值类型=枚举.值类型.时间戳,
            值解释="1676747497 or 1676661096",
    ))
    上次复习: 类型_视图本身属性项 = field(default_factory=lambda: 类型_视图本身属性项(
            字段名=枚举.视图.上次复习,
            展示名=译.视图上次复习,
            从上级读数据=1,  # 从上级读数据的意思是从上级读数据到视图数据中,
            保存到上级=1,
            可展示=1,  # 需要对应的展示组件, 这里的展示是指展示在卡片详情中
            用户可访=1,  # 用户可以用自定义的python语句访问到这个变量的值
            组件类型=枚举.组件类型.time,  # 展示用的组件
            默认值=0,
            值类型=枚举.值类型.时间戳,
            值解释="1676747497 or 1676661096",
    ))
    访问次数: 类型_视图本身属性项 = field(default_factory=lambda: 类型_视图本身属性项(
            字段名=枚举.视图.访问次数,
            展示名=译.视图访问次数,
            从上级读数据=1,  # 从上级读数据的意思是从上级读数据到视图数据中,
            保存到上级=1,
            可展示=1,  # 需要对应的展示组件, 这里的展示是指展示在卡片详情中
            用户可访=1,  # 用户可以用自定义的python语句访问到这个变量的值
            组件类型=枚举.组件类型.label,  # 展示用的组件
            默认值=0,
            值类型=枚举.值类型.整数,
            值解释="1 or 5",
    ))
    到期结点数: 类型_视图本身属性项 = field(default_factory=lambda: 类型_视图本身属性项(
            字段名=枚举.视图.到期结点数,
            展示名=译.视图到期结点数,
            从上级读数据=0,  # 从上级读数据的意思是从上级读数据到视图数据中,
            保存到上级=0,
            可展示=1,  # 需要对应的展示组件, 这里的展示是指展示在卡片详情中
            用户可访=1,  # 用户可以用自定义的python语句访问到这个变量的值
            _读取函数=lambda 项: funcs.GviewOperation.getDueCount(项.上级.数据源),
            组件类型=枚举.组件类型.label,  # 展示用的组件
            默认值=0,
            值类型=枚举.值类型.整数,
            值解释="1 or 5",
    ))

    主要结点: 类型_视图本身属性项 = field(default_factory=lambda: 类型_视图本身属性项(
            字段名=枚举.视图.主要结点,
            展示名=译.视图主要结点,
            保存到上级=0,
            从上级读数据=0,
            可展示=1,  # 需要对应的展示组件, 这里的展示是指展示在卡片详情中
            用户可访=1,  # 用户可以用自定义的python语句访问到这个变量的值
            _读取函数=lambda 项: funcs.GviewOperation.获取主要结点编号(项.上级.数据源),
            组件类型=枚举.组件类型.label,  # 展示用的组件
            函数_传值到组件=lambda 项: "\n".join([f"{结点编号}:{funcs.GviewOperation.获取视图结点描述(项.上级.数据源, 结点编号)}" for 结点编号 in 项.值]),
            默认值=[],
            值类型=枚举.值类型.列表,
            值解释="['1630171513585','1630171513679'] or ['1630171513585','4b9556bb']",
    ))
    缓存: 类型_视图本身属性项 = field(default_factory=lambda: 类型_视图本身属性项(
            字段名=枚举.视图.视图卡片内容缓存,
            展示名=枚举.视图.视图卡片内容缓存,
            说明="",
            保存到上级=0,
            从上级读数据=0,  # 从上级读数据的意思是从上级读数据到视图数据中,
            可展示=0,  # 需要对应的展示组件, 这里的展示是指展示在卡片详情中
            可展示中编辑=0,  # 需要对应的可展示中编辑组件, 与可展示联合判断
            用户可访=0,  # 用户可以用自定义的python语句访问到这个变量的值
            _读取函数=lambda 项: "",
            组件类型=枚举.组件类型.none,  # 展示用的组件
            值类型=枚举.值类型.列表,
            # 函数_传值到组件=None,
            # 保存值的函数=None, # 当不能直接保存到视图中时, 采用这个函数保存
            # 有限制=0,
            # 限制=[0, funcs.G.src_admin.MAXINT],
            # 自定义组件=None,
    ))

    pass
