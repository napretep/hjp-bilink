from .basic_widgets import *


class DeckSelectorProtoType(SelectorProtoType):
    def __init__(self, title_name="", separator="::", header_name=""):
        super().__init__(title_name, separator, header_name)

    def on_header_new_item_button_clicked_handle(self):
        new_item = self.Item(f"""new_deck_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}""")
        if self.view.selectedIndexes():
            item: "DeckSelectorProtoType.Item" = self.model.itemFromIndex(self.view.selectedIndexes()[0])
            parent_item = item.parent()
        else:
            parent_item = self.model.invisibleRootItem()
        parent_item.appendRow([new_item])
        self.view.edit(new_item.index())
        deck = mw.col.decks.add_normal_deck_with_name(self.get_full_item_name(new_item))
        new_item.deck_id = deck.id

    def on_view_doubleclicked_handle(self, index):
        raise NotImplementedError()

    # def on_item_button_clicked_handle(self, item: "deck_chooser.Item"):
    #     raise NotImplementedError()

    def on_model_data_changed_handle(self, topLeft, bottomRight, roles):
        item: "DeckSelectorProtoType.Item" = self.model.itemFromIndex(topLeft)

        DeckId = G.safe.funcs.Compatible.DeckId()
        new_deck_name = self.get_full_item_name(item)
        mw.col.decks.rename(DeckId(item.data_id), new_deck_name)
        # print(item.deck_name)

    def on_view_clicked_handle(self, index):
        item: DeckSelectorProtoType.Item = self.model.itemFromIndex(index)
        # tooltip(self.get_full_item_name(item))

    def get_all_data_items(self):

        decks = mw.col.decks
        return [self.Id_name(name=i.name, ID=i.id) for i in decks.all_names_and_ids() if
                not decks.is_filtered(i.id)]


class deck_chooser_for_changecard(DeckSelectorProtoType):

    def __init__(self, pair_li: "list[G.objs.LinkDataPair]" = None, fromview: "AnkiWebView" = None):
        super().__init__(title_name="deck_chooser", header_name="deck_name")
        self.fromview: "None|AnkiWebView|Previewer|Reviewer" = fromview
        self.pair_li = pair_li
        self.header.set_header_label(self.curr_deck_name)

    @property
    def curr_deck_name(self):
        CardId = G.safe.funcs.CardId
        if len(self.pair_li) == 1:
            did = mw.col.getCard(CardId(int(self.pair_li[0].card_id))).did
            name = mw.col.decks.get(did)["name"]
            return name
        else:
            return "many cards"

    def on_view_doubleclicked_handle(self, index):
        item = self.model.itemFromIndex(index)
        funcs = G.safe.funcs
        # showInfo(self.fromview.__str__())
        DeckId = funcs.Compatible.DeckId()
        CardId = funcs.CardId
        browser: Browser = funcs.BrowserOperation.get_browser()

        if browser is None:
            dialogs.open("Browser", mw)
            browser = funcs.BrowserOperation.get_browser()
        for pair in self.pair_li:
            set_card_deck(parent=browser, card_ids=[CardId(pair.int_card_id)],
                          deck_id=DeckId(item.data_id)).run_in_background()
        browser.showMinimized()
        Grapher = G.safe.linkdata_grapher.Grapher
        if isinstance(self.fromview, AnkiWebView):
            parent: "Union[Previewer,Reviewer]" = self.fromview.parent()
            parent.activateWindow()
        elif isinstance(self.fromview, Grapher):
            self.fromview.activateWindow()
        QTimer.singleShot(100, funcs.LinkPoolOperation.both_refresh)
        self.close()


class universal_deck_chooser(DeckSelectorProtoType):
    def on_view_doubleclicked_handle(self, index):
        item: "DeckSelectorProtoType.Item" = self.model.itemFromIndex(index)
        self.结果 = item.data_id
        self.close()

    def __init__(self, ):
        super().__init__(title_name="deck chooser", header_name="deck name")
        self.结果 = -1


class universal_template_chooser(SelectorProtoType):
    def __init__(self, ):
        super().__init__(title_name="template chooser", header_name="template name")
        self.结果 = -1
        self.tree_structure = False
        self.header.button.hide()
        self.header.new_item_button.hide()

    def on_header_new_item_button_clicked_handle(self):
        pass

    def on_model_data_changed_handle(self, topLeft, bottomRight, roles):
        pass

    def on_view_clicked_handle(self, index):
        pass

    def get_all_data_items(self) -> "list[SelectorProtoType.Id_name]":
        all_models = mw.col.models.all_names_and_ids()
        return [self.Id_name(name=i.name, ID=i.id) for i in all_models]
        pass

    def on_view_doubleclicked_handle(self, index):
        item: "DeckSelectorProtoType.Item" = self.model.itemFromIndex(index)
        self.结果 = item.data_id
        self.close()


