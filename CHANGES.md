## aeclients Changelog

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
