from .basic_funcs import *

class 全局配置操作:
    @staticmethod
    def 表格行数据装载(行数据模型:"G.safe.models.基类_模型_所有的表格行模型",数据来源:"dict"):
        for 键,值 in 行数据模型.属性字典.items():
            if 键 in 数据来源:
                行数据模型.属性字典[键].设值(数据来源[键])

    @staticmethod
    def 表格型属性项设值(表格属性项:"G.safe.models.基类_属性项",行数据模型:"G.safe.models.基类_模型_所有的表格行模型",数据来源:"list[dict]|dict"):
        """
            用于给表格属性项设值
            执行的思路: 当你要添加值的时候, 你要判断添加的是一行值还是一个新的列表, 分别处理
            需要对行数据模型做个打包的模型
            先完成格式检查
        """
        if type(数据来源)==list:
            全局配置操作.表格行数据装载()


        pass

    @staticmethod
    def 装饰器_属性项_赋值检查(设值函数):
        def 内包函数(self:"G.safe.models.基类_属性项",value):
            预定类型 = G.safe.baseClass.枚举命名.值类型.具备默认校验函数的类型
            可赋值 = True
            if self.有校验:
                可赋值 = 可赋值 and self.函数_赋值校验(self,value)
            elif self.值类型 in 预定类型:
                pass
            else:
                raise ValueError("")
            设值函数(self,value)
            pass


