# hjp-bilink使用介绍
- 插件版本:20200929144015 (请校对你手上获取的版本是否对应)
- [插件地址](https://gitee.com/huangjipan/hjp-bilink)
- 本插件实现在anki上简易的手动双向绑定.
- 依赖的插件代码 1423933177 ,他提供了核心的卡片单向链接功能.
- 本插件将单向链接自动化实现链过去的同时又链回来,并且提供两种链接算法.
- 讨论QQ群:891730352
- ![0nlpjS.jpg](https://s1.ax1x.com/2020/09/30/0nlpjS.jpg)
## 插件的安装
### `hjp-bilink`的安装
把文件夹`hjp-bilink`复制到anki的插件文件夹下,这个位置一般是`C:\Users\Administrator\AppData\Roaming\Anki2\addons21`
如果不知道插件文件夹在哪里,打开anki的`工具>附加组件>查看文件`也可以打开
### 依赖插件`link Cards`的安装
到`工具>附加组件>获取插件`输入1423933177  即可安装依赖插件
装完以后记得重启anki
## 使用教程
目前这个工具用起来还是有一点繁琐的,将来会加入对话框功能,简化操作.
1. ### 打开`browser`
- 就是在主界面点击`浏览/browse`弹出的那个窗口
2. ### 选取卡片记录插入txt
- 在`browser`窗口中选中几条你要双链的记录
- 点击右键,选择`hjpCopyCidAlltoTxt`,就能把你选的这几条记录的card_id插入到一个txt中
- 你可以反复执行这个过程,把所有需要的卡片ID都录入到txt中
3. ### (如果需要)打开txt编辑卡片ID,
- 在你把想双链的卡的id都插入到这个txt中后,你可以点击菜单栏上的`hjp_link>show`打开txt
- txt里面都是你在第二步操作中输入的card_id,你现在可以在每个id后面追加一个分隔符(默认是`\t`)后输入你想追加的对这个卡片ID的解释
- 你也可以不追加解释,走下一步操作.
4. ### 建立双向连接
- 选择`hjp_link`->`linkDefault`就会根据配置自动建立双向连接
- 选择`hjp_link`->`linkAll`调用完全图算法链接每个记录
- 选择`hjp_link`->`linkGroupToGroup` 调用组链接算法链接各个组的记录.
5. ### (如果需要)清除txt中的记录
- 选择`hjp_link`->`clear`就能删掉之前的全部记录.
- 其实你也可以自己打开这个文件把内容删除.

## 配置指导
配置文件名为`config.json`,可以在ANKI插件页面做修改,可以通过`hjp_link->config`打开
可修改的值
1. ### linkMode
- 链接多张卡片的算法,值为0或1,默认为0
- 0表示在txt中的每一张卡双向连接到每一张卡,
- 1表示在txt中会分成几个组,前一个组的每一张卡双向连接到后一个组的每一张卡,组与组之间用一个空的`rowSeparator`区分,默认就是空一行表示区分两个组.
2. ### rowSeparator
- 默认为"\n",表示一行一条链接,rowSeparator控制每一条记录的区分
- 也是分组的标识符,此时不能后面跟内容,直到下一个rowSeparator为止
- 标识符不能落到某条记录的内部,必须在外部
3. ### colSeparator
- colSeparator控制每一条记录中不同字段的区分,在本插件中就是卡ID与描述内容的区分,
4. ### cidPrefix
- 表示每个卡ID的默认前缀,可以为空,但如果装了最后请注意标识符在txt中的含义必须是唯一确定的,不能在插入的正文中使用标识符
5. ### appendNoteFieldPosition
- 这个属性控制双链的标记插入到anki卡片的第几个字段,取值从0开始,所以第一个字段为0,默认为2,也就是第三个字段
## 动画指导
单向链接的使用
  ![](https://www.jianguoyun.com/c/dl-file/%E6%88%90%E6%96%87%E4%BD%9C%E5%93%81/myscripts/hjp-bilink/link_addon_how_to_use_1.gif?dt=qhgbom&kv=NTY0Mjk4MzM5QHFxLmNvbQ&sd=azgih&ud=BFSfxnPc0AsG7tTyQthJw-yQBmx5wSdNmCXfP7A7nwU&vr=1) (gif图片12M)
双向链接的设置
![0n1jQf.gif](https://s1.ax1x.com/2020/09/30/0n1jQf.gif)
以上若无法显示,下方是图片的下载地址
https://www.jianguoyun.com/p/DZGFalUQ2ZDmCBjX_r8D
https://www.jianguoyun.com/p/DamL6qoQ2ZDmCBjY_r8D

## 未来计划
1. 实现unlink功能
2. 代码转移到github
3. 实现UI界面

## 更新记录
20200929144015 为了方便切换不同的链接模式,现在把两个模式直接拿到菜单中可点击了.

20200929141001 实现可修改前缀,网络化发布
