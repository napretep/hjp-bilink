# -*- coding:utf-8 -*-
"""
写了个HTML toObject toJSON 解析器
"""
import functools
import re
import types
import xml.dom.minidom as XMLParser
from html.parser import HTMLParser
from typing import List, Tuple, Dict

if __name__ == "__main__":
    from utils import console
    # from inputObj import *

else:
    from .utils import console


def logfunc(func):
    """Calculate the execution time of func."""

    @functools.wraps(func)
    def wrap_log(*args, **kwargs):
        """包装函数"""
        console(func.__name__ + "开始").noNewline.log.end()
        result = func(*args, **kwargs)
        console(func.__name__ + "结束").noNewline.log.end()
        return result

    return wrap_log


class MetaClass_loger(type):
    """"监控元类"""

    def __new__(mcs, name, bases, attr_dict):
        for k, v in attr_dict.items():
            # If the attribute is function type, use the wrapper function instead
            if isinstance(v, types.FunctionType):
                attr_dict[k] = logfunc(v)
        return type.__new__(mcs, name, bases, attr_dict)


class HTML_element:
    """
    这个是HTML基本元素对象,标签名,属性,文本值,还有孩子,父树
    """

    def __init__(self, tag="", attrs: Tuple[str, str] = None, parent=None,
                 data: List[str] = None, kids: List = None, end=False, singleTag=False, **args):
        self.__dict__ = args
        self.attrs = attrs if attrs is not None else ("", "")
        self.tagname = tag
        self.data = data if data is not None else []
        self.kids = kids if kids is not None else []
        self.parent = parent
        self.end = end
        self.singleTag = singleTag

    def __str__(self, s=""):
        console(self.attrs.__str__()).log.end()
        console(self.data.__str__()).log.end()
        attrs = functools.reduce(lambda x, y: x + y, map(lambda t: f"""{t[0]}='{t[1]}' """, self.attrs), "")
        s += f"""<{self.tagname} {attrs}>"""
        kids = self.kids
        while len(kids) > 0:
            for i in range(len(kids)):
                obj = kids[i]


class HTML_extractor(HTMLParser):
    """读取一些有用的信息"""

    # __metaclass__ = MetaClass_loger
    def __init__(self):
        HTMLParser.__init__(self)
        self.root: List[HTML_element] = []
        self.parent: HTML_element = HTML_element()
        self.stack: List[HTML_element] = []
        self.curr: HTML_element = HTML_element()
        self.tagdict: Dict[str, List[HTML_element]] = {"unknown": []}
        self.count = 0

    def handle_starttag(self, tag, attrs):
        """覆盖,这是一个深度优先遍历,为了方便取值,还有一个根据标签类型分类的便利指针"""
        el = HTML_element(tag=tag, attrs=attrs)
        if len(self.stack) == 0:  # 一开始栈里还没有东西
            self.root.append(el)  # 那就作为根节点
            self.curr = el  # 初始化
            self.curr.parent = None
        else:
            self.curr.kids.append(el)  # 如果栈不空,那么curr必然存在,那么就要添加为孩子
            self.parent = self.curr  # 调转链表
            self.curr = self.curr.kids[-1]  # 取出前面的孩子
            self.curr.parent = self.parent
        if self.tagdict.get(tag) is None:
            self.tagdict[tag] = []
        self.stack.append(el)
        self.tagdict[tag].append(el)

    def handle_startendtag(self, tag, attrs):
        """覆盖"""
        el = HTML_element(tag=tag, attrs=attrs, singleTag=True)
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
        if len(self.stack) > 0:
            if self.stack[-1].tagname == tag:
                self.stack.pop()
                self.curr.end = True
                self.curr = self.curr.parent
            else:
                legacy = self.stack.pop()
                # self.stack.data.append()

    def clear(self):
        """清空方便下次使用"""
        self.reset()
        return self


