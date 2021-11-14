from dataclasses import dataclass
from typing import Union, List

from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import QMenu, QAction
from aqt import mw
from aqt.browser import Browser
from aqt.utils import showInfo, tooltip
from aqt.webview import AnkiWebView

from ..common_tools import G
from ..common_tools.language import rosetta as say
from .. import common_tools


class T:
    # 标记不同的来源
    browser_context = 0
    browser = 1
    mainwin = 2
    webview = 3
    anchor_selected_context = 4
    linkpool_selected_context = 5
    linkpool_context = 6
    grapher_node_context = 7
    browser_searchbar_context = 8


def get_pair_li_from_view(view) -> "list[common_tools.objs.LinkDataPair]":
    """从view提取的只能是card_id,我们要转化成 pair_li"""
    cid = ""
    cardLi = []
    if isinstance(view, Browser):
        cardLi: List[str] = list(map(lambda x: str(x), view.selectedCards()))
    elif isinstance(view, AnkiWebView):
        if view.title == "main webview" and mw.state == "review":
            cid = mw.reviewer.card.id
        elif view.title == "previewer" and view.parent() is not None and view.parent().card() is not None:
            cid = view.parent().card().id
        if cid != "":
            cardLi = [str(cid)]
    pair_li = [common_tools.objs.LinkDataPair(card_id=card_id, desc=common_tools.funcs.desc_extract(card_id)
                                              ) for card_id in cardLi]
    return pair_li


def get_browser_menu(browser: "Browser"):
    if G.src.addon_name in browser.__dict__:
        M: "QMenu" = browser.__dict__[G.src.addon_name]
    else:
        M: "QMenu" = QMenu(G.src.addon_name)
        browser.__dict__[G.src.addon_name] = M
        browser.menuBar().addMenu(M)
    return M


def get_mainWin_menu():
    M: "QMenu" = QMenu(G.src.addon_name+"_v"+G.src.ADDON_VERSION)
    mw.__dict__[G.src.dialog_name] = M
    mw.menuBar().addMenu(M)
    # showInfo(M.__str__())
    return M


def func_actionMenuConnector(menu, action_name, action, **kwargs):
    """执行动作链接的一个辅助函数"""
    menu.addAction(action_name).triggered.connect(lambda: action(**kwargs))


def placeholder(*args, **kwargs):
    return


def make__open_anchor(atype, *args, **kwargs):
    if atype == T.webview:
        view: "AnkiWebView" = args[0]
        M: "QMenu" = args[1]
        pair_li = get_pair_li_from_view(view)
        act = M.addAction(f"""{kwargs["prefix"]}{say("打开anchor")}""")
        act.triggered.connect(lambda: common_tools.funcs.Dialogs.open_anchor(pair_li[0].card_id))
    pass


def make__copy_card_as(atype, *args, **kwargs):
    if atype in {T.browser_context, T.webview, T.anchor_selected_context,
                 T.linkpool_selected_context, T.linkpool_context}:
        view: "Union[AnkiWebView,Browser]" = args[0]
        M: "QMenu" = args[1]
        AnkiLinks=common_tools.funcs.AnkiLinks
        pair_li: "list[common_tools.objs.LinkDataPair]" = kwargs[
            "pair_li"] if "pair_li" in kwargs else get_pair_li_from_view(view)
        act_li =[["文内链接",lambda: common_tools.funcs.copy_intext_links(pair_li)],
                 ["html链接", lambda:AnkiLinks.copy_card_as(AnkiLinks.Type.html, pair_li)],
                 ["markdown链接", lambda:AnkiLinks.copy_card_as(AnkiLinks.Type.markdown, pair_li)],
                 ["orgmode链接", lambda:AnkiLinks.copy_card_as(AnkiLinks.Type.orgmode, pair_li)]
                 ]
        M2 = M.addMenu(f"""{kwargs["prefix"]}{say("复制为")}""")
        list(map(lambda x:M2.addAction(x[0]).triggered.connect(x[1]),act_li))
    pass


