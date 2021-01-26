"""
写了个HTML toObject toJSON 解析器
"""
import json
from abc import ABCMeta
from html.parser import HTMLParser
from typing import List, Tuple


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


def HTML_JSONGen(obj: List[HTML_element]):
    """利用深度优先遍历建立HTML的JSON对应"""
    HTML_dict = []
    stack_parent: List[HTML_element] = []  # element 对象
    stack_dict: List[HTML_element] = []  # element 字典
    stack: List[HTML_element] = []  # 原始对象
    stack += obj  # 入栈
    count = 0
    while len(stack) > 0:  # 当栈内有元素时
        count += 1
        print(str(count) + " stack " + stack.__str__())
        el: HTML_element = stack.pop(0)  # 弹出元素
        stack = el.kids + stack  # 将孩子纳入
        cur = {}  # 提取字典
        dict_attrs = {}
        for tp in el.attrs:
            dict_attrs[tp[0]] = tp[1]
        cur["tagName"], cur["attrs"], cur["data"], cur["kids"] = el.tagname, dict_attrs, el.data, []

        if len(stack_parent) > 0 and el in stack_parent[-1].kids:  # 设计这个逻辑之初, 并没有考虑到兄弟关系
            print(str(count) + " 走 len(stack_parent) > 0 and el in stack_parent[-1].kids:")
            # 当栈非空,而且是栈顶孩子时, 说明是树的枝, 所以字典要给kids 加东西. 同时stack_parent 往下走一步
            stack_dict[-1]["kids"].append(cur)  # 由于这里, 我们append的不一样, 导致了后面不能一样
        else:  # 当栈顶不是element的父亲时,退栈一个,一直到是为止
            print(str(count) + " 走 else # 当栈顶不是element的父亲时,退栈一个,一直到是为止")
            while len(stack_parent) > 0 and el not in stack_parent[-1].kids:
                stack_parent.pop()
                stack_dict.pop()
                # 此时如果还有元素,那就可以继续
            if len(stack_parent) > 0:
                stack_dict[-1]["kids"].append(cur)
                stack_parent.append(el)
            else:  # 没有元素了,那么我们自己入栈
                stack_dict.append(cur)
                stack_parent.append(el)
                HTML_dict.append(cur)

        print(str(count) + " cur" + cur.__str__())
        print(str(count) + " stack_parent " + stack_parent.__str__())
        print(str(count) + " stack_dict " + stack_dict.__str__())
        print(str(count) + " HTML_dict " + HTML_dict.__str__())
    return HTML_dict


class HTML_extractor(HTMLParser, metaclass=ABCMeta):
    """读取一些有用的信息"""

    def __init__(self):
        HTMLParser.__init__(self)
        self.root: List[HTML_element] = []
        self.parent: HTML_element = HTML_element()
        self.stack: List[str] = []
        self.curr: HTML_element = HTML_element()
        self.tagdict: Dict[str, List[HTML_element]] = {}
        self.count = 0

    def handle_starttag(self, tag, attrs):
        """覆盖,这是一个深度优先遍历,为了方便取值,还有一个根据标签类型分类的便利指针"""
        self.count += 1
        print(str(self.count) + " " + tag + " " + attrs.__str__())
        print(f"{self.count} stackDepth when start: {self.stack}")
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
        self.count += 1
        print(str(self.count) + " " + tag)
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
        print(str(self.count) + " data: " + data)
        if self.curr is None: print(str(self.count) + " None")
        self.curr.data.append(data)

    def handle_endtag(self, tag):
        """覆盖"""
        print(f"{self.count} stackDepth when End: {self.stack}")
        if len(self.stack) > 0 and self.stack[-1] == tag:
            self.stack.pop()
            self.curr = self.curr.parent

    def clear(self):
        """清空方便下次使用"""
        root = self.root
        tagdict = self.tagdict
        self.root = []
        self.tagdict = {}
        return [root, tagdict]


