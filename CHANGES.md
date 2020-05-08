## aeclients Changelog

###[1.0.1b5] - 2020-5-8

#### Added 
- 修复定时任务工具类中会造成多个worker都加载定时任务的问题


###[1.0.1b4] - 2020-2-23

#### Added 
- 增加jrpc客户端单个方法请求的功能,调用形式和普通的函数调用形式一致
- 增加jrpc客户端批量方法请求的功能,调用形式类似链式调用
- 增加jrpc服务端jsonrpc子类, http和websocket的URL固定和client中的一致
- 去掉不必要的日志

#### Changed 
- 优化所有代码中没有类型标注的地方,都改为typing中的类型标注

###[1.0.1b3] - 2020-1-10

#### Changed 
- 优化dbclient中执行execute方法,如果没有返回行则返回None或者[]

###[1.0.1b2] - 2020-1-8

#### Changed 
- 优化dbclient生成新的session时如果不在binds中则创建的功能
- 优化初始化app时变量的赋值方式，使得在单独使用的是更合理

###[1.0.1b1] - 2020-1-3

#### Added 
- 默认排序增加关闭功能，在大数据量的时候为了速度可以关闭此功能
- 增加新的execute功能，新增默认关闭游标功能，返回值可以选择一条，多条或者全部

#### Changed 
- 默认分页的时候如果已经排序，直接不再排序，去掉默认组合排序的功能
- 优化上下文管理器中提交操作的时机，都移动到else中
- 修改所有的出错信息从500到400


###[1.0.0b48] - 2019-12-30

#### Added 
- 新增如果查询(分页查询)的时候没有进行排序，默认按照id关键字升序排序的功能,防止出现混乱数据
- 如果已经排序，则主键ID做为组合排序字段使用

###[1.0.0b46] - 2019-9-27

#### Changed 
- 更改session可能存在的隐藏问题
- 更改多处不必要的异常抛出，改为日志写入

###[1.0.0b45] - 2019-9-24

#### Added 
- 增加唤醒job,确保启动的apscheduler进程定时唤醒，以便能够发现其他进程添加的job而执行

#### Changed 
- 优化apscheduler启动逻辑，确保多进程中只有一个进程能启动
- 优化pascheduler启动逻辑，确保其他的进程动态添加job也能成功

###[1.0.0b43] - 2019-9-11

#### Changed 
- 更改由于session过期后再次登录删除老的session报错的问题

###[1.0.0b42] - 2019-9-10

#### Added 
- 增加新的账号登录生成session后,清除老的session的功能,保证一个账号只能一个终端登录

#### Changed 
- 更改session的过期时间为30分钟
- 更改通用数据的缓存时间为12小时
- 删除session时删除和session所有相关的缓存key

###[1.0.0b41] - 2019-9-5

#### Added 
- utils模块中增加number方法，将字符串类型转换为number类型，转换失败返回默认值


###[1.0.0b40] - 2019-9-4

#### Changed 
- 优化session的创建机制，现在的机制和flask sqlalchemy一致
- 优化创建的session在应用上下文结束后remove的机制
- 修改execute函数的实现机制，参数和SQL分开更安全,直接返回代理对象
- 修改函数get_session为gen_session

###[1.0.0b39] - 2019-9-3

#### Changed 
- 解决切换数据库时启动后第一个请求会切换失败的问题
- 解决获取session出了请求上下文后查询出错的问题

###[1.0.0b38] - 2019-8-21

#### Changed 
- 解决跨库查询时新生成的session在连接断开后再次查询会报错的问题

###[1.0.0b37] - 2019-8-20

#### Added 
- 增加利用redis解决apscheduler多进程会有多实例的解决方案

###[1.0.0b36] - 2019-8-16

#### Added 
- 增加MySQL数据库连接时设置编码的功能，默认为utf8mb4
- 增加MySQL数据库连接时防止二进制数据警告的功能

###[1.0.0b35] - 2019-8-14

#### Changed 
- 更新获取新的session后，在新的session上可以同步使用各种上下文，save等的方法

###[1.0.0b34] - 2019-7-31

#### Added 
- DBClient类中增加分表查询的gen_model方法，动态生成需要分表的model,解决分表的CRUD功能

###[1.0.0b33] - 2019-7-23

#### Added 
- DBClient类中覆盖get_binds方法，增加映射缓存功能，防止每次初始化session时重新计算

#### Changed 
- 更改dbclient中获取engine时，只有bind为None时才从g中判断和获取，这样同表不同库，不同表不同库就都满足了

###[1.0.0b32] - 2019-7-19

#### Added 
- DBClient类中增加get_session方法，并且增加缓存实例功能，解决在一个视图内部同表不同库的访问问题

###[1.0.0b31] - 2019-7-12

