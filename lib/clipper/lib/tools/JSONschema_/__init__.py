"""
访问json的一个数据的constrain,先确定,type和是否为空,
然后根据type,选择range的读取方式,
1 不限定步伐范围形式, -->直接就可以做,范围显示为左右两个值的限定
2 限定步伐范围形式 -->也直接可以做,因为是数字,范围显示为一个数组
3 特殊意义数字迭代形式 -->需要结合特殊意义来看

"""


class DataType:
    int = 0
    float = 1
    iterobj = 2  # 特殊意义的数字
    iternum = 3  # 寻常的数字
    string = 4

class Empty:
    notAllow = 0
    allow = 1


class ViewLayout:
    Horizontal = 0
    Vertical = 1
    Freemode = 2


class NeedRatioFix:
    no = 0
    yes = 1
