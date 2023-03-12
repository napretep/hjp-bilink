import anki.cards

from .basic_funcs import *


class Dialogs:
    """打开对话框的函数,而不是对话框本身"""

    @staticmethod
    def open_GviewAdmin():
        # from ..bilink.dialogs.linkdata_grapher import GViewAdmin
        GViewAdmin = G.safe.linkdata_grapher.GViewAdmin
        if isinstance(G.GViewAdmin_window, GViewAdmin):
            G.GViewAdmin_window.activateWindow()
        else:
            G.GViewAdmin_window = GViewAdmin()
            G.GViewAdmin_window.show()

    @staticmethod
    def open_anchor(card_id):
        card_id = str(card_id)
        # from ..bilink.dialogs.anchor import AnchorDialog
        # from . import G
        AnchorDialog = G.safe.bilinkDialogs.anchor.AnchorDialog
        if card_id not in G.mw_anchor_window:
            G.mw_anchor_window[card_id] = None
        if G.mw_anchor_window[card_id] is None:
            G.mw_anchor_window[card_id] = AnchorDialog(card_id)
            G.mw_anchor_window[card_id].show()
        else:
            G.mw_anchor_window[card_id].activateWindow()

    @staticmethod
    def open_linkpool():
        LinkPoolDialog = G.safe.bilinkDialogs.linkpool.LinkPoolDialog
        if G.mw_linkpool_window is None:
            G.mw_linkpool_window = LinkPoolDialog()
            G.mw_linkpool_window.show()
        else:
            G.mw_linkpool_window.activateWindow()
        pass

    @staticmethod
    def open_custom_cardwindow(card: Union[anki.cards.Card, str, int]) -> 'Optional[G.safe.bilinkDialogs.custom_cardwindow.SingleCardPreviewer]':
        """请注意需要你自己激活窗口 请自己做好卡片存在性检查,这一层不检查 """
        # from ..bilink.dialogs.custom_cardwindow import external_card_dialog
        external_card_dialog = G.safe.bilinkDialogs.custom_cardwindow.external_card_dialog
        Card = anki.cards.Card,
        CardId = anki.cards.CardId
        if not isinstance(card, Card):
            card = mw.col.get_card(CardId(int(card)))
        return external_card_dialog(card)
        pass

    @staticmethod
    def open_support():

        p = G.safe.widgets.SupportDialog()
        p.exec()

    @staticmethod
    def open_contact():
        QDesktopServices.openUrl(QUrl(G.src.path.groupSite))

    @staticmethod
    def open_link_storage_folder():
        open_file(G.src.path.user)

    @staticmethod
    def open_repository():
        QDesktopServices.openUrl(QUrl(G.src.path.helpSite))

    @staticmethod
    def open_inrtoDoc():
        Utils.版本.打开网址()
        # from ..bilink import dialogs
        # p = dialogs.version.VersionDialog()
        # p.show()

    @staticmethod
    def open_tag_chooser(pair_li: "list[G.objs.LinkDataPair]"):

        p = G.safe.widgets.tag_chooser_for_cards(pair_li)
        p.exec()
        pass

    @staticmethod
    def open_deck_chooser(pair_li: "list[G.objs.LinkDataPair]", view=None):

        p = G.safe.widgets.deck_chooser_for_changecard(pair_li, view)
        p.exec()
        tooltip("完成")

        pass

    @staticmethod
    def open_view(gviewdata: G.safe.configsModel.GViewData = None, need_activate=True):
        Dialogs.open_grapher(gviewdata=gviewdata, mode=G.safe.configsModel.GraphMode.view_mode)

    @staticmethod
    def open_grapher(pair_li: "list[G.objs.LinkDataPair|str]" = None, need_activate=True,
                     gviewdata: "G.safe.configsModel.GViewData" = None, selected_as_center=True,
                     mode=G.safe.configsModel.GraphMode.normal, ):
        Grapher = G.safe.linkdata_grapher.Grapher
        if mode == G.safe.configsModel.GraphMode.normal:
            # from .graphical_bilinker import VisualBilinker
            VisualBilinker = G.safe.graphical_bilinker.VisualBilinker
            if isinstance(G.mw_grapher, VisualBilinker):
                G.mw_grapher.load_node(pair_li, selected_as_center=selected_as_center)
                if need_activate:
                    G.mw_grapher.activateWindow()
            else:
                G.mw_grapher = VisualBilinker(pair_li)
                G.mw_grapher.show()
        elif mode == G.safe.configsModel.GraphMode.view_mode:
            if (gviewdata.uuid not in G.mw_gview) or (not isinstance(G.mw_gview[gviewdata.uuid], Grapher)):
                G.mw_gview[gviewdata.uuid] = Grapher(mode=mode, gviewdata=gviewdata)
                G.mw_gview[gviewdata.uuid].load_node(pair_li)
                G.mw_gview[gviewdata.uuid].show()
            else:
                G.mw_gview[gviewdata.uuid].load_node(pair_li)
                # tooltip(f"here G.mw_gview[{gviewdata.uuid}]")
                if need_activate:
                    G.mw_gview[gviewdata.uuid].show()
                    G.mw_gview[gviewdata.uuid].activateWindow()
        elif mode == G.safe.configsModel.GraphMode.debug_mode:
            Grapher(pair_li=pair_li, mode=mode, gviewdata=gviewdata).show()

    @staticmethod
    def open_configuration():
        """ 这里的内容要整理到Config的父类中"""
        dialog = imports.Configs.Config.makeConfigDialog(None, imports.Configs.Config.get(),
                                                       # 关闭时回调=None)
                                                       lambda 数据: imports.Configs.Config.save(数据))  # save的参数是经过修正的cfg

        dialog.exec()

    # @staticmethod
    # def open_clipper(pairs_li=None, clipboxlist=None, **kwargs):
    #     if platform.system() in {"Darwin", "Linux"}:
    #         tooltip("当前系统暂时不支持PDFprev")
    #         return
    #     elif Utils.isQt6():
    #         tooltip("暂时不支持QT6")
    #         return
    #     else:
    #         # from . import G
    #         from ..clipper2.lib.Clipper import Clipper
    #     # log.debug(G.mw_win_clipper.__str__())
    #     if not isinstance(G.mw_win_clipper, Clipper):
    #         G.mw_win_clipper = Clipper()
    #         G.mw_win_clipper.start(pairs_li=pairs_li, clipboxlist=clipboxlist)
    #         G.mw_win_clipper.show()
    #     else:
    #         G.mw_win_clipper.start(pairs_li=pairs_li, clipboxlist=clipboxlist)
    #         # all_objs.mw_win_clipper.show()
    #         G.mw_win_clipper.activateWindow()
    #         # print("just activate")

    # @staticmethod
    # def open_PDFprev(pdfuuid, pagenum, FROM):
    #     if platform.system() in {"Darwin", "Linux"}:
    #         tooltip("当前系统暂时不支持PDFprev")
    #         return
    #     else:
    #         from ..clipper2.lib.PDFprev import PDFPrevDialog
    #     # print(FROM)
    #     if isinstance(FROM, Reviewer):
    #         card_id = FROM.card.id
    #         pass
    #     elif isinstance(FROM, BrowserPreviewer):
    #         card_id = FROM.card().id
    #         pass
    #     elif isinstance(FROM, SingleCardPreviewer):
    #         card_id = FROM.card().id
    #     else:
    #         TypeError("未能找到card_id")
    #     card_id = str(card_id)
    #
    #     DB = G.DB
    #     result = DB.go(DB.table_pdfinfo).select(uuid=pdfuuid).return_all().zip_up()[0]
    #     DB.end()
    #     pdfname = result.to_pdfinfo_data().pdf_path
    #     pdfpageuuid = UUID.by_hash(pdfname + str(pagenum))
    #     if card_id not in G.mw_pdf_prev:
    #         G.mw_pdf_prev[card_id] = {}
    #     if pdfpageuuid not in G.mw_pdf_prev[card_id]:
    #         G.mw_pdf_prev[card_id][pdfpageuuid] = None
    #     if isinstance(G.mw_pdf_prev[card_id][pdfpageuuid], PDFPrevDialog):
    #         G.mw_pdf_prev[card_id][pdfpageuuid].activateWindow()
    #     else:
    #         ratio = 1
    #         G.mw_pdf_prev[card_id][pdfpageuuid] = \
    #             PDFPrevDialog(pdfuuid=pdfuuid, pdfname=pdfname, pagenum=pagenum, pageratio=ratio, card_id=card_id)
    #         G.mw_pdf_prev[card_id][pdfpageuuid].show()
    #
    #     pass
