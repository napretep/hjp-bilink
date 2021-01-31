"""这个是用来放一些工具的
debug函数
一些常量
"""
import datetime, types, functools, json
from aqt.utils import *

VERSION = "0.5"
helpSite = "https://gitee.com/huangjipan/hjp-bilink"
inputFileName = "input.json"
configFileName = "config.json"
helpFileName = "README.md"
ISDEBUG = True
relyLinkDir = "1423933177"
relyLinkConfigFileName = "config.json"
logFileName = "log.txt"
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
PREV_FOLDER = os.path.dirname(THIS_FOLDER)
RELY_FOLDER = os.path.join(PREV_FOLDER, relyLinkDir)
inputSchema = {"IdDescPairs": [], "addTag": ""}
consolerName = "hjp-bilink|"
algPathDict = {
    "desc": ["默认连接", "完全图连接", "组到组连接", "按结点取消连接", "按路径取消连接"],
    "mode": [999, 0, 1, 2, 3]
}


def debugWatcher(func):
    @functools.wraps(func)
    def debugWatcher_sub(*args, **kwargs):
        if ISDEBUG:
            lineNumber = "line " + sys._getframe(1).f_lineno.__str__() + ":"
            path = sys._getframe(1).f_code.co_filename
            method = sys._getframe(1).f_code.co_name.__str__()
            local = sys._getframe(1).f_code.co_varnames.__str__()
            console(path + "\n" + lineNumber + "." + method + "--->start\nlocal:" + local).log.end()
            result = func(*args, **kwargs)
            local = sys._getframe(1).f_locals.__str__()
            console(path + "\n" + lineNumber + method + "--->end\nlocal:" + local).log.end()
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
    """卡片ID和卡片描述的键值对的对象"""

    def __init__(self, **pair):
        self.card_id: str = pair["card_id"]
        self.desc: str = pair["desc"]

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
            return None


class console:
    """debug用的"""

    def __init__(self, text: str = "", func: callable = tooltip, terminal=consolerName, logSwitcher=True, **need):
        self.logSwitcher = logSwitcher
        self.text = text
        self.say = func
        self.prefix = terminal + " > "
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

    def talk(self, chain=True):
        """talk 就是 说出来"""
        self.say(self.text)
        if chain:
            return self
        else:
            return

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