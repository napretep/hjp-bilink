# 数据迁移/data migration
1. ## 为什么需要数据迁移/why need data migration
   最初, 本插件设计为将链接信息存储到卡片字段中,
   
   但是这样的设计引起了与其他插件的不兼容问题, 因为其他插件对卡片字段的修改, 会破坏本插件所存储的链接信息, 甚至导致卡片无法读取.

   所以, 后来为了与其他插件相兼容, 本插件增加了多种存储方式, 分别是
   1. 卡片字段存储
   2. sqlite 数据库存储
   3. JSON文件存储
   
   每种存储方式各有优劣, 并且还提供了彼此迁移的小工具
   
   本插件默认使用sqlite 数据库存储链接信息

   Originally, this addon was designed to store link information in card fields.

   However, this design causes incompatibilities with other addons, because other addons modify the field of the card, which can break the link information stored by shis addons, or even make the card unreadable.

   Therefore, in order to be compatible with other addons, this addon has added a variety of storage methods, they are 
   1. Card field storage

   2. SQLite database storage

   3. JSON file storage

    This addon uses SQLite database to store link information by default

2. ## 不同存储方式的优劣/The advantages and disadvantages of different storage methods
   1. Card field storage
      - 优势/advantages
        - 链接信息伴随卡片同步,无需手动备份./Link information is synchronized with the card, eliminating the need for manual backups.
      - 劣势/disadvantages
        - 与其它会修改卡片字段的插件兼容不良,容易导致anki崩溃 /Incompatible with other addons that will modify card fields, causing Anki to crash

   2. SQLite database storage
      - 优势/advantages
        - 不会受其他插件的干扰./No interference from other addons
        - 性能比较好/It has good performance
      - 劣势/disadvantages
        - 需要自己同步和备份数据,以避免遗失/You need to synchronize your backup data to avoid loss 
        - 需要一些数据库知识才能直接修改文件/Some database knowledge is required to modify files directly
   3. JSON file storage
      - 优势/advantages
        - 不会受其他插件的干扰./No interference from other addons
        - 储存为文本文件,可直接查看和修改./Store as a text file that can be viewed and modified directly.
      - 劣势/disadvantages
        - 需要自己同步和备份数据,以避免遗失/You need to synchronize your backup data to avoid loss 
        - 如果链接的数据量巨大,可能会存在性能问题./If the amount of link data is large, there may be performance issues.
3. ## 如何进行数据迁移/how to data migration
   1. 将需要迁移的卡片插入到input中/Insert the cards that need to be migrated into the input
   2. 打开迁移对话框并执行/Open the Migration dialog then execute
    ![](https://z3.ax1x.com/2021/05/16/gg3adO.png)
    ![](https://z3.ax1x.com/2021/05/16/ggGmUU.png)
