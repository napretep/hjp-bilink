"""这个是用来放一些工具的
debug函数
一些常量
"""
from typing import List, Tuple, Dict
import datetime, types, functools, json
from aqt.utils import *
from aqt import mw, AnkiQt, dialogs
from .language import rosetta as say
import copy
import json
import time
from aqt.browser import Browser
from aqt.editor import EditorWebView, Editor
from aqt.reviewer import Reviewer
from aqt.webview import AnkiWebView

ISDEV = False
ISDEBUG = True  # 别轻易开启,很卡的
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
baseInfoFileName = "baseInfo.json"
baseInfoDir = os.path.join(THIS_FOLDER, baseInfoFileName)


def wrapper_webview_refresh(func):
    """刷新ankiWebView"""

    def refresh(*args, **kwargs):
        self = args[0]
        parent = self.parent
        result = func(*args, **kwargs)
        if parent.title == "previewer":
            parent.parent().render_card()
        if parent.title == "main webview":
            mw.reviewer.show()
        return result

    return refresh


def wrapper_browser_refresh(func):
    """用来刷新browser"""

    @functools.wraps(func)
    def refresh(*args, **kwargs):
        if dialogs._dialogs["Browser"][1] is not None:
            browser = dialogs._dialogs["Browser"][1]
            browser.maybeRefreshSidebar()
            browser.model.layoutChanged.emit()
            browser.editor.setNote(None)
            result = func(*args, **kwargs)
            browser.maybeRefreshSidebar()
            browser.model.layoutChanged.emit()
            browser.editor.setNote(None)
            browser.model.reset()  # 关键作用
        else:
            result = func(*args, **kwargs)
        return result

    return refresh


def debugWatcher(func):
    """debug专用"""

    @functools.wraps(func)
    def debugWatcher_sub(*args, **kwargs):
        if ISDEBUG:
            lineNumber = " line " + sys._getframe(1).f_lineno.__str__() + ":"
            path = sys._getframe(1).f_code.co_filename
            method = sys._getframe(1).f_code.co_name.__str__()
            # local = sys._getframe(1).f_code.co_varnames.__str__()
            console(path + "\n" + method + "--->start at" + lineNumber).log.end()
            result = func(*args, **kwargs)
            local = sys._getframe(1).f_locals.__str__()
            console(
                path + "\n" + method + "--->end at" + lineNumber + "\n" + path + "\nlocal:" + local + "\n").log.end()
        else:
            result = func(*args, **kwargs)
        return result

    return debugWatcher_sub


def logfunc(func):
    """Calculate the execution time of func."""

    @functools.wraps(func)
    def wrap_log(*args, **kwargs):
        """包装函数"""
        if ISDEBUG:
            console(f"""{func.__name__} 开始""").noNewline.log.end()
            result = func(*args, **kwargs)
            localss = locals()
            console(
                f"""{func.__name__} 中间:\nargs>{localss["args"]}\nkwargs>{localss["kwargs"]}\nresult>{localss["result"]}""").noNewline.log.end()
            console(f"""{func.__name__} 结束""").noNewline.log.end()
        else:
            result = func(*args, **kwargs)
        return result

    return wrap_log



class MetaClass_loger(type):
    """"监控元类"""

    def __new__(mcs, name, bases, attr_dict):
        for k, v in attr_dict.items():
            # If the attribute is function type, use the wrapper function instead
            if isinstance(v, types.FunctionType):
                attr_dict[k] = debugWatcher(v)
        return type.__new__(mcs, name, bases, attr_dict)


class CustomSignals(QObject):
    instance = None
    linkedEvent = pyqtSignal()

    @classmethod
    def start(cls):
        if cls.instance is None:
            cls.instance = cls()
        return cls.instance


class Empty:
    """空对象"""


class Pair:
    """卡片ID和卡片描述的键值对的对象
    通用名字:card_id,desc,dir,
    """

    def __init__(self, **pair):
        self.__dict__ = pair
        if "dir" not in pair:
            self.dir = "→"


    @property
    def int_card_id(self):
        """用方法伪装属性,好处是不必担心加入input出问题"""
        return int(self.card_id)

    def __str__(self):
        return f"""<{self.__class__.__name__}:{self.__dict__.__str__()}>"""

    def __add__(self, other):
        return other + self.__str__()

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, key):
        return self.__dict__[key]

    def __contains__(self, name):
        if self.__dict__.__contains__(name) and self.__dict__[name] is not None:
            return True
        return False

class Params:
    """参数对象"""

    def __init__(self, **args):
        self.__dict__ = args
        if "features" not in args: self.features = []

        if "actionTypes" not in args: self.actionTypes = []

    def __str__(self):
        return f"""<{self.__class__.__name__}:{self.__dict__.__str__()}"""

    def __add__(self, other):
        return other + self.__dict__.__str__()

    def __repr__(self):
        return self.__dict__.__str__()

    def __getattr__(self, name):
        if self.__dict__.__contains__(name):
            return self.__dict__[name]
        else:
            raise AttributeError(name + "这个属性不存在")

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __contains__(self, name):
        if self.__dict__.__contains__(name) and self.__dict__[name] is not None:
            return True
        return False