if __name__ == "__main__":
    eg = HTML_extractor()
    egHTML = """<div id="main-content" jstcache="0">
      <div class="icon icon-generic" jseval="updateIconClass(this.classList, iconClass)" alt="" jstcache="1"></div>
      <div id="main-message" jstcache="0">
        <h1 jstcache="0">
          <span jsselect="heading" jsvalues=".innerHTML:msg" jstcache="10">无法访问此网站</span>
          <a id="error-information-button" class="hidden" onclick="toggleErrorInformationPopup();" jstcache="0"></a>
        </h1>
        <p jsselect="summary" jsvalues=".innerHTML:msg" jstcache="2">网址为 <strong jscontent="failedUrl" jstcache="23">https://zh.wikipedia.org/zh-hans/泛型</strong> 的网页可能暂时无法连接，或者它已永久性地移动到了新网址。</p>
        <!--The suggestion list and error code are normally presented inline,
          in which case error-information-popup-* divs have no effect. When
          error-information-popup-container has the use-popup-container class, this
          information is provided in a popup instead.-->
        <div id="error-information-popup-container" jstcache="0">
          <div id="error-information-popup" jstcache="0">
            <div id="error-information-popup-box" jstcache="0">
              <div id="error-information-popup-content" jstcache="0">
                <div id="suggestions-list" style="display:none" jsdisplay="(suggestionsSummaryList &amp;&amp; suggestionsSummaryList.length)" jstcache="17">
                  <p jsvalues=".innerHTML:suggestionsSummaryListHeader" jstcache="19"></p>
                  <ul jsvalues=".className:suggestionsSummaryList.length == 1 ? 'single-suggestion' : ''" jstcache="20">
                    <li jsselect="suggestionsSummaryList" jsvalues=".innerHTML:summary" jstcache="22"></li>
                  </ul>
                </div>
                <div class="error-code" jscontent="errorCode" jstcache="18">ERR_INSUFFICIENT_RESOURCES</div>
                <p id="error-information-popup-close" jstcache="0">
                  <a class="link-button" jscontent="closeDescriptionPopup" onclick="toggleErrorInformationPopup();" jstcache="21">null</a>
                </p>
              </div>
            </div>
          </div>
        </div>
        <div id="diagnose-frame" class="hidden" jstcache="0"></div>
        <div id="download-links-wrapper" class="hidden" jstcache="0">
          <div id="download-link-wrapper" jstcache="0">
            <a id="download-link" class="link-button" onclick="downloadButtonClick()" jsselect="downloadButton" jscontent="msg" jsvalues=".disabledText:disabledMsg" jstcache="7" style="display: none;">
            </a>
          </div>
          <div id="download-link-clicked-wrapper" class="hidden" jstcache="0">
            <div id="download-link-clicked" class="link-button" jsselect="downloadButton" jscontent="disabledMsg" jstcache="12" style="display: none;">
            </div>
          </div>
        </div>
        <div id="save-page-for-later-button" class="hidden" jstcache="0">
          <a class="link-button" onclick="savePageLaterClick()" jsselect="savePageLater" jscontent="savePageMsg" jstcache="11" style="display: none;">
          </a>
        </div>
        <div id="cancel-save-page-button" class="hidden" onclick="cancelSavePageClick()" jsselect="savePageLater" jsvalues=".innerHTML:cancelMsg" jstcache="5" style="display: none;">
        </div>
        <div id="offline-content-list" class="list-hidden" hidden="" jstcache="0">
          <div id="offline-content-list-visibility-card" onclick="toggleOfflineContentListVisibility(true)" jstcache="0">
            <div id="offline-content-list-title" jsselect="offlineContentList" jscontent="title" jstcache="13" style="display: none;">
            </div>
            <div jstcache="0">
              <div id="offline-content-list-show-text" jsselect="offlineContentList" jscontent="showText" jstcache="15" style="display: none;">
              </div>
              <div id="offline-content-list-hide-text" jsselect="offlineContentList" jscontent="hideText" jstcache="16" style="display: none;">
              </div>
            </div>
          </div>
          <div id="offline-content-suggestions" jstcache="0"></div>
          <div id="offline-content-list-action" jstcache="0">
            <a class="link-button" onclick="launchDownloadsPage()" jsselect="offlineContentList" jscontent="actionText" jstcache="14" style="display: none;">
            </a>
          </div>
        </div>
      </div>
    </div>"""
    eg.feed(egHTML)
    d = HTML_JSONGen(eg.root)
    print(json.dumps(d, indent=4, ensure_ascii=False))

    print(json.dumps(eg.tagdict, indent=4, ensure_ascii=False))
