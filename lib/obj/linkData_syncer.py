"""
同步设计.
"""
import json


class DataSyncer:
    """
    操作说明: 如果初始化的参数是string,就会调用json.loads,如果是dict或list,就会直接赋值.
    这个类的目的是对对象进行数据同步.
    """

    def __init__(self, data):
        if type(data) == str:
            self.data = json.loads(data)
        elif type(data) in [list, dict]:
            self.data = data
        self.link_list = self.data["link_list"]
        self.root = self.data["root"]
        self.node = self.data["node"]

    def node_data_update(self):
        """将groupinfo更新为node,保存两种东西,1是list,2是dict"""
        # 先把卡片内容加上
        link_list, root, node = self.link_list, self.root, self.node
        for item in link_list:
            node[item["card_id"]] = item
        # 把groupinfo中,如果是值为列表的键,就检查他的列表每一项是否为指定的类型.
        for k, v in node.items():
            if type(v) == list:  # 说明是非终端节点 nonterminal node
                new_li = []
                for i in range(len(v)):
                    if type(v[i]) != dict:  # 如果不是字典,那很可能仅仅是字符串
                        new_li.append({"card_id": v[i]})
                if len(new_li) > 0:
                    node[k] = new_li
        for i in range(len(root)):  # root中的表达形式要改变.
            if "type" in root[i]:
                if root[i]["type"] == "cardinfo":
                    root[i] = {"card_id": root[i]["card_id"]}
                elif root[i]["type"] == "groupinfo":
                    root[i] = {"nodename": root[i]["groupname"]}
        self.link_list = link_list
        self.root = root
        self.node = node

    def data_sync_update(self):
        """数据同步的更新
        1,如果linklist是空的, 那么就全部置空.
        2,如果root是空的,那就填入linklist的内容,并且把node置空
        3,如果root,linklist都不是空的,那么把linklist中有但root中无的,填入root,把root中有但linklist中无的,从root中删除.
        """
        if self.link_list == []:
            self.root = []
            self.node = {}
        elif self.root == []:
            self.node = {}
            for item in self.link_list:
                self.root.append({"card_id": item["card_id"]})
        else:
            # 根据情况3来设计流程. 先制作一个插入表,后制作一个剔除表
            linkset = set([i["card_id"] for i in self.link_list])
            rootset = set([i["card_id"] for i in filter(lambda x: "card_id" in x, self.root)])

            addset = linkset - rootset
            delset = rootset - linkset
            for i in delset:
                self.root.remove({"card_id": i})
            for k, v in self.node.items():
                if type(v) == list:
                    nodeset = set([i["card_id"] for i in filter(lambda x: "card_id" in x, v)])
                    node_del_set = nodeset - linkset
                    addset -= nodeset
                    for i in node_del_set:
                        k.remove({"card_id": i})
            for i in addset:
                self.root.append({"card_id": i})

    def sync(self):
        """更新一些内容,把旧的锚点更新过来"""
        self.node_data_update()
        self.data_sync_update()
        self.node_data_update()
        self.data["link_list"] = self.link_list
        self.data["root"] = self.root
        self.data["node"] = self.node
        return self

    def remove_leaves(self):
        newdict = {}
        for i in filter(lambda x: type(x[1]) != dict and "card_id" not in x[1], self.data["node"].items()):
            newdict[i[0]] = i[1]
        self.data["node"] = newdict
        return self


datastr = """{"version": 1,
"self_data": {"card_id": "1234567", "desc": "334455"},
"link_list":
    [{"card_id": "1618912345046", "desc": "B", "dir": "→"},
    {"card_id": "1618912351734", "desc": "D", "dir": "→"},
    {"card_id": "1618912346117", "desc": "C", "dir": "→"}],
"root": [{"card_id": "1618912345046"}, {"nodename": "new_group"}],
"node":
    {"new_group": [{"card_id": "1618912351734"}, {"card_id": "1618912346117"}],
    "1618912345046": {"card_id": "1618912345046", "desc": "B", "dir": "→"},
    "1618912351734": {"card_id": "1618912351734", "desc": "D", "dir": "→"},
    "1618912346117": {"card_id": "1618912346117", "desc": "C", "dir": "→"}}}"""

if __name__ == '__main__':
    data = DataSyncer(datastr).sync().data
    print(data)