class view_chooser(SelectorProtoType):
    def on_view_doubleclicked_handle(self, index):
        item: "DeckSelectorProtoType.Item" = self.model.itemFromIndex(index)
        self.编号 = item.data_id
        self.close()
        pass

    def on_header_new_item_button_clicked_handle(self):
        pass

    def on_model_data_changed_handle(self, topLeft, bottomRight, roles):
        pass

    def on_view_clicked_handle(self, index):
        pass

    def get_all_data_items(self) -> "list[SelectorProtoType.Id_name]":
        gview_dict = G.safe.funcs.GviewOperation.load_all_as_dict()
        return [self.Id_name(name=data.name, ID=uuid) for uuid, data in gview_dict.items()]
        pass

    def __init__(self, title_name="", separator="::", header_name=""):
        super().__init__(title_name, separator, header_name)
        self.header.new_item_button.hide()
        self.编号 = -1


class SimpleSelectorProtoType(SelectorProtoType):
    """SelectorProtoType的函数太多太复杂，平时用到的并不多， 所以弄一个简单的"""

    def on_header_new_item_button_clicked_handle(self):
        pass

    def on_model_data_changed_handle(self, topLeft, bottomRight, roles):
        pass

    def on_view_clicked_handle(self, index):
        pass

    def get_all_data_items(self) -> "list[SelectorProtoType.Id_name]":
        raise NotImplementedError()

    def on_view_doubleclicked_handle(self, index):
        raise NotImplementedError()


class view_config_chooser(SimpleSelectorProtoType):

    def get_all_data_items(self) -> "list[SelectorProtoType.Id_name]":
        return [self.Id_name(name=config["name"], ID=config["uuid"])
                for config in G.safe.funcs.GviewConfigOperation.获取全部配置表字典()]

    def on_view_doubleclicked_handle(self, index):
        item: "SimpleSelectorProtoType.Item" = self.model.itemFromIndex(index)
        self.结果 = item.Id_name
        self.close()
        pass

    def __init__(self, title_name="", separator="::", header_name=""):
        super().__init__(title_name, separator, header_name)
        self.header.new_item_button.hide()
        self.结果: Union[DeckSelectorProtoType.Id_name, None] = None


class universal_field_chooser(SelectorProtoType):
    def __init__(self, 模板编号, title_name="", separator="::", header_name=""):
        self.模板编号: "int" = 模板编号
        self.tree_structure = False
        super().__init__("choose a field", separator, "field name")
        self.header.new_item_button.hide()
        self.header.button.hide()
        self.结果 = -1

    def on_header_new_item_button_clicked_handle(self):
        pass

    def on_model_data_changed_handle(self, topLeft, bottomRight, roles):
        pass

    def on_view_clicked_handle(self, index):
        pass

    def get_all_data_items(self) -> "list[SelectorProtoType.Id_name]":
        字段名集 = mw.col.models.field_names(mw.col.models.get(self.模板编号))
        return [self.Id_name(name=字段名集[i], ID=i) for i in range(len(字段名集))]
        pass

    def on_view_doubleclicked_handle(self, index):
        item: "DeckSelectorProtoType.Item" = self.model.itemFromIndex(index)
        self.结果 = item.data_id
        self.close()
        pass


class universal_tag_chooser(multi_select_prototype):
    def get_all_items(self) -> 'set[str]':
        return set(mw.col.tags.all())

    def __init__(self, preset: "Iterable[str]" = None):
        super().__init__(preset)


class tag_chooser_for_cards(universal_tag_chooser):
    def __init__(self, pair_li: "Optional[list[G.objs.LinkDataPair]]" = None):
        super().__init__()
        self.pair_li = pair_li
        self.item_list = self.get_all_tags_from_pairli()
        self.init_data_left()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        s = self.save()
        CardId = G.safe.funcs.CardId
        for pair in self.pair_li:
            note = mw.col.getCard(CardId(pair.int_card_id)).note()
            note.set_tags_from_str(" ".join(s))
            note.flush()
        G.safe.funcs.LinkPoolOperation.both_refresh()

    def add_tag(self, tag_name: str):
        CardId = G.safe.funcs.CardId
        if tag_name is None:
            return
        for pair in self.pair_li:
            note = mw.col.getCard(CardId(pair.int_card_id)).note()
            note.add_tag(tag_name)
            note.flush()

    def get_all_tags_from_pairli(self) -> 'set[str]':
        """多张卡片要取公共的"""
        tags = set()
        for pair in self.pair_li:
            tag = set(mw.col.getCard(pair.int_card_id).note().tags)
            if tags == set():
                tags |= tag
            else:
                tags &= tag
        return tags
        pass


class role_chooser_for_node(multi_select_prototype):

    def closeEvent(self, QCloseEvent):
        左侧表的字符串 = self.save()
        self.结果 = [self.角色表.index(角色名) for 角色名 in 左侧表的字符串 if 角色名 in self.角色表]

    def get_all_items(self) -> 'set[str]':
        return set(self.角色表)

    def __init__(self, preset, 角色表: "list[str]"):
        self.角色表 = 角色表
        super().__init__([角色表[pos] for pos in preset if pos in range(len(角色表))], )
        self.left_button_group.left_button.hide()
        self.left_button_group.arrange_button.hide()
        self.right_button_group.arrange_button.hide()
        self.init_data_right()
        self.init_data_left()