class BaseConfig(metaclass=abc.ABCMeta):
    """一切配置表的基类
    TODO 把Config中可以抽象的功能提升到这里来
    """

    @staticmethod
    def get_validate(item: G.safe.configsModel.ConfigModelItem):
        ConfigModel = G.safe.configsModel.ConfigModel
        w = ConfigModel.Widget
        d = {  # 不写在这的必须要有自己的validate
            w.spin: lambda x, itemSelf: type(x) == int and itemSelf.limit[0] <= x <= itemSelf.limit[1],
            w.radio: lambda x, itemSelf: type(x) == bool,
            w.line: lambda x, itemSelf: type(x) == str,
            w.label: lambda x, itemSelf: type(x) == str,
            w.text: lambda x, itemSelf: type(x) == str,
            w.combo: lambda x, itemSelf: x in itemSelf.limit,
            w.customize: lambda x, itemSelf: True
        }

        if item.validate(item.value, item) is None:
            # write_to_log_file(str(item.validate(item.value, item)))
            return d[item.component]
        else:
            return item.validate

    @staticmethod
    def makeConfigRow(配置项名, 配置项: G.safe.configsModel.ConfigModelItem, 上级: G.safe.widgets.组件定制.配置表容器):
        """这里制作配置表中的每一项"""
        ConfigModel = G.safe.configsModel.ConfigModel
        value, validate, widgetType = 配置项.value, 配置项.validate, 配置项.component
        typ = ConfigModel.Widget
        tipbutton = QToolButton()
        tipbutton.setIcon(QIcon(G.src.ImgDir.help))
        tipbutton.clicked.connect(lambda: Utils.大文本提示框("<br>".join(配置项.instruction)))
        container = QWidget(parent=上级)
        layout = QHBoxLayout()
        w = None
        if widgetType == typ.spin:
            w = QSpinBox(container)
            w.setRange(配置项.limit[0], 配置项.limit[1])
            w.setValue(value)
            w.valueChanged.connect(lambda x: 配置项.setValue(x))
            配置项.设值到组件 = lambda 值: w.setValue(值)
        elif widgetType == typ.line:
            w = QLineEdit()
            w.setText(value)
            w.textChanged.connect(lambda: 配置项.setValue(w.text()))
            配置项.设值到组件 = lambda 值: w.setText(值)
        elif widgetType == typ.combo:
            w = QComboBox(container)
            list(map(lambda x: w.addItem(x.name, x.value), 配置项.limit))
            w.setCurrentIndex(w.findData(value))
            w.currentIndexChanged.connect(lambda x: 配置项.setValue(w.currentData(role=Qt.ItemDataRole.UserRole)))
            配置项.设值到组件 = lambda 值: w.setCurrentIndex(w.findData(值))
        elif widgetType == typ.radio:
            w = QRadioButton(container)
            w.setChecked(value)
            w.clicked.connect(lambda: 配置项.setValue(w.isChecked()))
            配置项.设值到组件 = lambda 值: w.setChecked(值)
        elif widgetType == typ.label:
            w = QLabel(container)
            w.setText(配置项.display(value))
            配置项.设值到组件 = lambda 值: w.setText(值)
        elif widgetType == typ.text:
            w = QTextEdit(container)
            w.setContentsMargins(0, 0, 0, 0)
            w.setText(value)
            配置项.设值到组件 = lambda 值: w.setText(值)
        elif widgetType == typ.customize:
            x2 = 配置项.customizeComponent()(配置项, 上级)  # 这个地方的警告去不掉, 很烦人.
            配置项.设值到组件 = lambda 值: x2.SetupData(值)
            w = x2.View
        else:
            raise ValueError(f"配置项:{配置项名},未知组件方案")
        配置项.widget = w
        layout.addWidget(w)
        layout.addWidget(tipbutton)
        container.setLayout(layout)
        return container

    @staticmethod
    def makeConfigDialog(调用者, 数据: G.safe.configsModel.BaseConfigModel, 关闭时回调: Callable[[G.safe.configsModel.BaseConfigModel],None] = None):
        """
        关闭时回调
        TODO:这里的内容要整理到Config的父类中
        onclose 接受一个高阶函数: Callable[cfg,Callable[]] 这个高阶函数的参数是本函数的第一个参数cfg
        """

        # from .configsModel import BaseConfigModel
        # print(f"in makeConfigDialog data={数据}")
        @dataclasses.dataclass()
        class 分页字典项:
            widget: QWidget = dataclasses.field(default_factory=QWidget)
            layout: QFormLayout = dataclasses.field(default_factory=QFormLayout)

        ConfigModel = G.safe.configsModel.ConfigModel

        容器 = G.safe.widgets.组件定制.配置表容器(数据, 调用者=调用者)

        总布局 = QVBoxLayout()
        分栏 = QTabWidget()

        分栏字典: "dict[Any,分页字典项]" = {}
        for 名, 值 in 数据.get_editable_config().items():
            if 值.component == ConfigModel.Widget.none:
                continue
            if 值.tab_at not in 分栏字典:
                分栏字典[值.tab_at]: '分页字典项' = 分页字典项()
            item = BaseConfig.makeConfigRow(名, 值, 容器)
            分栏字典[值.tab_at].layout.addRow(language.rosetta(名), item)
        for 名, 值 in 分栏字典.items():
            值.widget.setLayout(值.layout)
            分栏.addTab(值.widget, 名)
        滚动组件 = QScrollArea(容器)
        滚动组件.setWidget(分栏)
        滚动组件.setContentsMargins(0, 0, 0, 0)
        滚动组件.setMinimumHeight(500)
        滚动组件.setWidgetResizable(True)
        滚动组件.setAlignment(Qt.AlignmentFlag.AlignCenter)
        总布局.addWidget(滚动组件, stretch=1)
        容器.setLayout(总布局)
        # 容器.resize(int(分栏.width() * 1.1), 500)
        容器.setContentsMargins(0, 0, 0, 0)
        容器.setWindowIcon(QIcon(G.src.ImgDir.config))
        容器.setWindowTitle("配置表/configuration")
        if 关闭时回调:
            容器.rejected.connect(lambda: 关闭时回调(数据))

        return 容器


