# rainpy 简介

rainpy 是一个简单的用于科研或生产的工具包, 以科研导向为主, 兼顾生产.
这是笔者多年科研和工作中逐渐积累和完善的.
本工具倡导以包的形式进行开发,以便复用和积累.
计划每年发包两次, 分别是六月份和十二月份

* utils.py 中包含常见的工具集，包括读取各类数据文件, 网络请求等
* test_instances.py 中包含各种常见测试集(.json, .jsonl, .csv, .pkl等) 的处理方法,核心思路是复用常见的处理工作工作, 以专注于工作本身
* raindrop 包含常见工程的初始化方法, 包括web项目和常用非web项目. 针对vscode环境进行设计,能够基本满足生产需求,但仍需较大改进
* core 中包括各类核心方法