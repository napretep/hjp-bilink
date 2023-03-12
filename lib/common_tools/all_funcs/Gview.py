from .basic_funcs import *


class GviewOperation:

    @staticmethod
    def 获取视图配置编号(data: Union[str, G.safe.configsModel.GViewData]) -> "str":
        uuid = data if type(data) == str else data.uuid
        DB = G.DB
        DB.go(DB.table_Gview)
        return DB.select(DB.EQ(uuid=uuid)).return_all().zip_up()[0]["config"]


    @staticmethod
    def 设为默认视图(uuid):
        cfg = 导入.Configs.Config.get()
        cfg.set_default_view.value = uuid
        cfg.save_to_file(G.src.path.userconfig)


    @staticmethod
    def 打开默认视图():
        cfg = 导入.Configs.Config.get()
        if cfg.set_default_view.value != -1:
            导入.Dialogs.open_view(gviewdata=GviewOperation.load(uuid=cfg.set_default_view.value))
        else:
            showInfo(译.请先设定默认视图)


    @staticmethod
    def 打开默认漫游复习():
        cfg = 导入.Configs.Config.get()
        if cfg.set_default_view.value != -1:
            GviewOperation.打开默认视图()
            # from ..bilink.dialogs.linkdata_grapher import Grapher
            view: G.safe.linkdata_grapher.Grapher = G.mw_gview[cfg.set_default_view.value]
            view.toolbar.openRoaming()
        else:
            showInfo(译.请先设定默认视图)


    @staticmethod
    def 判断视图已经打开(视图编号):
        """判断且直接返回"""
        # from ..bilink.dialogs.linkdata_grapher import Grapher

        if 视图编号 in G.mw_gview and isinstance(G.mw_gview[视图编号], G.safe.linkdata_grapher.Grapher):
            视图窗口: G.safe.linkdata_grapher.Grapher = G.mw_gview[视图编号]
            return 视图窗口
        else:
            return None


    @staticmethod
    def 更新卡片到期时间(卡片编号):
        视图数据集 = GviewOperation.找到结点所属视图(卡片编号)
        for 视图数据 in 视图数据集:
            视图窗口 = GviewOperation.判断视图已经打开(视图数据.uuid)
            if 视图窗口:
                视图窗口.data.node_dict[卡片编号].due = GviewOperation.判断结点已到期(视图数据, 卡片编号)

        pass


    @staticmethod
    def 重命名(视图数据: G.safe.configsModel.GViewData, 新名字):
        视图数据.name = 新名字
        GviewOperation.save(视图数据)
        # tooltip("改名成功".format(view_name=视图数据.name, name=新名字))


    @staticmethod
    def 获取主要结点编号(视图数据: G.safe.configsModel.GViewData):
        return [结点 for 结点 in 视图数据.nodes if 视图数据.nodes[结点].主要结点.值 == True]


    @staticmethod
    def 判断结点已到期(视图数据: G.safe.configsModel.GViewData, 结点编号: str):
        现在 = int(time.time())
        类型 = 视图数据.nodes[结点编号].数据类型.值
        枚举_视图结点类型 = G.safe.baseClass.视图结点类型
        if 类型 == 枚举_视图结点类型.卡片:
            _, nextRev = G.safe.funcs.CardOperation.getLastNextRev(结点编号)
            # Utils.print("card_id=",结点编号,"nextRev=",nextRev,)
            # Utils.print(nextRev.timetuple())
            return int(time.mktime(nextRev.timetuple())) <= 现在
        elif 类型 == 枚举_视图结点类型.视图:
            return True
        else:
            raise NotImplementedError()


    @staticmethod
    def 结点上次复习时间(视图数据:G.safe.configsModel.GViewData, 结点编号: str):
        """如果是卡片, 则调用 CardOperation.上次复习时间(结点编号)
        否则另外解决
        """
        枚举_视图结点类型 = G.safe.baseClass.视图结点类型
        字典键名 = G.safe.baseClass.枚举命名
        类型 = 视图数据.nodes[结点编号].数据类型.值
        if 类型 == 枚举_视图结点类型.卡片:
            return G.safe.funcs.CardOperation.getLastNextRev(结点编号)[0]
        elif 类型 == 枚举_视图结点类型.视图:
            return Utils.时间戳转日期(视图数据.meta[字典键名.视图.上次复习])
        else:
            raise NotImplementedError()


    @staticmethod
    def 获取结点出度(视图数据: G.safe.configsModel.GViewData, 结点编号: str):
        return len([1 for 边 in 视图数据.edges.keys() if 边.startswith(结点编号)])


    @staticmethod
    def 获取结点入度(视图数据: G.safe.configsModel.GViewData, 结点编号: str):
        return len([1 for 边 in 视图数据.edges.keys() if 边.endswith(结点编号)])


    @staticmethod
    def 设定视图结点描述(视图数据: G.safe.configsModel.GViewData, 结点编号, 设定内容):
        视图类型 = 视图数据.nodes[结点编号].数据类型.值
        Utils.print(结点编号, 设定内容)
        枚举_视图结点类型 = G.safe.baseClass.视图结点类型
        字典键名 = G.safe.baseClass.枚举命名
        if 视图类型 == 枚举_视图结点类型.卡片:
            G.safe.funcs.CardOperation.desc_save(结点编号, 设定内容)
            G.safe.funcs.CardOperation.refresh()
        else:
            结点对应视图 = GviewOperation.load(结点编号)
            结点对应视图.name = 设定内容
            GviewOperation.save(结点对应视图)
        if GviewOperation.判断视图已经打开(视图数据.uuid):
            视图数据.nodes.data[结点编号][字典键名.结点.描述] = 设定内容


    @staticmethod
    def 获取视图结点描述(视图数据: G.safe.configsModel.GViewData, 结点编号, 全部内容=False):
        视图类型 = 视图数据.nodes[结点编号].数据类型.值
        枚举_视图结点类型 = G.safe.baseClass.视图结点类型
        字典键名 = G.safe.baseClass.枚举命名
        if 视图类型 == 枚举_视图结点类型.卡片:
            return G.safe.funcs.CardOperation.desc_extract(结点编号) if not 全部内容 else G.safe.funcs.CardOperation.获取卡片内容与标题(结点编号)
        else:
            return GviewOperation.load(uuid=结点编号).name

        pass


    @staticmethod
    def 获取视图名字(视图编号):
        if not GviewOperation.exists(uuid=视图编号):
            raise ValueError(f"视图:{视图编号}不存在")

        DB = G.DB
        return DB.go(DB.table_Gview).select(DB.EQ(uuid=视图编号)).return_all().zip_up()[0]["name"]


    @staticmethod
    def 列出已打开的视图():
        Grapher =G.safe.linkdata_grapher.Grapher
        结果: List[str] = [键 for 键 in G.mw_gview.keys() if isinstance(G.mw_gview[键], Grapher)]
        return 结果


    @staticmethod
    def 更新缓存(视图: "str|G.safe.configsModel.GViewData" = None):
        """这个东西, 更新的是一个表, 这个表的每个记录对应一个视图索引,
        记录的第一列是视图索引, 第二列是视图中全部卡片描述的并集, 用于搜索关键词定位视图
        流程, 如果存在数据表, 则drop table, 然后生成新的插
        """
        Logic = G.objs.Logic
        枚举_视图结点类型 = G.safe.baseClass.视图结点类型
        字典键名 = G.safe.baseClass.枚举命名
        DB = G.DB
        if 视图:
            if type(视图) == str:
                数据 = GviewOperation.load(uuid=视图)
                编号 = 视图
            else:
                数据 = 视图
                编号 = 视图.uuid
            缓存内容 = "\n".join(
                GviewOperation.获取视图结点描述(数据, 索引, 全部内容=True) for 索引 in 数据.nodes.keys())
            DB.go(DB.table_Gview)

            DB.update(values=Logic.LET(**{字典键名.视图.视图卡片内容缓存: 缓存内容}),
                      where=Logic.EQ(uuid=编号)
                      ).commit()

        else:

            # DB.go(DB.table_Gview_cache)
            Utils.tooltip("gview cache begin to rebuild")
            DB.表删除(DB.table_Gview_cache)

            视图数据表 = GviewOperation.load_all_as_dict()
            视图缓存字典 = []
            计数 = 0
            for 数据 in 视图数据表.values():
                结点索引表 = list(数据.nodes.keys())
                视图缓存字典.append([数据.uuid, ""])

                for 结点索引 in 结点索引表:

                    if ISLOCALDEBUG:
                        描述 = "debug"
                    else:
                        描述 = G.safe.funcs.CardOperation.获取卡片内容与标题(结点索引) if 数据.nodes[结点索引][
                                                                                 字典键名.结点.数据类型] == 枚举_视图结点类型.卡片 \
                            else 视图数据表[结点索引].name

                    视图缓存字典[-1][1] += 描述 + "\n"
                视图缓存字典[-1][1] = "'" + 视图缓存字典[-1][1] + "'"
            DB.go(DB.table_Gview_cache).批量插入(视图缓存字典)

        Utils.tooltip("gview cache rebuild end")


    @staticmethod
    def 刷新所有已打开视图的配置():
        Grapher =G.safe.linkdata_grapher.Grapher
        for 视图编号 in GviewOperation.列出已打开的视图():
            视图窗口: Grapher = G.mw_gview[视图编号]
            视图窗口.data.gviewdata.数据更新.刷新配置模型()
            # 视图窗口.data.gviewdata.config_model = GviewConfigOperation.从数据库读(视图窗口.data.gviewdata.config)


    @staticmethod
    def fuzzy_search(search_string: str):
        """在GRAPH_VIEW , GRAPH_VIEW_CACHE 两个表中做模糊搜索, 将用户的空格替换成通配符"""
        # 关键词正则 = re.sub(r"\s", ".*", search_string)
        关键词正则 = re.sub(r"\s", "%", search_string)
        DB, Logic = G.DB, G.objs.Logic

        DB.go(DB.table_Gview)
        DB.excute_queue.append(f"""select * from GRAPH_VIEW_TABLE where 
        name like '%{关键词正则}%' 
        or uuid like '%{关键词正则}%' 
        or card_content_cache like '%{关键词正则}%' """)
        匹配的视图集 = [data.to_GviewData() for data in DB.return_all().zip_up().to_gview_record()]

        return 匹配的视图集
        pass


    @staticmethod
    def save(data: G.safe.configsModel.GViewData = None, data_li: "Iterable[G.safe.configsModel.GViewData]" = None, exclude: "list[str]" = None):
        """"""
        Logic = G.objs.Logic
        if data:
            # Utils.print("保存前的数据", data)
            prepare_data = data.to_DB_format()
            # Utils.print("写入数据库的数据", prepare_data)
            if exclude is not None:
                [prepare_data.pop(item) for item in exclude]
            DB = G.DB.go(G.DB.table_Gview)

            if DB.exists(Logic.EQ(uuid=data.uuid)):
                DB.update(values=Logic.LET(**prepare_data), where=Logic.EQ(uuid=data.uuid)).commit()
            else:
                DB.insert(**prepare_data).commit()
            return
        elif data_li:
            DB = G.DB.go(G.DB.table_Gview)
            for data in data_li:
                prepare_data = data.to_DB_format()
                if exclude is not None:
                    [prepare_data.pop(item) for item in exclude]
                if DB.exists(Logic.EQ(uuid=data.uuid)):
                    DB.update(values=Logic.LET(**prepare_data), where=Logic.EQ(uuid=data.uuid)).commit()
                else:
                    DB.insert(**prepare_data).commit()
            return


    @staticmethod
    def exists(data: G.safe.configsModel.GViewData = None, name=None, uuid=None):
        DB = G.DB
        DB.go(DB.table_Gview)
        exists = False
        if data:
            exists = DB.exists(DB.EQ(uuid=data.uuid))
        elif name:
            exists = DB.exists(DB.EQ(name=name))
        elif uuid:
            exists = DB.exists(DB.EQ(uuid=uuid))
        return exists


    @staticmethod
    def load(uuid=None, gviewdata: G.safe.configsModel.GViewData = None):
        """"""
        # print("uuid=",uuid)
        data = None
        if GviewOperation.exists(uuid=uuid):
            DB = G.DB
            DB.go(DB.table_Gview)
            data = DB.select(DB.EQ(uuid=uuid)).return_all().zip_up().to_gview_record()[0].to_GviewData()

        elif gviewdata is not None:
            DB = G.DB
            DB.go(DB.table_Gview)
            data = DB.select(DB.EQ(uuid=gviewdata.uuid)).return_all().zip_up().to_gview_record()[0].to_GviewData()

        # elif pairli is not None:
        #     data = GviewOperation.find_by_card(pairli)
        if data is None:
            raise ValueError(f"未知的uuid={uuid},或gviewdata={gviewdata}")
        return data


    @staticmethod
    def load_all() -> 'List[G.safe.configsModel.GViewData]':
        DB = G.DB
        DB.go(DB.table_Gview)
        DB.excute_queue.append(DB.sqlstr_RECORD_SELECT_ALL.format(tablename=DB.tab_name))
        records = [记录.to_GviewData() for 记录 in DB.return_all().zip_up().to_gview_record()]
        return records


    @staticmethod
    def load_all_as_dict() -> Dict[str,G.safe.configsModel.GViewData]:
        DB = G.DB
        DB.go(DB.table_Gview)
        DB.excute_queue.append(DB.sqlstr_RECORD_SELECT_ALL.format(tablename=DB.tab_name))
        记录表 = DB.return_all().zip_up().to_gview_record()
        结果 = {}
        [结果.__setitem__(记录.uuid, 记录.to_GviewData()) for 记录 in 记录表]
        return 结果


    @staticmethod
    def 读取全部id():
        DB = G.DB
        DB.go(DB.table_Gview)
        DB.excute_queue.append(DB.sqlstr_RECORD_SELECT_ALL.format(tablename=DB.tab_name))
        return [记录.uuid for 记录 in DB.return_all().zip_up().to_gview_record()]


    @staticmethod
    def 找到结点所属视图(结点编号):
        结点编号 = 结点编号.card_id if isinstance(结点编号, G.objs.LinkDataPair) else 结点编号
        DB = G.DB
        视图记录集 = DB.go(DB.table_Gview).select(DB.LIKE("nodes", 结点编号)).return_all().zip_up().to_gview_record()
        return [视图记录.to_GviewData() for 视图记录 in 视图记录集]


    @staticmethod
    def find_by_card(pairli: "List[G.safe.objs.LinkDataPair|str]") ->"Set[G.safe.configsModel.GViewData]":
        """找到卡片所属的gview记录,还要去掉重复的, 比如两张卡在同一个视图中, 只取一次 """
        DB = G.DB
        DB.go(DB.table_Gview)

        # def pair_to_gview(pair):
        #     card_id = pair.card_id if isinstance(pair,LinkDataPair) else pair
        #     DB.go(DB.table_Gview)
        #     datas = DB.select(DB.LIKE("nodes", card_id)).return_all(Utils.print).zip_up().to_gview_record()
        #     return set(map( lambda data: data.to_GviewData(), datas))

        all_records = list(map(lambda x: set(GviewOperation.找到结点所属视图(x)), pairli))
        final_givew = reduce(lambda x, y: x & y, all_records) if len(all_records) > 0 else set()

        return final_givew


    @staticmethod
    def delete(uuid: str = None, uuid_li: "Iterable[str]" = None):
        """"""
        Grapher =G.safe.linkdata_grapher.Grapher
        DB = G.DB

        def 彻底删除(视图标识):

            if 视图标识 in G.mw_gview and isinstance(G.mw_gview[视图标识], Grapher):
                视图窗口: Grapher = G.mw_gview[视图标识]
                视图窗口.close()
            [G.mw_gview[gid].remove_node(视图标识) for gid in GviewOperation.列出已打开的视图() if
             视图标识 in G.mw_gview[gid].data.gviewdata.nodes]
            视图数据 = GviewOperation.load(视图标识)
            if len(视图数据.config_model.data.appliedGview.value) == 1:
                imports.Configs.GviewConfigOperation.从数据库删除(视图数据.config)
            DB.go(DB.table_Gview)
            DB.delete(where=DB.LET(uuid=视图标识)).commit()

        if uuid:
            彻底删除(uuid)
        elif uuid_li:
            for uuid in uuid_li:
                彻底删除(uuid)
        return


    @staticmethod
    def get_correct_view_name_input(placeholder="", config:"str"=None):
        def view_name_check(name: str, placeholder="") -> bool:
            if name == "" or re.search(r"\s", name) or re.search("::::", name) \
                    or re.search("\s", "".join(name.split("::"))) or "".join(name.split("::")) == "":
                tooltip(译.视图命名规则)
                return False
            if GviewOperation.exists(name=name):
                tooltip(译.视图名已存在)
                return False
            return True
        models = G.safe.models
        数据源 = models.类型_数据源_视图创建参数()
        if config:
            configmodel = imports.Configs.GviewConfigOperation.从数据库读(config)
            数据源.配置 = models.Id_name(configmodel.name,configmodel.uuid)
        # Utils.print("数据源=",数据源)
        while True:
            模型 = models.类型_模型_视图创建参数(数据源)
            模型.创建UI().exec()
            # viewName, submitted = QInputDialog.getText(None, "input", 译.视图名, QLineEdit.Normal, placeholder)
            if not 模型.完成选择:
                break
            if 模型.数据源.视图名 == placeholder:
                模型.完成选择 = False
                break
            if view_name_check(模型.数据源.视图名, placeholder):
                break
        return 模型


    @staticmethod
    def create(nodes=None, edges=None, name="", need_save=True, need_open=True, config:"str"=None):
        """需要进行一个兼容处理, 既要满足过去的使用方式, 又要拓展到未来.
        2023年3月9日02:43:30 新版处理对象: 视图名, 是否使用已有配置
        """
        models = G.safe.models
        if not name:
            结果 = GviewOperation.get_correct_view_name_input(config=config)
            if not 结果.完成选择:
                return None
            else:
                name = 结果.视图名.值
                config = 结果.数据源.配置.ID
        uuid = UUID.by_random()
        data = G.safe.configsModel.GViewData(uuid=uuid, name=name, nodes=nodes if nodes else {}, edges=edges if edges else {}, config=config)
        # 去检查一下scene变大时,item的scene坐标是否会改变
        if need_save:
            GviewOperation.save(data)
        if need_open:
            imports.Dialogs.open_view(gviewdata=data)
        if G.GViewAdmin_window:

            win: G.safe.linkdata_grapher.GViewAdmin = G.GViewAdmin_window
            win.init_data()
        return data


    @staticmethod
    def create_from_pair(cid_li: 'list[str|G.safe.objs.LinkDataPair]', name=""):
        nodes = {}
        for cid in cid_li:
            if isinstance(cid, G.safe.objs.LinkDataPair):
                cid = cid.card_id
            nodes[cid] = GviewOperation.依参数确定视图结点数据类型模板(编号=cid)
        GviewOperation.create(nodes=nodes, edges={}, name=name)


    @staticmethod
    def choose_insert(pairs_li: 'list[G.objs.LinkDataPair]' = None):
        all_gview = GviewOperation.load_all()
        check: dict[str, G.safe.configsModel.GViewData] = {}
        list(map(lambda data: check.__setitem__(data.name, data), all_gview))
        # name_li = list()
        viewname, okPressed = QInputDialog.getItem(None, "Get gview", "", set(check.keys()), 0, False)
        if not okPressed:
            return None
        imports.Dialogs.open_grapher(pair_li=pairs_li, gviewdata=check[viewname], mode=G.safe.configsModel.GraphMode.view_mode)
        return check[viewname]


    @staticmethod
    def getDueCount(gview):
        """用于统计未复习数量"""
        g: G.safe.configsModel.GViewData = gview

        now = now = datetime.datetime.now()
        return sum(1 for i in Filter.do(Map.do([索引 for 索引 in g.nodes.keys() if G.safe.funcs.CardOperation.exists(索引)],
                                               lambda x: G.safe.funcs.CardOperation.getLastNextRev(x)),
                                        lambda due: due[1] <= now))


    @staticmethod
    def 默认元信息模板(数据=None):
        字典键名 = G.safe.baseClass.枚举命名
        默认值 = {
            字典键名.视图.创建时间: int(time.time()),
            字典键名.视图.上次访问: int(time.time()),
            字典键名.视图.上次编辑: int(time.time()),
            字典键名.视图.上次复习: int(time.time()),
            字典键名.视图.访问次数: 0
        }
        return Utils.字典缺省值填充器(默认值, 数据)


    @staticmethod
    def 默认视图边数据模板(数据=None):
        默认值 = {
            G.safe.baseClass.枚举命名.边.名称: ""
        }
        return Utils.字典缺省值填充器(默认值, 数据)


    @staticmethod
    def 依参数确定视图结点数据类型模板(结点类型=G.safe.baseClass.视图结点类型.卡片, 数据=None, 编号=None):
        models = G.safe.models

        _ = G.safe.baseClass.枚举命名
        模型 = models.类型_视图结点模型()
        默认值模板 = {}
        类型对照 = {}
        for 名字 in 模型.__dict__:
            if isinstance(模型.__dict__[名字], models.类型_视图结点属性项):
                属性: models.类型_视图结点属性项 = 模型.__dict__[名字]
                if 属性.从上级读数据:
                    默认值模板[属性.字段名] = 属性.默认值
                    类型对照[属性.字段名] = 属性.值类型
        新值 = Utils.字典缺省值填充器(默认值模板, 数据, 类型对照)
        if 编号:
            新值[_.结点.描述] = G.safe.funcs.CardOperation.desc_extract(
                编号) if 结点类型 == G.safe.baseClass.视图结点类型.卡片 else GviewOperation.获取视图名字(编号)
        新值[_.结点.数据类型] = 结点类型
        # 新值[_.结点.描述] = GviewOperation.获取视图结点描述()
        return 新值


