[toc]
- (本段上面有toc,不支持toc的markdown解析器请点下方链接跳转)
- [使用介绍](#1)|[更新记录](#2)|[未来计划](#3)|[安装教程](#4)|[配置教程](#5)

<a name="1"></a>
# hjp-bilink使用介绍
- ![0nlpjS.jpg](https://s1.ax1x.com/2020/09/30/0nlpjS.jpg)
- 本插件实现在anki上简易的手动双向绑定.
- 依赖的第三方插件代码 `1423933177`它提供了核心的卡片单向链接功能,
- 还有依赖插件`564851917(可选)` ,它提供了层级标签功能,这不是必须的,但有更好.
- 本插件将单向链接自动化实现链过去的同时又链回来,并且提供两种链接算法.
- 其他功能:修改连接样式,连接集体加tag,取消连接,可修改连接前缀,可定制连接描述
- 讨论QQ群:891730352
- 插件版本:0.3
- [插件地址](https://gitee.com/huangjipan/hjp-bilink)
- [anki的用法心得](https://dynalist.io/d/Ne5AAmNFNBOrJCj2BnK7Gduv) //可能需要科学上网
- ## 提醒:
    - 本插件只适用于windows和桌面linux系统,不适用于mac系统,安卓手机,iphone,ipad等移动端

<a name="2"></a>
## 更新记录
### 0.4.1
- 优化
    - 现在菜单按钮全部翻译成了中文,顾名思义会很好理解,简化上手的难度.
### 0.4
- 新增
    1. 可以在编辑界面(如`复习/review`时,点编辑,所跳出的界面,又如`浏览/browse`时,可编辑卡片的那个区域)右键点选插入卡片到`input.json`
    - [![Bt1JIK.gif](https://s1.ax1x.com/2020/10/30/Bt1JIK.gif)](https://imgchr.com/i/Bt1JIK)
        - 插入卡片的选中模式,当你选中一段文字,点击右键选择`hjp|将卡片插入input`或`hjp|将卡片插入上一个组`,会将你所选中的文字作为`desc`描述字段和ID一起插入到`input.json`
        - `hjp|将卡片插入input`和`hjp|将卡片插入上一个组`的区别,顾名思义
    2. 在编辑界面选中的文字右键点击`hjp|用选中文字更新input中的标签`,也可以将其作为`tag`的名字覆盖`input.json`中原先的`tag`
    - 这些操作能减少用户打开`input.json`编辑的次数,从而减少用户犯错造成插件崩溃的机会.
- 优化
    - 内部代码优化.
    - 改进提示的描述内容.
    - 建立链接时自动关闭`浏览/browse`,
        - 因为只要用户在浏览特定卡片,程序就无法对这个卡片进行写入操作,导致连接工作不正常.
        - 而且用户有时候会忘了不去浏览要链接的卡片,这样不如直接关掉,
        - 而且本来就需要重新打开才能看到tag 的更新,所以干脆建立连接时自动关闭.
### 0.3
- 新增
    - 新增集体加tag功能,你可以在`input.json>addTag`添加你喜欢的tag名,这样建立连接后,会给连接中的卡片集体添加`hjp-bilink::yourtagname`这样方便你从全局角度查看同一连接的全部成员.
    - [![B8c73n.gif](https://s1.ax1x.com/2020/10/29/B8c73n.gif)](https://imgchr.com/i/B8c73n)
    - 如果你没有输入tag名,那么插件会选择插入时间戳形式的tag:`hjp-bilink::YYYYMMDDHHMMSS`,
    - 这个tag默认是开启的,你可以在`config.json>addTagEnable`中关闭它(0关闭,1开启)
    - 没有提供取消tag功能,一是因为我还没想好合适的算法,二是因为批量取消tag的操作比较容易实现,不用插件也能做到,不排除将来会增加取消tag的功能.
    - 推荐安装层级标签插件`564851917`来管理标签,因为随着标签的增多如果不能层级折叠一定会越来越臃肿难看.
- 优化
    - 改进了菜单描述,现在`clear`菜单改名为`initInput`
### 0.2.2
- 优化
    - 现在`input.json`中的卡片ID可以统一处理,不再区分group或pair,每个pair都是单一的group,使用者不必在group或pair中反复横跳.
    - 现在`input.json`中的card_id在完全连接时是唯一的(尽管不唯一也不会造成重复).
    - 除非出现错误,大部分命令提示不再弹出窗口, 改为左下角静音提示.
- 新增
    - 增加style接口,你现在可以自定义链接的div样式.默认样式为空.
    - 退出时清空`input.json`
    - 增加可修改的链入和链出标记.

### 0.2.1
- 修复了一个愚蠢的错误

### 0.2
- 新增unlink取消链接，算法也是两种
- `input.txt`文本改为JSON数据,增加了易用性

### 0.1.1
- 修复了一些bug,比如重复插入卡片id

### 0.1
- 为了方便切换不同的链接模式,现在把两个模式直接拿到菜单中可点击了.
- 实现可修改前缀,网络化发布
> 注:版本号`左.中.右`三个数字分别表示 不兼容性更新,功能更新,修复改进.
<a name="3"></a>
## 未来计划
### 近期

- [ ] 增加提取tag内容和deck内容作为描述符的正则
- [ ] 实现各种方案转为tag(deck路径转tag,卡片内容转tag)
- [ ] 实现答题日志系统(点击显示答案后的任意一个按钮都会弹出是否记录日志的问号,选择是就会记录当前的文本到指定的位置.)
- [ ] 在复习,预览和编辑界面,显示右键添加到input.json(这个特别难)
### 长期
- [ ] 实现UI界面(抛弃丑陋的文本编辑,减少用户犯错几率)
- [ ] 1.0正式版,利用sqlite3,实现链接信息的外部存储,方便维护,比如链接的同步更新,实时加载(可选)
    - 将来hjp-bilink会改为用外部存储anki卡片的链接关系,不会修改卡片内容,
    - 到时候是,打开一个卡片预览,会提供一个扩展按钮,点击后弹出linklist,
    - 连接关系独立出来做的好处是,将来修改link对应的desc可以同步更新到每一张被链接的卡片上,还可以做关系图,前途很光明.
    - 为了实现这个目标,我们需要独立实现依赖的核心插件的功能,才能随心所欲地给窗口加自己的按钮,否则就要跟着别人的代码改了.
### 已完成
- [x] 实现选中文字读取为desc内容,并添加到`input.json`
- [x] 提供链接的html元素的样式修改接口
- [x] 实现input.json文件中card_id的唯一化.
- [x] 代码转移到gitee
- [x] 实现unlink功能(若选中的卡片存在link关系,则删除这个link)
- [x] 为了方便操作,将来会将卡片ID存储的`input.json`文本改为json数据({id:,desc:})

<a name="4"></a>
## 插件的安装
### 依赖插件`link Cards`和 `advanced browser` 的安装
到`工具>附加组件>获取插件` 分别输入`1423933177` , `564851917`  即可安装依赖插件

### `hjp-bilink`的安装
下载克隆这个插件仓库到本地,把文件夹`hjp-bilink`复制到anki的插件文件夹下,这个位置在windows上一般是`C:\Users\Administrator\AppData\Roaming\Anki2\addons21`
如果不知道插件文件夹在哪里,打开anki的`工具>附加组件>查看文件`也可以打开
装完以后记得重启anki

## 使用教程
目前这个工具用起来还是有一点繁琐的,将来会加入对话框功能,简化操作.
1. ### 打开`browser`
    - 就是在主界面点击`浏览/browse`弹出的那个窗口
    - ![输入图片说明](https://images.gitee.com/uploads/images/2020/1013/034448_bbf2a1fc_332584.png "屏幕截图.png")
2. ### 选取卡片记录插入`input.json`
    - 在`browser`窗口中选中几条你要双链的记录，在任何一条被选中的记录上点击鼠标右键，弹出上下文菜单，其中有
        - `hjp|将选中的卡片插入input`，
        - `hjp|将选中的卡片编组插入input`两个选项
    - ![输入图片说明](https://images.gitee.com/uploads/images/2020/1013/034558_0ef8a51b_332584.png "屏幕截图.png")
    - 根据模式不同,选择不同的选项
        1. 当你需要使用以下三种模式

            1 `完全图连接`模式, 

            2 `按结点取消连接`模式 , 

            3 `按路径取消连接`模式 时

            - 选择`hjp|将选中的卡片插入input`,就能把你选的这几条记录的`card_id`插入到`input.json`中
            - 你可以反复执行这个过程,把所有需要的卡片ID都录入到`input.json`中
        2. 当你需要使用 `组对组连接` 模式 时
            - 选择`hjp|将选中的卡片编组插入input`,把所有选中的记录作为一个组录入到`input.json`中,
            - 注意 组链接至少需要两个组才能正常工作
            - 你执行`hjp|将选中的卡片编组插入input`就是把选中的卡片编一个组插入到`input.json`中,所以想要实现链接到其他组,还得插入另一个编组.
            - 实际上你也可以对非编组的ID使用`linkGroupToGroup`,目前(0.2版之后)新增功能可实现每个卡片默认是一个组.
3. ### (如果需要)打开`input.json`编辑卡片ID和描述desc,
    - ![输入图片说明](https://images.gitee.com/uploads/images/2020/1013/035618_5e0cbe98_332584.png "屏幕截图.png")
    - 在你把想双链的卡的id都插入到这个`input.json`中后,你可以点击菜单栏上的`hjp_link>显示input`打开`input.json`
    - `input.json`里面都是你在第二步操作中输入的`card_id`还有程序默认提取的描述`desc`,你这时候可以修改默认的描述内容,你也可以不追加解释,走下一步操作.(注:0.4版后,你可以在编辑界面选中文字再右键选`hjp|将卡片插入input`,就能自动把选中的文字读取为连接的描述内容,详情看0.4更新的介绍)
    - ![0Rd6yj.png](https://s1.ax1x.com/2020/10/12/0Rd6yj.png)
4. ### 建立双向连接
    - ![输入图片说明](https://images.gitee.com/uploads/images/2020/1013/034730_38b2b795_332584.png "屏幕截图.png")
    - 选择`hjp_link>默认连接`就会根据预先在`config.json>linkMode`中配置好的链接算法,自动建立双向连接
    - 不过,如果你想使用其他模式,也可以直接点击其他模式,因为我们会经常切换加链接的方式,所以我把这些模式单列了出来:
        - 选择`hjp_link>完全图连接`,会将`input.json>IdDescPairs`中的每一张卡双向连接到每一张卡,比如输入ABC,那么A中有BC,B中有AC,C中有BA的ID链接.
        - 选择`hjp_link>组对组连接`,会在`input.json>IdDescGroups`中会分成几个组,前一个组的每一张卡双向连接到后一个组的每一张卡.比如ABC是一个组，DEF是一个组，那么组间链接就是第一组：A到DEF,B到DEF,C到DEF，第二组：D到ABC，E到ABC,F到ABC。
        - 选择`hjp_link>按结点取消连接`,相当于将`input.json>IdDescPairs`中列出的每个节点孤立，比如`input.json>IdDescPairs`中有节点A，那么程序会查询A卡片，并发现A连接到BCD，那么就会解除到BCD的链接，并且反向解除BCD到A的链接。
        - 选择`hjp_link>按路径取消连接`,相当于将`input.json>IdDescPairs`中的彼此相连的节点按顺序解除绑定，比如输入`input.json>IdDescPairs`中的ABCD是彼此有链接的节点，那么程序就会从A节点开始，从A到B解除链接，B到C解除链接以此类推，但是注意,这不会解除A到其他结点的链接,比如A连接到BCD,但是你输入`input.json>IdDescPairs`的顺序是ABCD,那么A只会解除从A到B的链接,A到CD的链接保持不动。
    
5. ### (如果需要)清除json中的记录
    - 选择`hjp_link`->`初始化input`就能删掉之前的全部记录.(0.2.2之后关闭anki能自动初始化`input.json`)
    -  **如果不熟悉json的语法,千万别自己删json的结构,最好用clear清除记录,不容易破坏json结构,否则会频繁报错.** 
    - 如果你熟悉json的语法,以上操作也可以打开`input.json`手工完成录入.
    - ![输入图片说明](https://images.gitee.com/uploads/images/2020/1013/034926_1c9e8e3d_332584.png "屏幕截图.png")
<a name="5"></a>
## 配置指导
配置文件名为`config.json`,可以在ANKI插件页面做修改,也可以通过`hjp_link->config`打开,可修改的值有
1. ### `linkMode` (重点必看)
    - `linkMode`影响默认的链接多张卡片的算法,就是你点击`hjp_link>linkDefault`时会调用的算法,值为0或1,2,3,默认为0.
    - 0表示`完全图连接`
    - 1表示`组对组连接`
    - 2表示`按结点取消连接`
    - 3表示`按路径取消连接`
4. ### `cidPrefix`
    - 表示每个卡ID的默认前缀,用于让依赖的link插件识别这是可点的链接，默认是依赖插件的默认配置即`cidd`,可以清空,请注意标识符在`input.json`中的含义必须是唯一确定的,不能在插入的正文中使用标识符.
5. ### `appendNoteFieldPosition`
    - 这个属性控制双链的标记插入到anki卡片的第几个字段,取值从0开始,所以第一个字段为0,默认为0,第一个字段通常是问题描述,也就是卡片的正面,那么双链就会插入到正面的末尾.
6. ### `readDescFieldPosition`
    - 这个属性控制程序默认从卡片的第几个字段提取卡片描述的字符，数据类型为number,默认为0,也就是提取问题描述中的前面10个非标点类字符.
7. ### `regexForDescContent`
    - 这个属性控制程序从卡片提取描述字符的方法，默认为0的话，会调用`DEFAULT>regexForDescContent`中的正则表达式来提取描述字符.如果你想按自己的正则表达式提取描述字符,可以改外层的`regexForDescContent`的值.`DEFAULT>regexForDescContent`的值就别动了.
0. ### `regexForDescFromDeck`(未完成)
0. ### `descMaxLength`(未完成)
0. ### `linkFromSymbol`,`linkToSymbol`
    - 这两个属性,一个控制链入的符号,另一个控制链出的符号. 默认是`"←"`和`"→"`,如果不需要,可以设为`""`值
    - 效果比如这个图
    - [![BYKTWd.png](https://s1.ax1x.com/2020/10/30/BYKTWd.png)](https://imgchr.com/i/BYKTWd)
    - 完全图算法全是链出符号,只有组对组连接算法有链入符号.
0. ### `linkStyle` 
    - 控制link所在的div元素的样式,默认是空字符串,即没有样式,你可以按照CSS的写法填入样式,不过注意JSON格式的回车换行问题.
0. ### `addTagEnable` ,`addTagRoot`**新增**
    - `addTagEnable`控制是否开启集体加标签功能,默认值是1,表示开启,可选0,表示关闭,
    - `addTagRoot`给所有的标签增加一个根节点,
        - 比如你在`input.json`输入的tag 是`abc`, `addTagRoot`的值为`hjp-bilink`,那么真正插入anki的tag显示为`hjp-bilink::abc`
        - 如果你安装了前文推荐的层级tag,你还可以继续在自己的tag上输入`::def`实现层级折叠,最终插入的tag是`hjp-bilink::abc::def`.
    - 你可以先不手动加标签,每次连接都会诞生一个时间戳的标签,然后事后再去整理这些时间戳的标签,只要修改标签名字即可.
    - 标签的玩法有很多种,具体可以看前面dynalist中的用法
    
## 动画指导 
- 单向链接的使用
- ![0n1jQf.gif](https://s1.ax1x.com/2020/09/30/0n1jQf.gif)
- 双向链接的设置
- ![0n3JOO.gif](https://s1.ax1x.com/2020/09/30/0n3JOO.gif)


