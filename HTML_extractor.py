"""
写了个HTML toObject toJSON 解析器
"""
import json
from abc import ABCMeta
from html.parser import HTMLParser
from typing import List, Tuple, Dict


class HTML_element:
    """
    这个是HTML基本元素对象,标签名,属性,文本值,还有孩子,父树
    """

    def __init__(self, tag="", attrs: Tuple[str, str] = None, parent=None,
                 data: List[str] = None, kids: List = None):
        self.attrs = attrs if attrs is not None else ("", "")
        self.tagname = tag
        self.data = data if data is not None else []
        self.kids = kids if kids is not None else []
        self.parent = parent

    def HTML_JSONGen(self, obj: List[HTML_element]):
        """利用深度优先遍历建立HTML的JSON对应"""
        HTML_dict = []
        stack_elem: List[HTML_element] = []  # element 对象
        stack_dict: List[Dict] = []  # element 字典
        stack: List[HTML_element] = []  # 原始对象
        stack += obj  # 入栈
        while len(stack) > 0:  # 当栈内有元素时
            el: HTML_element = stack.pop(0)  # 弹出元素
            stack = el.kids + stack  # 将孩子纳入
            cur = {}  # 提取字典
            dict_attrs = {}
            for tp in el.attrs:
                if isinstance(tp, tuple) and len(tp) == 2 and tp[0] != '' and tp[1] != '':
                    dict_attrs[tp[0]] = tp[1]
            cur["tagName"], cur["attrs"], cur["data"], cur["kids"] = el.tagname, dict_attrs, el.data, []
            if len(stack_elem) == 0:
                stack_elem.append(el)
                stack_dict.append(cur)
                HTML_dict.append(cur)
            else:
                while len(stack_elem) > 0 and el not in stack_elem[-1].kids:
                    stack_elem.pop()
                    stack_dict.pop()
                if len(stack_elem) > 0:
                    stack_dict[-1]["kids"].append(cur)
                else:
                    HTML_dict.append(cur)
                stack_elem.append(el)
                stack_dict.append(cur)
        return HTML_dict


class HTML_extractor(HTMLParser, metaclass=ABCMeta):
    """读取一些有用的信息"""

    def __init__(self):
        HTMLParser.__init__(self)
        self.root: List[HTML_element] = []
        self.parent: HTML_element = HTML_element()
        self.stack: List[str] = []
        self.curr: HTML_element = HTML_element()
        self.tagdict: Dict[str, List[HTML_element]] = {"unknown": []}
        self.count = 0

    def handle_starttag(self, tag, attrs):
        """覆盖,这是一个深度优先遍历,为了方便取值,还有一个根据标签类型分类的便利指针"""
        el = HTML_element(tag=tag, attrs=attrs)
        if len(self.stack) == 0:  # 一开始栈里还没有东西
            self.root.append(el)  # 那就作为根节点
            self.stack.append(tag)  # 入栈
            self.curr = el  # 初始化
            self.curr.parent = None
        else:
            self.stack.append(tag)  # 必须入栈
            self.curr.kids.append(el)  # 如果栈不空,那么curr必然存在,那么就要添加为孩子
            self.parent = self.curr  # 调转链表
            self.curr = self.curr.kids[-1]  # 取出前面的孩子
            self.curr.parent = self.parent
        if self.tagdict.get(tag) is None:
            self.tagdict[tag] = []
        self.tagdict[tag].append(el)

    def handle_startendtag(self, tag, attrs):
        """覆盖"""
        el = HTML_element(tag=tag, attrs=attrs)
        if len(self.stack) == 0:
            self.root.append(el)
            self.curr = el
            self.curr.parent = None
        else:
            self.curr.kids.append(el)
        if self.tagdict.get(tag) is None:
            self.tagdict[tag] = []
        self.tagdict[tag].append(el)

    def handle_data(self, data):
        """覆盖"""
        if self.curr is not None:
            self.curr.data.append(data)
        else:
            el = HTML_element(tag="unknown", data=[data])
            self.root.append(el)
            self.tagdict[el.tagname].append(el)
            print("堆栈已空!")

    def handle_endtag(self, tag):
        """覆盖"""
        if len(self.stack) > 0 and self.stack[-1] == tag:
            self.stack.pop()
            self.curr = self.curr.parent

    def clear(self):
        """清空方便下次使用"""
        root = self.root
        tagdict = self.tagdict
        return [root, tagdict]


# class HTML_converter:
#     """格式转换综合对象"""
#     def __init__(self):
#         self.extractor=HTML_extractor()
#         self.text=""
#
#     def convert(self,text):
#
#
#     def HTML_JSONGen(self, obj: List[HTML_element]):
#         """利用深度优先遍历建立HTML的JSON对应"""
#         HTML_dict = []
#         stack_elem: List[HTML_element] = []  # element 对象
#         stack_dict: List[Dict] = []  # element 字典
#         stack: List[HTML_element] = []  # 原始对象
#         stack += obj  # 入栈
#         while len(stack) > 0:  # 当栈内有元素时
#             el: HTML_element = stack.pop(0)  # 弹出元素
#             stack = el.kids + stack  # 将孩子纳入
#             cur = {}  # 提取字典
#             dict_attrs = {}
#             for tp in el.attrs:
#                 if isinstance(tp, tuple) and len(tp) == 2 and tp[0] != '' and tp[1] != '':
#                     dict_attrs[tp[0]] = tp[1]
#             cur["tagName"], cur["attrs"], cur["data"], cur["kids"] = el.tagname, dict_attrs, el.data, []
#             if len(stack_elem) == 0:
#                 stack_elem.append(el)
#                 stack_dict.append(cur)
#                 HTML_dict.append(cur)
#             else:
#                 while len(stack_elem) > 0 and el not in stack_elem[-1].kids:
#                     stack_elem.pop()
#                     stack_dict.pop()
#                 if len(stack_elem) > 0:
#                     stack_dict[-1]["kids"].append(cur)
#                 else:
#                     HTML_dict.append(cur)
#                 stack_elem.append(el)
#                 stack_dict.append(cur)
#         return HTML_dict

if __name__ == "__main__":
    eg = HTML_extractor()
    egHTML = """ 开始
    <div class="ProfileHeader-contentHead">
        <h1 class="ProfileHeader-title">
            <span class="ProfileHeader-name">十五</span>
            <span class="ztext ProfileHeader-headline">想想,和平演变是如何植入思想的?&gt;</span>
        </h1>
    </div> 结束
"""
    eg.feed(egHTML)
    d = HTML_JSONGen(eg.root)
    print(json.dumps(d, indent=4, ensure_ascii=False))
    print(eg.clear()[1])
