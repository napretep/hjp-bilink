from .basic_funcs import *


class CardOperation:

    @staticmethod
    def 描述更新(card_id):
        字典键名 = G.safe.baseClass.枚举命名
        最新描述 = CardOperation.desc_extract(card_id)
        含card_id视图集 = 导入.Gview.GviewOperation.find_by_card([card_id])
        for 视图数据 in 含card_id视图集:
            视图窗口 = 导入.Gview.GviewOperation.判断视图已经打开(视图数据.uuid)
            if 视图窗口:
                视图窗口.data.gviewdata.设置结点属性(card_id, 字典键名.结点.描述, 最新描述)
        图形助手窗口 = 导入.Gview.GrapherOperation.判断视图已经打开()
        if 图形助手窗口 and card_id in 图形助手窗口.data.node_dict:
            图元 = 图形助手窗口.data.node_dict[card_id]
            图元.desc = 最新描述

    @staticmethod
    def 判断卡片被独立窗口预览(card_id):
        结果 = None
        # from ..bilink.dialogs.custom_cardwindow import SingleCardPreviewer
        SingleCardPreviewer = G.safe.bilinkDialogs.custom_cardwindow.SingleCardPreviewer
        if card_id in G.mw_card_window and isinstance(G.mw_card_window[card_id], SingleCardPreviewer):
            结果: SingleCardPreviewer = G.mw_card_window[card_id]
        return 结果

    @staticmethod
    def 删除不存在的结点(结点编号集: "list[str]"):
        Gview = 导入.Gview.GviewOperation
        Card = CardOperation
        DB = G.DB
        DB.go(DB.table_linkinfo)
        for 结点编号 in 结点编号集:
            视图数据集 = Gview.找到结点所属视图(结点编号)
            for 视图数据 in 视图数据集:
                视图窗口 = Gview.判断视图已经打开(视图数据.uuid)
                if 视图窗口 is not None:
                    视图窗口.remove_node(结点编号)
                    视图窗口.data.node_edge_packup()
            bilinker = 导入.Gview.GrapherOperation.判断视图已经打开()
            if bilinker and 结点编号 in bilinker.data.node_dict:
                bilinker.remove_node(结点编号)
            if 结点编号.isdigit():
                卡片独立窗口 = Card.判断卡片被独立窗口预览(结点编号)
                if 卡片独立窗口:
                    卡片独立窗口.close()
                # if DB.exists(DB.EQ(card_id=结点编号)):
                #     全局链接数据 = DB.select()
                # 数字类型的必然是卡片, 是卡片就要考虑他有没有全局链接数据

                pass
                # if DB.exists(DB.EQ(card_id))
                # 全局链接数据 = DB.select(DB.EQ())
                # for 文外链接 in 全局链接数据.link_list:
                #     导入.link.GlobalLinkDataOperation.unbind(结点编号,文外链接.card_id)

    # @staticmethod
    # def group_review(answer: AnswerInfoInterface):
    #     """用来同步复习卡片"""
    #
    #     if Config.get().group_review.value == False:
    #         return
    #     if answer.card_id not in G.GroupReview_dict.card_group:
    #         return
    #     if Config.get().group_review_comfirm_dialog.value:
    #         go_on = QMessageBox.information(None, "group_review", Translate.群组复习提示, QMessageBox.Yes | QMessageBox.No)
    #         if go_on == QMessageBox.No:
    #             return
    #     searchs = G.GroupReview_dict.card_group[answer.card_id]
    #
    #     sched = compatible_import.mw.col.sched
    #     reportstring = ""
    #     for search in searchs:
    #         cids = G.GroupReview_dict.search_group[search]
    #         for cid in cids:
    #             card = mw.col.get_card(CardId(cid))
    #             button_num = sched.answerButtons(card)
    #             ease = answer.option_num if button_num >= answer.option_num else button_num
    #             if card.timer_started is None: card.timer_started = time.time() - 60
    #             CardOperation.answer_card(card, ease)
    #             reportstring += str(cid) + ":" + CardOperation.desc_extract(cid) + "<br>"
    #     mw.col.reset()
    #     reportstring += "以上卡片已经同步复习<br>cards above has beend sync reviewed"
    #     tooltip(reportstring, period=5000)

    # @staticmethod
    # def 上次复习时间(card_id):
    # CardOperation.GetCard(card_id).load()

    @staticmethod
    def delay_card(card, delay_num):
        print(f"delay={delay_num}")
        mw.col.sched.set_due_date([card.id], str(delay_num))
        # card.due=card.due+delay_num
        # mw.col.flush
        card.flush()
        # print("refresh")
        CardOperation.refresh()
        pass

    @staticmethod
    def answer_card(card, ease):
        sched = mw.col.sched
        count = 10
        for i in range(count):
            Utils.print(f"try answer_card time={i}")
            try:
                sched.answerCard(card, ease)
                break
            except:
                time.sleep(0.2)
                continue
        导入.Gview.GrapherOperation.updateDue(f"{card.id}")
        导入.Gview.GviewOperation.更新卡片到期时间(f"{card.id}")

    @staticmethod
    def create(model_id: "int" = None, deck_id: "int" = None, failed_callback: "Callable" = None):
        if ISLOCALDEBUG:
            return "1234567890"
        if model_id is not None and not (type(model_id)) == int:
            model_id = int(model_id)
        if deck_id is not None and not (type(deck_id)) == int:
            deck_id = int(deck_id)

        if model_id is None:
            if "Basic" not in mw.col.models.allNames():
                # mw.col.models.add(stdmodels.addBasicModel(mw.col))
                material = json.load(open(G.src.path.card_model_template, "r", encoding="utf-8"))
                new_model = mw.col.models.new("Basic")
                new_model["flds"] = material["flds"]
                new_model["tmpls"] = material["tmpls"]
                mw.col.models.add(new_model)
            model = mw.col.models.by_name("Basic")
        else:
            if mw.col.models.have(model_id):
                model = mw.col.models.get(model_id)
            else:
                tooltip(f"modelId don't exist:{model_id}")
                if failed_callback:
                    failed_callback()
                return

        note = Anki.notes.Note(mw.col, model=model)
        if deck_id is None:
            deck_id = mw.col.decks.current()["id"]
        else:
            if not mw.col.decks.have(deck_id):
                tooltip(f"deck_id don't exist:{deck_id}")
        mw.col.add_note(note, deck_id=deck_id)
        note.flush()
        return str(note.card_ids()[0])

    @staticmethod
    def refresh(card_id=None):
        def prev_refresh(p: Previewer):
            # return False
            """在被包裹的函数执行完后刷新"""
            _last_state = p._last_state
            _card_changed = p._card_changed
            p._last_state = None
            p._card_changed = True
            p._render_scheduled()
            p._last_state = _last_state
            p._card_changed = _card_changed

        browser: "Browser" = 导入.browser.BrowserOperation.get_browser()
        if browser is not None and browser._previewer is not None:
            prev_refresh(browser._previewer)
        if mw.state == "review":
            mw.reviewer._refresh_needed = RefreshNeeded.NOTE_TEXT
            mw.reviewer.refresh_if_needed()  # 这个功能时好时坏,没法判断.

        for k, v in G.mw_card_window.items():
            if v is not None:
                prev_refresh(v)
        导入.Gview.GrapherOperation.refresh()
        # 导入.Gview.GviewOperation.刷新()
        # from ..bilink.dialogs.linkdata_grapher import Grapher

        # print("card refreshed")

    @staticmethod
    def exists(card_id):
        if isinstance(card_id, str) and not card_id.isdigit():
            return False
        cid = CardOperation.get_correct_id(card_id)
        txt = f"cid:{cid}"
        card_ids = mw.col.find_cards(txt)

        if len(card_ids) == 1:
            return True
        else:
            tooltip("卡片不存在/card not exists:\n"
                    "id=" + str(cid))
            return False

    @staticmethod
    def note_get(card_id):
        cid = CardOperation.get_correct_id(card_id)
        if CardOperation.exists(cid):
            note = CardOperation.GetCard(cid).note()
        else:
            showInfo(f"{cid} 卡片不存在/card don't exist")
            return None
        return note

    @staticmethod
    def 获取卡片内容与标题(card_id):
        note: Anki.notes.Note = CardOperation.note_get(card_id)
        卡片内容 = "\n".join(note.fields)
        卡片标题 = 导入.link.GlobalLinkDataOperation.read_from_db(card_id).self_data.desc
        return 卡片标题 + "\n" + 卡片内容

    @staticmethod
    def desc_extract(card_id, fromField=False):
        """读取逻辑,
        0 判断是否强制从卡片字段中提取
            0.1 是 则直接提取
            0.2 不是 再往下看.
        1 从数据库了解是否要auto update,
            1.1 不auto则读取数据库
            1.2 auto 则读取卡片本身
                1.2.1 从预设了解是否有预定的读取方案
                    1.2.1.1 若有预定的方案则根据预定方案读取
                    1.2.1.2 无预定方案, 则根据默认的方案读取.
       """
        cfg = 导入.Configs.Config.get()
        models = G.safe.models

        def get_desc_from_field(ins: "models.类型_模型_描述提取规则", note) -> str:
            if ins.字段.值 == -1:
                StrReadyToExtract = "".join(note.fields)
            else:
                StrReadyToExtract = note.fields[ins.字段.值]
            step1_desc = HTML.TextContentRead(StrReadyToExtract)
            # Utils.print(step1_desc)
            step2_desc = step1_desc if ins.长度.值 == 0 else step1_desc[0:int(ins.长度.值)]
            if ins.正则 != "":
                search = re.search(ins.正则, step2_desc)
                if search is None:
                    tooltip("根据设置中预留的正则表达式, 没有找到描述")
                else:
                    step2_desc = search.group()
            return step2_desc

        # from . import objs
        objs = G.objs

        ins = CardOperation.InstructionOfExtractDesc(card_id)

        note: Anki.notes.Note = CardOperation.note_get(card_id)
        if fromField:  # 若强制指定了要从字段中读取, 则抛弃以下讨论, 直接返回结果.
            # 确定字段
            return get_desc_from_field(ins, note)
        else:
            datainfo = 导入.link.GlobalLinkDataOperation.read_from_db(card_id)
            if datainfo.self_data.get_desc_from == objs.LinkDescFrom.DB:
                # print("--------=--=-=-=-=       desc  from DB       ")
                return datainfo.self_data._desc
            else:
                if ins.同步.值:
                    # 确定字段
                    return get_desc_from_field(ins, note)
                else:
                    datainfo.self_data.get_desc_from = objs.LinkDescFrom.DB
                    datainfo.save_to_DB()
                    return datainfo.self_data._desc

    @staticmethod
    def desc_save(card_id, desc):
        导入.link.GlobalLinkDataOperation.update_desc_to_db(G.objs.LinkDataPair(card_id, desc))

    @staticmethod
    def InstructionOfExtractDesc(card_id):
        models = G.safe.models

        cfg = 导入.Configs.Config.get()
        空规则 = models.类型_模型_描述提取规则()
        全部描述提取规则 = [models.类型_模型_描述提取规则(规则) for 规则 in cfg.descExtractTable.value]
        卡片信息 = mw.col.get_card(int(card_id))
        牌组编号 = 卡片信息.did
        模板编号 = 卡片信息.note().mid
        标签集: "set[str]" = set(卡片信息.note().tags)
        选中规则 = 空规则

        for 规则 in 全部描述提取规则:
            规则的标签集: "set[str]" = set(规则.标签.值)
            # 三个东西全部满足, 说明这条规则对上了, 就可以用,
            满足牌组 = 规则.牌组.值 == -1 or 牌组编号 == 规则.牌组.值 or 牌组编号 in [子[1] for 子 in
                                                                                      mw.col.decks.children(
                                                                                          规则.牌组.值)]
            满足模板 = (规则.模板.值 == -1 or 模板编号 == 规则.模板.值)

            满足标签 = (len(规则.标签.值) == 0 or 标签集 & 规则的标签集 != set() or len(
                [规则标签 for 规则标签 in 规则的标签集 if
                 len([标签 for 标签 in 标签集 if 标签.startswith(规则标签)]) > 0]) > 0)
            Utils.print("card model id=", 模板编号, "rule model id=", 规则.模板.值)
            if 满足牌组 and 满足模板 and 满足标签: # TODO add view check
                选中规则 = 规则

        return 选中规则
        # from . import objs
        # cfg = Config.get()
        # specialModelIdLi = [desc[0] for desc in cfg.descExtractTable.value]
        # modelId = CardOperation.note_get(card_id).mid
        # returnData = []
        # if modelId in specialModelIdLi:
        #     idx = specialModelIdLi.index(modelId)
        #     returnData = cfg.descExtractTable.value[idx]
        # elif -1 in specialModelIdLi:
        #     idx = specialModelIdLi.index(-1)
        #     returnData = cfg.descExtractTable.value[idx]
        # else:
        #     returnData = [-1, -1, cfg.length_of_desc.value, "", cfg.desc_sync.value]
        # return objs.descExtractTable(*returnData)

    @staticmethod
    def get_correct_id(card_id):
        # from . import objs
        objs = G.objs
        Card = anki.cards.Card
        if isinstance(card_id, objs.LinkDataPair):  # 有可能把pair传进来的
            cid = card_id.int_card_id
        elif isinstance(card_id, Card):
            cid = card_id.id
        elif isinstance(card_id, str):
            cid = int(card_id)
        elif type(card_id) == int:
            cid = card_id
        else:
            raise TypeError("参数类型不支持:" + card_id.__str__())
        return cid

    @staticmethod
    def GetCard(card_id_):
        card_id = CardOperation.get_correct_id(card_id_)
        if pointVersion() > 46:
            return mw.col.get_card(card_id)
        else:
            return mw.col.getCard(card_id)


    @staticmethod
    def getLastNextRev(card_id):
        """获取上次复习与下次复习时间"""
        result = mw.col.db.execute(
            # 从 数据库表revlog 中获取 上次回顾时间, 下次间隔, 推算出下次回顾的时间, 之所以直接从数据库提取是因为anki的接口做的很不清楚, 无法判断一个卡片是否可复习
            # 比如他的 card.due 值是时间戳, 表示到期时间, 但 也有一些到期时间比如746,1817480这种显然就不是时间戳
            f"select id,ivl from revlog where id = (select  max(id) from revlog where cid = {card_id})"
        )
        if result:
            last, ivl = result[0]
            last_date = datetime.datetime.fromtimestamp(last / 1000)  # (Y,M,D,H,M,S,MS)
            if ivl >= 0:  # ivl 正表示天为单位,负表示秒为单位
                next_date = datetime.datetime.fromtimestamp(last / 1000 + ivl * 86400)  # (Y,M,D,H,M,S,MS)
            else:
                next_date = datetime.datetime.fromtimestamp(last / 1000 - ivl)  # 此时的 ivl保存为负值,因此要减去
        else:
            # 没有记录表示新卡片, 直接给他设个1970年就完事
            next_date = datetime.datetime.fromtimestamp(0)  # (Y,M,D,H,M,S,MS)
            last_date = datetime.datetime.fromtimestamp(0)  # (Y,M,D,H,M,S,MS)
        # today = datetime.today()  # (Y,M,D,H,M,S,MS)
        # Utils.print(last_date, next_date)
        return last_date, next_date