class Config(BaseConfig):
    """TODO 这里需要抽象出一个父类, 实现widget继承"""

    @staticmethod
    def read(cfg: G.safe.configsModel.ConfigModel, data: "dict"):
        for key, value in data.items():
            if key in cfg.get_editable_config():
                item: "G.safe.configsModel.ConfigModelItem" = cfg[key]
                # if not validate_dict[item.component](value,item):
                if not Config.get_validate(item)(value, item):
                    showInfo(f"{key}={value}<br>is invalid, overwritten")
                    # write_to_log_file(f"{key}={value}\n"+str(Config.get_validate(item)(value,item)),need_timestamp=True)
                    continue
                cfg[key].value = value

    @staticmethod
    def get() -> G.safe.configsModel.ConfigModel:
        """静态方法,直接调用即可"""
        if G.CONFIG is None:
            template = G.safe.configsModel.ConfigModel()
            if os.path.exists(G.src.path.userconfig):
                file_str = open(G.src.path.userconfig, "r", encoding="utf-8").read()
            else:
                file_str = template.to_json_string()
            try:
                data = json.loads(file_str)
                Config.read(template, data)
                G.CONFIG = template
            except:
                backfile = Utils.make_backup_file_name(G.src.path.userconfig)
                if os.path.exists(G.src.path.userconfig):
                    shutil.copy(G.src.path.userconfig, backfile)
                    showInfo(f"config file load failed, backup and overwrite")
                Config.save(template)

        return G.CONFIG

    @staticmethod
    def save(config: G.safe.configsModel.ConfigModel = None, path=None):
        # showInfo("Config.save")
        ConfigModel = G.safe.configsModel.ConfigModel
        if path is None: path = G.src.path.userconfig
        if config is None: config = ConfigModel()
        template = ConfigModel()
        Config.read(template, config.get_dict())
        template.save_to_file(path)
        G.CONFIG = template


