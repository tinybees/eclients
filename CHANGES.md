## aeclients Changelog

###[1.0.0b4] - 2019-1-28

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