class HTML_converter(object, metaclass=MetaClass_loger):
    """格式转换综合对象"""

    def __init__(self, **args):
        self.parse = XMLParser.parseString
        self.text = ""
        self.domRoot: XMLParser.Element = None
        self.container: str = "virtualRoot"
        self.objRoot: List[HTML_element] = []
        self.dictLiTag: Dict[str, HTML_element] = {}
        self.objJSON: Dict = {}
        self.HTML_text = ""

    @property
    def back(self):
        """将HTML文本串输入此处,内部转化输出为JSON和OBJ"""
        self.objRoot = self.extractor.root[0].kids
        self.dictLiTag = self.extractor.tagdict
        self.objJSON = {"tree": self.HTML_JSONGen(self.objRoot), self.container: self.extractor.root[0].data}
        return self

    def HTML_addcontainer(self, text):
        """清理文本, 适应解析器,"""
        self.text = f"<{self.container}>" + text + f"</{self.container}>"

        return self

    def feed(self, text):
        """把接口变得简单一点,domRoot修改"""
        self.domRoot = self.HTML_addcontainer(text).parse(self.text).documentElement
        return self

    def getElementsByTagName(self, tagName):
        """获取TAG"""
        pass

    @property
    def text_get(self, node=None):
        """外层"""
        if node is None or not isinstance(node, XMLParser.Element):
            node = self.domRoot
        text = self.text_get_(node)
        self.HTML_text = re.sub("(:?^\s+|\s+$)", "", re.sub(r"\s+", " ", "".join(text)))
        return self

    def text_get_(self, node: XMLParser.Element):
        """具体实现获取数据"""
        rc = []
        nodeli = node.childNodes
        for n in nodeli:
            if n.nodeType == n.TEXT_NODE:
                console("data=" + n.data).log.end()
                if re.search(r"\S", n.data) is not None:
                    rc += [n.data]
                else:
                    rc += [re.sub(r"\s+", " ", n.data)]
            else:
                rc += self.text_get_(n)
        return rc

    def node_removeByTagAttrs(self, tagNames=["button", "div"], attrs={"card_id": ""}, **args):
        """剔除一些标签, 默认是为了我的插件服务的,临时删除所有影响获取文本的无关结点"""
        from .inputObj import Params
        p = Params(**args)
        p.tagNames, p.attrs = tagNames, attrs
        if not "checkValue" in p.__dict__: p.checkValue = False
        for tagName in tagNames:
            nodeli = self.domRoot.getElementsByTagName(tagName)
            for node in nodeli:
                parent = node.parentNode
                for k, v in attrs.items():
                    if p.checkValue:
                        if node.getAttribute(k) == v:
                            parent.removeChild(node)
                    else:
                        if node.hasAttribute(k):
                            parent.removeChild(node)
        return self

    # def obj_HTMLgen
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

    def HTML_back(self):
        text = self.domRoot.toxml()
        return re.sub(f"</?\s*{self.container}\s*>", "", text)

    def clear(self):
        self.__init__()
        return self

    def __setattr__(self, name, value):
        console(f"""{self.__class__.__name__}.{name}={value}""").log.end()
        self.__dict__[name] = value

    def __getattr__(self, name):
        console(f""" get {self.__class__.__name__}.{name}""").log.end()
        return self.__dict__[name]


def text_get(node: XMLParser.Element):
    rc = []
    nodeli = node.childNodes

    for n in nodeli:
        if n.nodeType == n.TEXT_NODE:
            console("data=" + n.data).log.end()
            if re.search(r"\S", n.data) is not None:
                rc += [n.data]
            else:
                rc += [re.sub(r"\s+", " ", n.data)]
        else:
            rc += text_get(n)
    return rc


if __name__ == "__main__":
    egHTML3 = """G<button card_id="1611035896519" dir="→" onclick="javascript:pycmd(&quot;cidd&quot;+&quot;1611035896519&quot;);" style="font-size:inherit;"> →A</button><button card_id="1611035896519" dir="→" onclick="javascript:pycmd(&quot;cidd&quot;+&quot;1611035896519&quot;);" style="font-size:inherit;"> →A</button><button card_id="1611035896519" dir="→" onclick="javascript:pycmd(&quot;cidd&quot;+&quot;1611035896519&quot;);" style="font-size:inherit;"> →A</button><button card_id="1611035896519" dir="→" onclick="javascript:pycmd(&quot;cidd&quot;+&quot;1611035896519&quot;);" style="font-size:inherit;"> →A</button>"""
    egHTML = """<div class="anci_header_content">
  <div class="article-title">
    <h2>辉瑞和阿斯利康缩减供货？部分国家恐将辉瑞告上法庭</h2>
  </div>
  <div class="article-desc clearfix">
    <div class="author-icon">
      <a href="https://author.baidu.com/home?from=bjh_article&amp;app_id=1549941228125394" target="_blank">
        <img src="https://pic.rmb.bdstatic.com/b9279adf974b78d27201a0b34970c2a9.jpeg"/>
      </a>
      <i class="author-vip author-vip-2"/>
    </div>
    <div class="author-txt">
      <div class="author-name">
        <a href="https://author.baidu.com/home?from=bjh_article&amp;app_id=1549941228125394" target="_blank">北晚新视觉网</a>
      </div>
      <div class="article-source article-source-bjh">
        <span class="date">发布时间：01-28</span>
        <span class="time">09:24</span>
        <span class="account-authentication">北京晚报官网官方帐号</span>
      </div>
    </div>
  </div>
</div>"""
    egHTML2 = """<?xml version="1.0"?>
<virtualRoot>
    <country name="Liechtenstein">
        <rank>1</rank>
        <year>2008</year>
        <gdppc>141100</gdppc>
        <neighbor name="Austria" direction="E"/>
        <neighbor name="Switzerland" direction="W"/>
    </country>
    <country name="Singapore">
        <rank>4</rank>
        <year>2011</year>
        <gdppc>59900</gdppc>
        <neighbor name="Malaysia" direction="N"/>
    </country>
    <country name="Panama">
        <rank>68</rank>
        <year>2011</year>
        <gdppc>13600</gdppc>
        <neighbor name="Costa Rica" direction="W"/>
        <neighbor name="Colombia" direction="E"/>
    </country>
</virtualRoot>
    """

    eg = HTML_converter()
    p = eg.feed(egHTML3)
    s = p.node_removeByTagAttrs().text_get.HTML_text

    print(s)
    # print(json.dumps(d, indent=4, ensure_ascii=False))
