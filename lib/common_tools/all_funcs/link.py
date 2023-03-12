from .basic_funcs import *


class GlobalLinkDataOperation:
    """针对链接数据库的操作,
    这里的LinkDataOperation.bind/unbind和LinkPoolOperation中的link/unlink是类似但不同,不冲突.
    因为那是一个link池里的操作,而这不是, 这是一个普通的链接操作
    """

    @staticmethod
    def read_from_db(card_id):
        # from ..bilink.linkdata_admin import read_card_link_info
        return G.safe.linkdata_admin.read_card_link_info(card_id)

    @staticmethod
    def write_to_db(card_id, data):
        # from ..bilink.linkdata_admin import write_card_link_info
        return G.safe.linkdata_admin.write_card_link_info(card_id, data)

    @staticmethod
    def update_desc_to_db(pair: G.objs.LinkDataPair):
        """仅根据pair的desc信息更新,别的不做"""
        data = GlobalLinkDataOperation.read_from_db(pair.card_id)
        data.self_data.desc = pair._desc
        data.self_data.get_desc_from = G.objs.LinkDescFrom.DB
        data.save_to_DB()
        if pair.get_desc_from == G.objs.LinkDescFrom.Field:
            tooltip(译.描述已修改但是___, period=6000)

    @staticmethod
    def bind(card_idA: 'Union[str,G.objs.LinkDataJSONInfo]', card_idB: 'Union[str,G.objs.LinkDataJSONInfo]', needsave=True):
        """needsave关闭后,需要自己进行save"""
        if isinstance(card_idA, G.objs.LinkDataJSONInfo) and isinstance(card_idB, G.objs.LinkDataJSONInfo):
            cardA, cardB = card_idA, card_idB
        else:
            # from ..bilink import linkdata_admin
            cardA = G.safe.linkdata_admin.read_card_link_info(card_idA)
            cardB = G.safe.linkdata_admin.read_card_link_info(card_idB)
        if cardB.self_data not in cardA.link_list:
            cardA.append_link(cardB.self_data)
            if needsave: cardA.save_to_DB()
        if cardA.self_data not in cardB.link_list:
            cardB.append_link(cardA.self_data)
            if needsave: cardB.save_to_DB()

    @staticmethod
    def unbind(card_idA: 'Union[str,G.objs.LinkDataJSONInfo]', card_idB: 'Union[str,G.objs.LinkDataJSONInfo]', needsave=True):
        """needsave关闭后,需要自己进行save"""
        # from ..bilink import linkdata_admin

        cardA = card_idA if isinstance(card_idA, G.objs.LinkDataJSONInfo) else G.safe.linkdata_admin.read_card_link_info(card_idA)
        cardB = card_idB if isinstance(card_idB, G.objs.LinkDataJSONInfo) else G.safe.linkdata_admin.read_card_link_info(card_idB)

        if cardB.self_data in cardA.link_list:
            cardA.remove_link(cardB.self_data)
            if needsave: cardA.save_to_DB()
        if cardA.self_data in cardB.link_list:
            cardB.remove_link(cardA.self_data)
            if needsave: cardB.save_to_DB()

    @staticmethod
    def backup(cfg: G.safe.configsModel.ConfigModel, now=None):
        if not now: now = datetime.datetime.now().timestamp()
        db_file = G.src.path.DB_file
        path = cfg.auto_backup_path.value
        backup_name = Utils.make_backup_file_name(db_file, path)
        shutil.copy(db_file, backup_name)
        cfg.last_backup_time.value = now
        cfg.save_to_file(G.src.path.userconfig)

    @staticmethod
    def need_backup(cfg: G.safe.configsModel.ConfigModel, now) -> bool:
        if not cfg.auto_backup.value:
            return False
        last = cfg.last_backup_time.value
        if (now - last) / 3600 < cfg.auto_backup_interval.value:
            return False
        return True