class GviewConfigOperation(BaseConfig):

    @staticmethod
    def 获取全部配置表字典():
        DB = G.DB
        DB.go(DB.table_GviewConfig)
        result: "list[dict]" = [row for row in DB.selectAll().return_all().zip_up()]
        return result

    @staticmethod
    def 获取结点角色数据源(gview_uuid=None, gview_data: G.safe.configsModel.GViewData = None) -> "list[str]":

        if gview_uuid:
            data = 导入.Gview.Gview.load(gview_uuid)
        else:
            data = gview_data
        if data.config:
            from ast import literal_eval
            role_enum = literal_eval(G.objs.Record.GviewConfig.readModelFromDB(data.config).data.node_role_list.value)
            return role_enum
        else:
            return []

    @staticmethod
    def 获取结点角色名(视图数据: "G.safe.configsModel.GViewData", 结点编号,
                       配置数据: "G.safe.configsModel.GviewConfig" = None):
        角色选中序号表 = 视图数据.nodes[结点编号].角色.值
        角色列表 = eval(
            (GviewConfigOperation.从数据库读(视图数据.config) if not 配置数据 else 配置数据).data.node_role_list.value)
        return [角色列表[角色序号] for 角色序号 in 角色选中序号表 if 角色序号 in range(0, len(角色列表))]

    @staticmethod
    def 漫游路径生成之深度优先遍历(视图数据: G.safe.configsModel.GViewData, 结点队列: "list[str]", 起点: "list[str]"):
        Utils.print("深度优先排序开始")
        栈 = []
        结点集 = set(结点队列)
        已访问 = []
        边集 = 视图数据.edges.keys()
        while 结点集:
            if not 栈:
                栈.append(结点集.pop() if not 起点 else 起点.pop(0))
            while 栈:
                结点 = 栈.pop()
                已访问.append(结点)
                结点为起点的边集 = [边 for 边 in 边集 if 边.startswith(结点)]
                for 边 in 结点为起点的边集:
                    终点 = 边.split(",")[1]
                    if 终点 not in 已访问 and 终点 not in 栈:
                        栈.append(终点)
            结点集 -= set(已访问)
        return 已访问
        pass

    @staticmethod
    def 漫游路径生成之广度优先遍历(视图数据: G.safe.configsModel.GViewData, 结点队列: "list[str]", 起点: "list[str]"):
        队 = []
        结点集 = set(结点队列)
        已访问 = []
        边集 = 视图数据.edges.keys()
        while 结点集:
            if not 队:
                队.insert(0, 结点集.pop() if not 起点 else 起点.pop(0))
            while 队:
                结点 = 队.pop()
                已访问.append(结点)
                结点为起点的边集 = [边 for 边 in 边集 if 边.startswith(结点)]
                for 边 in 结点为起点的边集:
                    终点 = 边.split(",")[1]
                    if 终点 not in 已访问 and 终点 not in 队:
                        队.insert(0, 终点)

            结点集 -= set(已访问)
        return 已访问
        pass

    @staticmethod
    def 漫游路径生成之多级排序(前一项, 后一项, 视图数据: G.safe.configsModel.GViewData,
                               排序表: "List[Iterable[str,str]]"):
        """默认升序排序,默认的比较是 前一项>后一项"""
        前一项结点数据, 后一项结点数据 = 视图数据.nodes[前一项], 视图数据.nodes[后一项]
        _ = G.safe.baseClass.枚举命名
        for 排序字段, 升降序 in 排序表:
            if 前一项结点数据[排序字段].值 == 后一项结点数据[排序字段].值:
                continue
            else:
                return (前一项结点数据[排序字段].值 - 后一项结点数据[排序字段].值) * (1 if 升降序 == _.上升 else -1)
        return 0
        pass

    @staticmethod
    def 漫游路径生成之加权排序(前一项, 后一项, 视图数据: G.safe.configsModel.GViewData, 排序公式):
        return eval(排序公式, *GviewConfigOperation.获取eval可用变量与函数(视图数据, 前一项)) - eval(排序公式,
                                                                                                     *GviewConfigOperation.获取eval可用变量与函数(
                                                                                                         视图数据,
                                                                                                         后一项))

    @staticmethod
    def 漫游路径生成(视图数据: G.safe.configsModel.GViewData, 配置数据: G.objs.Record.GviewConfig, 队列: "list[str]",
                     选中队列=None):
        字典键名 = G.safe.baseClass.枚举命名
        _ = 字典键名.路径生成模式

        if not 视图数据.config:
            raise ValueError('config is None')
        生成模式 = 配置数据.data.roaming_path_mode.value
        if 生成模式 == _.随机排序:
            random.shuffle(队列)
            return 队列
        elif 生成模式 == _.多级排序:
            待选表, 选中序号 = 配置数据.data.cascading_sort.value
            if 选中序号 >= len(待选表):
                选中序号 = -1
                配置数据.data.cascading_sort.value[1] = -1

            排序表: "List[Iterable[str,str]]" = eval(待选表[选中序号]) if len(
                待选表) > 选中序号 >= 0 else G.safe.baseClass.漫游预设.默认多级排序规则
            队列.sort(key=cmp_to_key(lambda x, y: GviewConfigOperation.漫游路径生成之多级排序(x, y, 视图数据, 排序表)))
            return 队列
        elif 生成模式 == _.加权排序:
            待选表, 选中序号 = 配置数据.data.weighted_sort.value
            if 选中序号 >= len(待选表):
                选中序号 = -1
                配置数据.data.weighted_sort.value[1] = -1

            公式 = 待选表[选中序号] if len(待选表) > 选中序号 >= 0 else G.safe.baseClass.漫游预设.默认加权排序规则
            队列.sort(key=cmp_to_key(lambda x, y: GviewConfigOperation.漫游路径生成之加权排序(x, y, 视图数据, 公式)),
                      reverse=True)
            return 队列
        else:
            图排序模式 = 配置数据.data.graph_sort.value
            入度零结点 = [结点编号 for 结点编号 in 队列 if 视图数据.nodes[结点编号].入度.值 == 0]
            开始结点 = 入度零结点 if 入度零结点 else [random.choice(队列)]
            if 配置数据.data.roamingStart.value == 字典键名.视图配置.roamingStart.手动选择卡片开始:
                可能的开始结点 = [结点编号 for 结点编号 in 队列 if 视图数据.nodes[结点编号].漫游起点.值]
                if len(可能的开始结点) > 0:
                    开始结点 = 可能的开始结点 + 开始结点
                if 选中队列:
                    开始结点 = 选中队列 + 开始结点
                Utils.print("开始结点={开始结点}".format(开始结点=开始结点))
            if 图排序模式 == 字典键名.视图配置.图排序模式.广度优先遍历:
                return GviewConfigOperation.漫游路径生成之广度优先遍历(视图数据, 队列, 开始结点)
            else:
                return GviewConfigOperation.漫游路径生成之深度优先遍历(视图数据, 队列, 开始结点)

    @staticmethod
    def 满足过滤条件(视图数据: G.safe.configsModel.GViewData, 结点编号: "str", 配置数据: G.objs.Record.GviewConfig):
        """传到这里的参数, 必须满足视图数据.config存在"""
        if not 视图数据.config:
            raise ValueError('config is None')
        列表, 选项 = 配置数据.data.roaming_node_filter.value

        if 选项 >= len(列表):
            配置数据.data.roaming_node_filter.value[1] = 选项 = -1

        结点数据 = 视图数据.nodes[结点编号]
        if 结点数据.必须复习.值:
            return True
        elif not 结点数据.需要复习.值:
            return False
        elif 选项 == -1:
            默认过滤条件 = G.safe.baseClass.漫游预设.默认过滤规则
            全局, 局部 = GviewConfigOperation.获取eval可用变量与函数(视图数据, 结点编号)
            return eval(默认过滤条件, 全局, 局部)
        else:
            return eval(列表[选项], *GviewConfigOperation.获取eval可用变量与函数(视图数据, 结点编号))
        pass

    @staticmethod
    def 获取eval可用变量与函数的说明(指定变量类型=None):
        models = G.safe.models

        说明 = f"<h1>{译.可用变量与函数}</h1>"

        结点属性模型 = models.类型_视图结点模型()
        视图属性模型 = models.类型_视图本身模型()

        _ = G.safe.baseClass.枚举命名
        for 属性名 in 结点属性模型.获取可访变量(指定变量类型).keys():
            说明 += fr"<p><b>{属性名}</b>,{结点属性模型[属性名].变量使用的解释()}</p>"
        for 属性名 in 视图属性模型.获取可访变量(指定变量类型).keys():
            说明 += fr"<p><b>{属性名}</b>,{视图属性模型[属性名].变量使用的解释()}</p>"
        说明 += f"<p><b>{_.视图配置.结点角色表}</b>,mean:{译.角色待选列表},type:list,example:['apple','banana']</p>"
        说明 += f"<p><b>time_xxxx</b>,{译.所有time开头的变量都是时间戳}:{', '.join([_.时间.今日, _.时间.昨日, _.时间.上周, _.时间.本周, _.时间.一个月前, _.时间.本月, _.时间.三天前, _.时间.三个月前, _.时间.六个月前])}</p>"
        说明 += f"<p><b>{_.时间.转时间戳}</b>,example:to_timestamp('2023-2-18')->1676649600</p>"
        说明 += f"<p><b>supported python module:</b> math,random,re</p>"
        return BeautifulSoup(说明, "html.parser").__str__()

    @staticmethod
    def 获取eval可用函数():
        _ = G.safe.baseClass.枚举命名.时间
        return {
            _.转时间戳: Utils.日期转时间戳,
            _.今日: Utils.时间处理.今日(),
            _.昨日: Utils.时间处理.昨日(),
            _.上周: Utils.时间处理.上周(),
            _.本周: Utils.时间处理.本周(),
            _.一个月前: Utils.时间处理.一个月前(),
            _.本月: Utils.时间处理.本月(),
            _.三天前: Utils.时间处理.三天前(),
            _.三个月前: Utils.时间处理.三个月前(),
            _.六个月前: Utils.时间处理.六个月前(),
        }

    @staticmethod
    def 获取eval可用字面量(指定变量类型=None):
        # from . import models
        return {**G.safe.models.类型_视图本身模型().获取可访字面量(指定变量类型=指定变量类型),
                **G.safe.models.类型_视图结点模型().获取可访字面量(指定变量类型=指定变量类型)}
        pass

    @staticmethod
    def 获取eval可用变量与函数(视图数据: G.safe.configsModel.GViewData = None, 结点索引=None, 指定变量类型=None):
        """"""
        # from . import models
        _ = G.safe.baseClass.枚举命名
        new_globals = globals().copy()
        结点变量 = (G.safe.models.类型_视图结点模型().获取可访变量(指定变量类型=指定变量类型) if not 视图数据 else
                    视图数据.nodes[结点索引].获取可访变量(指定变量类型=指定变量类型))
        视图变量 = (G.safe.models.类型_视图本身模型().获取可访变量(
            指定变量类型=指定变量类型) if not 视图数据 else 视图数据.meta_helper.获取可访变量(
            指定变量类型=指定变量类型))
        配置变量 = eval(GviewConfigOperation.从数据库读(
            视图数据.config).data.node_role_list.value) if 视图数据 and 视图数据.config else []
        函数变量 = GviewConfigOperation.获取eval可用函数()
        变量对儿 = [new_globals,
                    {
                        **结点变量,
                        **视图变量,
                        **函数变量,
                        _.视图配置.结点角色表: 配置变量
                    }
                    ]
        return 变量对儿

    @staticmethod
    def 从数据库读(标识):
        return G.objs.Record.GviewConfig.readModelFromDB(标识)

    @staticmethod
    def 从数据库删除(标识: str):
        if type(标识) != str:
            raise ValueError("类型不匹配")
        DB = G.DB
        DB.go(DB.table_GviewConfig)
        DB.excute_queue.append(f"delete from GRAPH_VIEW_CONFIG where uuid='{标识}'")
        DB.commit(lambda x: Utils.print(x, need_logFile=True))
        # G.DB.go(G.DB.table_GviewConfig).delete(objs.Logic.EQ(uuid=f"'{标识}'")).commit(lambda x:Utils.print(x,need_logFile=True))

    @staticmethod
    def 存在(标识):
        if not 标识:
            return False
        DB = G.DB
        return DB.go(DB.table_GviewConfig).exists(DB.EQ(uuid=标识))

    @staticmethod
    def 指定视图配置(视图记录: "G.safe.configsModel.GViewData | str",
                     新配置记录: "G.objs.Record.GviewConfig|str|None" = None, need_save=True, 视图初始化中=False):
        """如果是从 grapher 中打开的，最好直接读取视图记录本身 而非编号"""
        DB = G.DB
        # def 清空无效配置():
        #     空集: List[G.objs.Record.GviewConfig] = DB.go(DB.table_GviewConfig).select(
        #         DB.LIKE("data", '"appliedGview": [], "node_role_list"')) \
        #         .return_all().zip_up().to_givenformat_data(G.objs.Record.GviewConfig, multiArgs=True)
        #     # Utils.print(空集)
        #     for 配置 in 空集:
        #         配置.从数据库中删除()
        # def 清空视图之前对应的配置(视图数据:G.safe.configsModel.GViewData):
        #
        #     配置集:List[G.objs.Record.GviewConfig] = DB.go(DB.table_GviewConfig).select(DB.LIKE("data",视图数据.uuid))\
        #         .return_all().zip_up().to_givenformat_data(G.objs.Record.GviewConfig, multiArgs=True)
        #     for 配置 in 配置集:
        #         配置.删除一个支配视图(视图数据.uuid)
        #         if 配置.data.appliedGview.value:
        #             配置.saveModelToDB()
        #         else:
        #             配置.从数据库中删除()



        if 新配置记录 is None:
            新配置记录 = G.objs.Record.GviewConfig()
        elif type(新配置记录) == str:
            新配置记录 = G.objs.Record.GviewConfig.readModelFromDB(新配置记录)
        新配置记录.指定视图配置(视图记录)


        return 新配置记录

    @staticmethod
    def 移除视图配置(视图标识: "str", 配置标识: "str"):
        视图模型 = 导入.Gview.GviewOperation.load(uuid=视图标识)
        视图模型.config = ""
        导入.Gview.GviewOperation.save(视图模型)

    @staticmethod
    def 据关键词同时搜索视图与配置数据库表(关键词: "str") -> "list[tuple[str,str,str]]":
        """返回一个列表,里面是[类型,名称,uuid]三元组
        """

        G.DB.go(G.DB.table_GviewConfig).excute_queue.append(f"""
        select "{译.视图}",name,uuid from GRAPH_VIEW_TABLE  where name like "%{关键词}%" and config != ""
        union 
        select "{译.配置}",name,uuid from GRAPH_VIEW_CONFIG where name like "%{关键词}%"
        order by name
        """)
        result = G.DB.commit()
        return list(result)