def make__copy_search_as(atype, *args, **kwargs):

    if atype in {T.browser}:
        view: "Browser" = args[0]
        M = get_browser_menu(view)
        M2=M.addMenu("复制当前搜索栏为")
        AnkiLinks = common_tools.funcs.AnkiLinks
        act_li=[["html链接",lambda:AnkiLinks.copy_search_as(AnkiLinks.Type.html,view)],
                ["markdown链接",lambda:AnkiLinks.copy_search_as(AnkiLinks.Type.markdown,view)],
                ["orgmode链接",lambda:AnkiLinks.copy_search_as(AnkiLinks.Type.orgmode,view)]]
        list(map(lambda x:M2.addAction(x[0]).triggered.connect(x[1]),act_li))


def make__outtext_link(atype, *args, **kwargs):
    if atype in {T.browser, T.webview, T.browser_context, T.anchor_selected_context,
                 T.linkpool_selected_context, T.linkpool_context}:
        view = args[0]
        pair_li: "list[common_tools.objs.LinkDataPair]" = kwargs[
            "pair_li"] if "pair_li" in kwargs else get_pair_li_from_view(view)

        prefix = kwargs["prefix"]
        if atype in {T.browser}:
            M = get_browser_menu(view)
            prefix = ""
        else:
            M: "QMenu" = args[1]
            if atype not in {T.browser_context, T.linkpool_context, T.webview}:
                prefix = ""
        out_text_link = M.addMenu(prefix + say("文外链接操作"))
        # out_text_link_act=[]
        open_pool: "QAction" = out_text_link.addAction(say("打开链接池"))
        open_pool.triggered.connect(common_tools.funcs.Dialogs.open_linkpool)
        clean_pool: "QAction" = out_text_link.addAction(say("清空链接池"))
        clean_pool.triggered.connect(common_tools.funcs.LinkPoolOperation.clear)
        L = common_tools.funcs.LinkPoolOperation

        if atype == T.browser_context:
            d = {"选中直接操作": [("完全图绑定", lambda: L.link(mode=L.M.complete_map, pair_li=pair_li)),
                            ("组到组绑定", lambda: L.link(mode=L.M.group_by_group, pair_li=pair_li)),
                            ("按结点解绑", lambda: L.unlink(mode=L.M.unlink_by_node, pair_li=pair_li)),
                            ("按路径解绑", lambda: L.unlink(mode=L.M.unlink_by_path, pair_li=pair_li))
                            ], }
            for menu, actli in d.items():
                m = out_text_link.addMenu(say(menu))
                for a in actli:
                    m.addAction(say(a[0])).triggered.connect(a[1])

        d = {

            "卡片插入池": [("清空后插入", lambda: L.insert(pair_li, mode=L.M.before_clean)),
                      ("直接插入", lambda: L.insert(pair_li, mode=L.M.directly)),
                      ("编组插入", lambda: L.insert(pair_li, mode=L.M.by_group))],
            "池中卡片操作": [("完全图绑定", lambda: L.link(mode=L.M.complete_map)),
                       ("组到组绑定", lambda: L.link(mode=L.M.group_by_group)),
                       ("按结点解绑", lambda: L.unlink(mode=L.M.unlink_by_node)),
                       ("按路径解绑", lambda: L.unlink(mode=L.M.unlink_by_path))]
        }
        for menu, actli in d.items():
            m = out_text_link.addMenu(say(menu))
            for a in actli:
                m.addAction(say(a[0])).triggered.connect(a[1])
    pass


def make__change_deck(atype, *args, **kwargs):
    if atype in {T.webview, T.browser_context,T.grapher_node_context}:
        prefix = kwargs["prefix"]
        if atype in {T.webview, T.browser_context}:
            view = args[0]
            pair_li = get_pair_li_from_view(view)
        elif atype in {T.grapher_node_context}:
            pair_li = args[0]
            view = args[2]
        menu: "QMenu" = args[1]
        menu.addAction(prefix + say("改变牌组")).triggered.connect(
            lambda: common_tools.funcs.Dialogs.open_deck_chooser(pair_li,view))

    pass