#### Changed 
- 更改dbclient中初始化时调用的query_class为自定义的CustomBaseQuery类

#### Added 
- dbclient模块中增加自定义的BaseQuery类，用以实现limit=0时返回所有数据的需求

###[1.0.0b30] - 2019-7-12

#### Changed 
- 更改schema valication的中文提示信息
- 更改http,mongo,mysql,redis中停止服务时会出现关闭pool报错的情况
- 更改dbclient中部分命名不规范的情况

#### Added 
- dbclient中增加session的save,save_all,delete的别名


###[1.0.0b29] - 2019-6-14

#### Added 
- 工具类中增加异步任务执行的pool_submit工具函数

###[1.0.0b28] - 2019-5-23

#### Added 
- 工具类中增加生成随机长度以字母开头的字母和数字的字符串标识

###[1.0.0b27] - 2019-5-20

#### Added 
- 增加向dbclient实例传递业务逻辑函数获取bind value的功能

###[1.0.0b26] - 2019-5-20

#### Changed 
- 修改dbclient支持绑定同表不同库的实现
- 增加了bind_name的指定
- 增加了初始化之前的钩子函数的实现
- 修改23到26版本之间遇到的测试问题

###[1.0.0b22] - 2019-5-18

#### Added 
-  增加dbclient支持绑定同表不同库的处理方式

###[1.0.0b21] - 2019-4-30

#### Changed 
-  修改mysqlclient为通用的dbclient

###[1.0.0b20] - 2019-4-29

#### Changed 
- 修改三方库的pymongo>=3.8.0,以上的版本实现了ObjectID 0.2版本规范,生成的ObjectID发生碰撞的可能行更小.

###[1.0.0b19] - 2019-4-22

#### Changed 
- 修改schema message装饰器判断错误的情况

###[1.0.0b18] - 2019-4-21

#### Added 
- 增加保存和更新hash数据时对单个键值进行保存和更新的功能
- 增加基于pymysql的简单TinyMySQL功能，用于简单操作MySQL的时候使用 
- 工具类中增加由对象名生成类名的功能
- 工具类中增加解析yaml文件的功能
- 工具类中增加返回objectid的功能

#### Changed 
- 修改获取redis数据时可能出现的没有把字符串转换为对象的情况
- 修改保存redis数据时指定是否进行dump以便进行性能的提高
- 修改获取redis数据时指定是否进行load以便进行性能的提高
- 修改Session中增加page_id和page_menu_id两个用于账户的页面权限管理

###[1.0.0b16] - 2019-3-25

#### Added 
- 修改update data中设置前缀的错误

###[1.0.0b15] - 2019-3-23

#### Added 
- 添加redis基于redis-py的同步客户端的高频使用封装

###[1.0.0b14] - 2019-3-23

#### Changed 
- 修改mongo模块使用过程中遇到的问题

###[1.0.0b13] - 2019-3-16

#### Changed 
- 优化insert document中的ID处理逻辑 
- 优化update data处理逻辑 
- 优化query key处理逻辑，可以直接使用in、like等查询


###[1.0.0b12] - 2019-1-31

#### Changed 
- 修改schema装饰器的实现

###[1.0.0b11] - 2019-1-31

#### Changed 
- 去掉调试信息

###[1.0.0b10] - 2019-1-31

#### Added 
- 增加基于元类的单例装饰器

#### Changed 
- 修改mysql client和mongo client没有请求时停止服务会报错的问题
- 修改http client为元类单例的子类，这样可以再次继承

###[1.0.0b9] - 2019-1-31

#### Changed 
- 修改mysql client实现，删除init engine方法

###[1.0.0b8] - 2019-1-31

#### Changed 
- 修改mysql client中的init engine实现，增加脚本中使用的功能
###[1.0.0b6] - 2019-1-30

#### Changed 
- 修改基于flask-sqlalchemy的mysqlclient封装的实现，由组合变继承

###[1.0.0b5] - 2019-1-29

#### Added 
- 增加基于flask-sqlalchemy的mysqlclient封装

###[1.0.0b4] - 2019-1-28

#### Added 
- 添加schema_validate装饰器用于校验schema
- 增加schema message 使用的消息
#### Changed 
- 优化exceptions的实现方式

###[1.0.0b3] - 2019-1-21

#### Added 
- 增加多数据库、多实例应用方式
- 增加在没有app时脚本中使用时的初始化功能,这样便于通用性
- 增加错误类型，能够对错误进行定制
- 增加单例的装饰器，修改httpclient为单例

###[1.0.0b2] - 2019-1-21

#### Added 
- http基于requests的CRUD封装

###[1.0.0b1] - 2019-01-21

#### Added 
- mongo基于pymongo的CRUD封装
- 所有消息可自定义配置,否则为默认配置
