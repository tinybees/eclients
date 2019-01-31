## aeclients Changelog

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