def make__tag_operation(atype, *args, **kwargs):
    if atype in {T.webview, T.browser_context,T.grapher_node_context}:
        prefix = kwargs["prefix"]
        if atype in {T.webview, T.browser_context}:
            view = args[0]
            pair_li = get_pair_li_from_view(view)
        elif atype in {T.grapher_node_context}:
            pair_li = args[0]
        menu: "QMenu" = args[1]
        m = menu.addAction(prefix + say("操作标签")).triggered.connect(
            lambda: common_tools.funcs.Dialogs.open_tag_chooser(pair_li))

    pass


def make__other(atype, *args, **kwargs):
    if atype in {T.browser}:
        M: "QMenu" = get_browser_menu(args[0])
        other = M.addMenu(say("其他"))
        act_li = [
            ("配置表", lambda: showInfo("还未完成/not finished yet")),
            ("联系作者", common_tools.funcs.Dialogs.open_contact),
            ("支持作者", common_tools.funcs.Dialogs.open_support),
            ("打开链接数据保存目录", common_tools.funcs.Dialogs.open_link_storage_folder),
            ("打开代码仓库", common_tools.funcs.Dialogs.open_repository),
            ("重设配置表", lambda: showInfo("还未完成/not finished yet")),
            ("查看更新与文档", common_tools.funcs.Dialogs.open_version)
        ]
        for act, func in act_li:
            other.addAction(say(act)).triggered.connect(func)
    pass


def make__open_clipper(atype, *args, **kwargs):
    if atype in {T.browser, T.browser_context, T.webview, T.mainwin}:
        from ..common_tools import funcs
        prefix = kwargs["prefix"]
        name = "打开clipper"
        pairs_li = []
        if len(args) > 0:
            view = args[0]
            pairs_li = get_pair_li_from_view(view)
            if atype == T.browser:
                M = get_browser_menu(view)
                prefix = ""
            elif atype == T.browser_context:
                M: "QMenu" = args[1]
                name = "在clipper中打开卡片"
            elif atype == T.webview:
                M: "QMenu" = args[1]
                name = "在clipper中打开卡片"
            elif atype in (T.mainwin):
                M = get_mainWin_menu()
                prefix = ""
        else:
            view = mw
            M = get_mainWin_menu()
            prefix = ""
        # def open_clipper()
        # M.addAction(prefix + say(name)).triggered.connect(lambda: funcs.BrowserOperation.search(f"""tag:hjp-bilink::timestamp""").activateWindow())

        M.addAction(prefix + say(name)).triggered.connect(lambda: funcs.Dialogs.open_clipper(pairs_li))

def make__open_grapher(atype, *args, **kwargs):
    if atype in {T.browser_context, T.webview}:
        from . import funcs
        prefix = kwargs["prefix"]
        if len(args) > 0:
            view = args[0]
            pairs_li = get_pair_li_from_view(view)
            M: "QMenu" = args[1]
            name = "在grapher中打开卡片"
            M.addAction(prefix+name).triggered.connect(lambda:funcs.Dialogs.open_grapher(pairs_li))


make_list = [globals()[name] for name in globals() if name.startswith("make__")]


def maker(atype):
    def do(*args, **kwargs):
        if "needPrefix" not in kwargs:
            kwargs["needPrefix"] = True
        kwargs["prefix"] = G.src.addon_name + "_" if kwargs["needPrefix"] else ""

        if atype == T.webview:
            focus_on_mw = args[0].title == "main webview"  and mw.state == "review" and mw.isActiveWindow()
            focus_on_prev = args[0].title == "previewer"
            if not focus_on_mw and not focus_on_prev :
                # showInfo("return")
                return
        for m in make_list:
            m(atype, *args, **kwargs)

    return do
