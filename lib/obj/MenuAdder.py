"""
专门用来加按钮的文件
prefix 必须由consolerName规定
"""

from .mainfunctions import *
from .utils import *

addonName = BaseInfo().dialogName
mw.__dict__[addonName] = {}
mw.__dict__[addonName]["card_window"] = {}


def func_actionMenuConnector(*args, **kwargs):
    """执行动作链接的一个辅助函数"""
    param = Params(**kwargs)
    menu, actionName, action = param.menu, param.actionName, param.action
    menu.addAction(actionName).triggered.connect(lambda: action(**kwargs))


def func_menuAddAlterDeck(*args, **kwargs):
    """添加卡组操作:移动,创建"""


def func_menuAddAlterTag(*args, **kwargs):
    """添加标签操作:添加,移除,创建"""


def func_resetConfig():
    """重置config窗口"""
    base = BaseInfo()
    json.dump(base.configTemplateJSON, open(base.configDir, "w", encoding="utf-8"), indent=4,
              ensure_ascii=False)
    tooltip(say("参数表重置成功"))


# @debugWatcher
def func_menuAddBrowserInsert(*args, **kwargs):
    """browser插入类函数集合"""
    param = Params(**kwargs)
    prefix = "" if ("prefix" not in param.features) or "selected" in param.features else BaseInfo().consolerName
    menuNameLi = list(map(lambda x: prefix + say(x), ["清除后选中卡片插入", "将选中卡片插入", "将选中卡片编组插入"]))
    featureli = [["clear"], [""], ["group"]]
    if "selected" in param.features:
        for feat in featureli: feat.append("selected")
    if "prefix" in param.features:
        if "selected" in param.features:
            linkmenu = param.menu.addMenu(BaseInfo().consolerName + say("选中插入"))
        else:
            linkmenu = param.menu
    else:
        linkmenu = param.menu.addMenu(say("插入"))
    list(map(lambda i:
             func_actionMenuConnector(menu=linkmenu, actionName=menuNameLi[i], action=func_browserInsert,
                                      parent=param.parent, features=featureli[i])
             , range(len(featureli))))


def func_menuAddSingleInsert(*args, **kwargs):
    """用来添加常规插入按钮组"""
    param = Params(**kwargs)
    actionNameLi = list(map(lambda x: say(x), ["先清除再插入", "直接插入", "插入上一个组", "选中文字更新标签"]))
    featureli = ["clear", "", "last", "tag"]
    prefix = "" if "prefix" not in param.features else BaseInfo().consolerName
    papamenu = param.menu.addMenu(prefix + say("插入"))
    list(map(lambda i: func_actionMenuConnector(menu=papamenu, actionName=actionNameLi[i], action=func_singleInsert,
                                                pair=param.pair, features=[featureli[i]]), range(len(featureli))))


def func_menuAddLink(*args, **kwargs):
    """用来给链接类型的函数加按钮"""
    param = Params(**kwargs)
    menuNameLi = list(map(lambda x: say(x), ["默认链接", "完全图链接", "组到组链接", "按结点取消链接", "按路径取消链接"]))
    prefix = "" if "prefix" not in param.features else BaseInfo().consolerName
    linkname = "链接"
    if "selected" in param.features:
        linkname = "选中链接"
    linkmenu = param.menu.addMenu(prefix + say(linkname))
    modeLi = [999, 0, 1, 2, 3]
    list(map(
        lambda x, y: linkmenu.addAction(x).triggered.connect(
            lambda: LinkStarter(mode=y, parent=param.parent, input=Input(), features=param.features)),
        menuNameLi, modeLi))


def func_menuAddClearOpen(*args, **kwargs):
    """用来给清除和打开input功能加按钮"""
    param = Params(**kwargs)
    prefix = "" if "prefix" not in param.features else BaseInfo().consolerName
    menuli = ["打开input", "清空input"]
    funcli = [func_openInput, func_clearInput]
    list(map(lambda x, y: param.menu.addAction(f"{prefix}{say(x)}").triggered.connect(y), menuli, funcli))


def func_menuAddBaseMenu(*args, **kwargs):
    """基础的如,help,config,version"""
    param = Params(**kwargs)
    menuli = ["调整config", "查看版本和新特性", "打开插件页面", "升级旧版(小于等于0.6的版本)锚点", "联系作者", "支持作者", "重置config"]
    funcli = [func_config, func_version, func_help, func_anchorUpdate, func_contactMe, func_supportMe, func_resetConfig]
    menu = param.menu.addMenu(say("其他"))
    list(map(lambda x, y: menu.addAction(f"{say(x)}").triggered.connect(y), menuli, funcli))


def func_menuAddAnchorMenu(*args, **kwargs):
    """加打开anchor的按钮,传来的参数有:pair,features,parent,menu"""
    param = Params(**kwargs)
    cfg = BaseInfo()
    prefix = cfg.consolerName if "prefix" in param.features else ""

    func_actionMenuConnector(actionName=f"{prefix}{say('打开anchor')}", action=func_openAnchor, **kwargs)


# @debugWatcher
def func_menuAddHelper(*args, **kwargs):
    """提供大部分类似的按钮添加操作帮助"""
    param = Params(**kwargs)
    for action in param.actionTypes:
        func_menuAdderLi[action](**kwargs)


func_menuAdderLi = {
    "link": func_menuAddLink,
    "browserinsert": func_menuAddBrowserInsert,
    "clear_open": func_menuAddClearOpen,
    "basicMenu": func_menuAddBaseMenu,
    "insert": func_menuAddSingleInsert,
    "anchor": func_menuAddAnchorMenu,
    "alter_deck": func_menuAddAlterDeck,
    "alter_tag": func_menuAddAlterTag
}
