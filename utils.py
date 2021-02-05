"""这个是用来放一些工具的
debug函数
一些常量
"""
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


def wrapper_browser_refresh(func):
    """用来刷新browser"""

    @functools.wraps(func)
    def refresh(*args, **kwargs):
        browser = dialogs.open("Browser", mw)
        browser.maybeRefreshSidebar()
        browser.model.layoutChanged.emit()
        browser.editor.setNote(None)
        result = func(*args, **kwargs)
        browser.maybeRefreshSidebar()
        browser.model.layoutChanged.emit()
        browser.editor.setNote(None)
        browser.model.reset()  # 关键作用
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


class Empty:
    """空对象"""


class Pair:
    """卡片ID和卡片描述的键值对的对象
    通用名字:card_id,desc,dir,
    """

    def __init__(self, **pair):
        self.card_id = pair["card_id"]
        if "desc" in pair:
            self.desc = pair["desc"]
        else:
            self.desc = ""
        if "dir" in pair:
            self.dir = pair["dir"]
        else:
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

    def __contains__(self, name):
        if self.__dict__.__contains__(name) and self.__dict__[name] is not None:
            return True
        return False


class console:
    """debug用的"""

    def __init__(self, text: str = "", func: callable = tooltip, terminal=None, logSwitcher=True, **need):
        self.logSwitcher = logSwitcher
        self.text = text
        self.say = func
        self.prefix = terminal if terminal is not None else consolerName + " > "
        self.need = need
        self.timestamp = datetime.datetime.now().strftime("%H:%M:%S") + " > "
        self.who = f"""line{sys._getframe(1).f_lineno.__str__()}:{sys._getframe(1).f_code.co_name} >"""
        self.logfile = os.path.join(THIS_FOLDER, logFileName)
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
        f = open(self.logfile, mode, encoding="utf-8")
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



ISDEV = False
ISDEBUG = False  # 别轻易开启,很卡的
helpSite = "https://gitee.com/huangjipan/hjp-bilink"
inputFileName = "input.json"
configFileName = "user_files/config.json" if not ISDEV else "user_files/configdev.json"
configSchemaFileName = "user_files/config.schema.json"
configTemplateFileName = "config_template.json"
helpFileName = "README.md"
relyLinkDir = "1423933177"
advancedBrowserDir = "564851917"
relyLinkConfigFileName = "config.json"
logFileName = "log.txt"
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
USER_FOLDER = os.path.join(THIS_FOLDER, "user_files")
PREV_FOLDER = os.path.dirname(THIS_FOLDER)
RELY_FOLDER = os.path.join(PREV_FOLDER, relyLinkDir)
inputSchema = {"IdDescPairs": [], "addTag": ""}
consolerName = "hjp-bilink|"
algPathDict = {
    "desc": ["默认连接", "完全图连接", "组到组连接", "按结点取消连接", "按路径取消连接"],
    "mode": [999, 0, 1, 2, 3]
}

config_template = json.load(open(os.path.join(THIS_FOLDER, configTemplateFileName), "r", encoding="utf-8"))
VERSION = """
<p>版本:{version}</p>
<p>新增功能:</p>
<p style="color:red;">新增菜单:重置config文件</p>
<p style="color:red;">锚点改为下拉弹出式,卡片渲染后注入按钮</p>
<p style="color:red;">可升级旧版(0.4.x和0.6.x)的锚点,卡片需要插入input操作</p>
<p>锚点改为按钮格式,</p>
<p>input对话框,可拖拽,可双击打开卡片预览,可右键执行链接,删除,选中部分卡片链接等</p>
<p>快捷键:在browser浏览界面下,可以使用快捷键执行链接,反链接,清空input,打开input,插入选中卡片</p>
<p>可以在复习窗口,预览窗口点右键执行绝大部分功能</p>
<a href="https://ankiweb.net/shared/info/1420819673">点我看详情</a>
""".format(version=config_template["VERSION"])

try:
    cardPrevDialog = __import__("1423933177").card_window.external_card_dialog
except:
    cardPrevDialog = None
    showInfo(say("请安装插件1423933177,否则将无法点击链接预览卡片"))

if not os.path.exists(os.path.join(PREV_FOLDER, advancedBrowserDir)):
    showInfo(say("请安装插件564851917,否则将无法折叠标签,我们每次链接都会产生标签"))


class BaseInfo(object, ):
    """基础信息"""

    def __init__(self, inputFileDir: str = os.path.join(THIS_FOLDER, inputFileName),
                 configFileDir: str = os.path.join(THIS_FOLDER, configFileName),
                 helpDir: str = helpSite,
                 relyDir: str = RELY_FOLDER,
                 initDict: dict = inputSchema,
                 model: AnkiQt = mw, ):
        self.valueStack = []
        self.model = model
        self.helpSite = helpDir
        self.initDict = initDict
        self.relyDir = relyDir
        self.inputDir = inputFileDir
        self.configDir = configFileDir
        self.config = json.load(open(configFileDir, "r", encoding="UTF-8", ))
        self.configObj = Params(**self.config)

    def anchorCSS_load(self):
        """首先读取用户区域的这个文件,读不到再找本地的文件"""
        path = os.path.join(USER_FOLDER, self.configObj.anchorCSSFileName)
        if not os.path.exists(path):
            path = os.path.join(THIS_FOLDER, "anchorCSS.txt")
        s = open(path, "r", encoding="utf-8")
        t = s.read()
        s.close()
        return t
