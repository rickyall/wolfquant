# futuretrader
基于上期接口开发的交易系统，使用语言python3.6，环境linux64/ubuntu
# 使用
```
3)使用案例
```python

# 通过以下方式使用期货版API
>>>from ctp import ApiStruct, MdApi, TraderApi

```

4）目录结构
* doc：内容包含上期接口的相关开发文档
* docker: docker运行文件相关的内容
* example:一些使用接口的案例
* lib:上期接口的封装文件，参考pyctp
* core:基于封装的二次接口开发，内容涉及行情、交易信息的连接。
  * config: 配置信息
  * data: 行情数据
  * my: 交易的连接


# 路线图
### 0.0.0
* 实现了期货python版的交易接接口（完成）
* 基于python交易接口的二次封装
* 整理交易接口的使用文档