class GrapherOperation:

    @staticmethod
    def 判断视图已经打开():
        VisualBilinker = G.safe.graphical_bilinker.VisualBilinker
        if isinstance(G.mw_grapher, VisualBilinker):
            bilinker: VisualBilinker = G.mw_grapher
            return bilinker
        else:
            return None

    @staticmethod
    def refresh():
        # from ..bilink.dialogs.linkdata_grapher import Grapher
        Grapher =G.safe.linkdata_grapher.Grapher
        if isinstance(G.mw_grapher, Grapher):
            G.mw_grapher.on_card_updated.emit(None)
        for gviewName in G.mw_gview.keys():
            if isinstance(G.mw_gview[gviewName], Grapher):
                G.mw_gview[gviewName].on_card_updated.emit(None)

    @staticmethod
    def updateDue(card_id: str):
        """当在reviewer中复习了卡片后, 在相关的领域内也要更新对应的Due"""
        # from ..bilink.dialogs.linkdata_grapher import Grapher
        Grapher = G.safe.linkdata_grapher.Grapher
        if isinstance(G.mw_grapher, Grapher):
            if card_id in G.mw_grapher.data.node_dict.keys():
                G.mw_grapher.data.updateNodeDue(card_id)

        for gviewName in G.mw_gview.keys():
            if isinstance(G.mw_gview[gviewName], Grapher):
                if card_id in G.mw_gview[gviewName].data.node_dict.keys():
                    G.mw_gview[gviewName].data.updateNodeDue(card_id)

        # return sum(filter(g.data.node_dict.keys()))

