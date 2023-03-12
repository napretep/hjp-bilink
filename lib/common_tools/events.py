# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'events.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2021/7/30 9:15'
"""
import shutil
import time
from .compatible_import import *
from anki.cards import Card
from anki.notes import Note
from . import objs
from . import funcs

say = funcs.G.say


def on_card_will_show(htmltext, card, kind):
    htmltext = funcs.HTML.injectToWeb(htmltext, card, kind)

    return htmltext


def on_reviewer_did_show_question(card: "Card"):
    # showInfo("show question!")
    starttime = funcs.G.cardChangedTime = time.time()
    # print(f"show question at time={starttime}")
    # if funcs.Config.get().time_up_buzzer.value > 0:
    #     funcs.ReviewerOperation.time_up_buzzer(card, starttime)


def on_profile_will_close_handle():
    if funcs.LinkPoolOperation.exists():
        funcs.LinkPoolOperation.clear()
    if funcs.Utils.LOG.exists():
        funcs.Utils.LOG.file_clear()
    cfg, now = funcs.Config.get(), datetime.datetime.now().timestamp()
    if funcs.GlobalLinkDataOperation.need_backup(cfg, now):
        funcs.GlobalLinkDataOperation.backup(cfg, now)
    funcs.Config.save(funcs.G.CONFIG)


def on_add_cards_did_init_handle(addcards: "AddCards"):
    def newcard_grahper_open_close_switch(state):
        funcs.G.mw_addcard_to_grapher_on = state == "on"

    button = QToolButton()
    button.setText("off")  # on,off
    button.setIcon(QIcon(funcs.G.src.ImgDir.link2))
    button.setToolTip("开启或关闭功能: 当创建新卡片时,自动将其添加到grahper,以便于进行下一步的链接操作\n"
                      "On/off: When a new card is created, it is automatically added to Grahper for the next link operation")
    oldicon = funcs.G.src.ImgDir.link2
    newicon = funcs.G.src.ImgDir.link2_red
    button.clicked.connect(lambda: funcs.button_icon_clicked_switch(button, ["off", oldicon], ["on", newicon],
                                                                    callback=newcard_grahper_open_close_switch
                                                                    ))
    addcards.form.buttonBox.addButton(button, QDialogButtonBox.ActionRole)


def open_grahper_with_newcard(note: "Note"):
    if funcs.G.mw_addcard_to_grapher_on:
        QTimer.singleShot(100, lambda: funcs.Dialogs.open_grapher(pair_li=
                                                                  [objs.LinkDataPair(str(note.card_ids()[0]), funcs.CardOperation.desc_extract(note.card_ids()[0]))]
                                                                  , need_activate=False))


def on_browser_sidebar_will_show_context_menu_handle(view: "SidebarTreeView", menu: "QMenu", item: "SidebarItem", index: "QModelIndex"):
    def open_grapher_with_deck_or_tag(item: "SidebarItem"):
        full_name = item.full_name
        if item.item_type == SidebarItemType.DECK:
            search_in = "deck"
        elif item.item_type == SidebarItemType.TAG:
            search_in = "tag"
        else:
            raise TypeError("未知的类型!")
        final = f"{search_in}:{full_name}"
        pairs_li = [str(cid) for cid in mw.col.find_cards(final)]
        tooltip(pairs_li)
        # view.browser.search_for(final)
        # view.browser.table._view.selectAll()
        # pairs_li = [ objs.LinkDataPair(str(card_id),funcs.desc_extract(card_id)) for card_id in view.browser.selected_cards()]
        funcs.GviewOperation.create_from_pair(pairs_li, name=full_name)

    if item.item_type in {SidebarItemType.TAG, SidebarItemType.DECK}:
        menu.addAction(funcs.Translate.新建视图).triggered.connect(lambda: open_grapher_with_deck_or_tag(item))


def 处理_视图中新建卡片(note: "Note"):
    视图索引 = funcs.G.常量_当前等待新增卡片的视图索引
    卡片索引 = note.card_ids()[0].__str__()
    if 视图索引 is not None:
        if type(视图索引)==str:
            from ..bilink.dialogs.linkdata_grapher import Grapher
            视图: Grapher = funcs.G.mw_gview[视图索引]
            视图.load_node([卡片索引])
        else:
            from .graphical_bilinker import VisualBilinker
            视图:VisualBilinker=funcs.G.mw_grapher
            视图.load_node([卡片索引])
    pass


def on_add_cards_did_add_note_handle(note: "Note"):
    处理_视图中新建卡片(note)
    pass