class console:
    """debug用的"""

    def __init__(self, text: str = "", func: callable = tooltip, terminal=None, logSwitcher=ISDEBUG, **need):
        self.baseinfo = BaseInfo()
        self.logSwitcher = logSwitcher
        self.text = text
        self.say = func
        self.prefix = terminal if terminal is not None else self.baseinfo.consolerName + " > "
        self.need = need
        self.timestamp = datetime.datetime.now().strftime("%H:%M:%S") + " > "
        self.who = f"""line{sys._getframe(1).f_lineno.__str__()}:{sys._getframe(1).f_code.co_name} >"""
        self.logDir = self.baseinfo.logDir
        self.newline_ = "\n"
        self.breakline_ = "\n"

    @property
    def log(self, chain=True):
        """debug用"""
        if not ISDEBUG:
            return self
        obj = self.need["obj"].__class__.__name__ + "." if "obj" in self.need else ""
        text = self.timestamp + self.prefix + obj + self.who + self.newline_ + self.text + self.breakline_
        self.logFileWrite(text)
        if chain:
            return self
        else:
            return

    def logFileWrite(self, text, mode="a"):
        """写入文件"""
        f = open(self.logDir, mode, encoding="utf-8")
        f.write(text)
        f.close()

    def _(self, text):
        """当这个类是一个对象的属性时,我们可以通过这个方法来发起通信"""
        self.text = text
        return self

    @property
    def talk(self):
        """talk 就是 说出来"""
        self.say(self.prefix + self.text)
        return self

    @property
    def showInfo(self, chain=True):
        """和外来的名字一样就是为了链式访问简单一点"""
        self.say = showInfo
        if chain:
            return self
        else:
            return

    @property
    def noNewline(self):
        """改写是否换行"""
        self.newline_ = ""
        return self

    @property
    def logFileClear(self):
        """清空log文件"""
        self.logFileWrite("", mode="w")
        return self

    def end(self):
        return self


configFileName = "user_files/config.json" if not ISDEV else "user_files/configdev.json"
configSchemaFileName = "config.schema.json"
configHTMLFileName = "config.html"
configTemplateFileName = "config.template.json"
helpFileName = "README.md"
versionFileName = "version.html"
relyLinkDir = "1423933177"
advancedBrowserDir = "564851917"
relyLinkConfigFileName = "config.json"
logFileName = "log.txt"
USER_FOLDER = os.path.join(THIS_FOLDER, "user_files")
PREV_FOLDER = os.path.dirname(THIS_FOLDER)
RELY_FOLDER = os.path.join(PREV_FOLDER, relyLinkDir)
inputSchema = {"IdDescPairs": [], "addTag": ""}
consolerName = "hjp-bilink|"
algPathDict = {
    "desc": ["默认连接", "完全图连接", "组到组连接", "按结点取消连接", "按路径取消连接"],
    "mode": [999, 0, 1, 2, 3]
}


class BaseInfo(object):
    """解决大量赋值消耗内存的情况"""

    def __init__(self):
        self.baseinfo = Params(**json.load(open(baseInfoDir, "r", encoding="utf-8")))

    def path_get(self, name, dirName=THIS_FOLDER):
        """返回文件路径"""
        return os.path.join(THIS_FOLDER, self.baseinfo[name + "FileName"])

    def file_open_r(self, path, as_="JSON"):
        """返回dict或者list"""
        if as_ == "JSON":
            return json.load(open(path, "r", encoding="utf-8"))
        elif as_ == "_obj":
            return Params(**self.file_open_r(path))
        elif as_ == "File":
            return open(path, "r", encoding="utf-8").read()

    def __getattr__(self, name):
        """一次赋值终生受益"""
        if name not in self.__dict__:
            if name[-3:] == "Dir":
                self.__dict__[name] = self.path_get(name[:-3])
            if name[-4:] in ["JSON", "File", "_obj"]:
                self.__dict__[name] = self.file_open_r(self.path_get(name[:-4]), as_=name[-4:])
            if name[-4:] in ["Site", "Name"]:
                self.__dict__[name] = self.__dict__["baseinfo"][name]
        elif name in self.__dict__["baseinfo"]:
            self.__dict__[name] = self.__dict__["baseinfo"][name]
        else:
            raise TypeError("找不到数据:" + name)
        return self.__dict__[name]


"""开始的一段检测"""
try:
    cardPrevDialog = __import__("1423933177").card_window.external_card_dialog
except:
    cardPrevDialog = None
    showInfo(say("请安装插件1423933177,否则将无法点击链接预览卡片"))

if not os.path.exists(os.path.join(PREV_FOLDER, advancedBrowserDir)):
    showInfo(say("请安装插件564851917,否则将无法折叠标签,我们每次链接都会产生标签"))
