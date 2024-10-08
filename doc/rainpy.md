# rainpy 简介

rainpy 是一个简单的用于科研或生产的工具包, 以科研导向为主, 兼顾生产.
这是笔者多年科研和工作中逐渐积累和完善的.
本工具倡导以包的形式进行开发,以便复用和积累, 倡导单元测试尽量覆盖, 并且能够一键测试和部署以便于环境迁移


* utils.py 中包含常见的工具集，包括读取各类数据文件, 网络请求等
* test_instances.py 中包含各种常见测试集(.json, .jsonl, .csv, .pkl等) 的处理方法,核心思路是复用常见的处理工作工作, 以专注于工作本身
* raindrop 包含常见工程的初始化方法, 包括web项目和常用非web项目. 针对vscode环境进行设计,能够基本满足生产需求,但仍需较大改进
* core 中包括各类核心方法


## doc

### read(file_path, **kwarg)
读取数据, 
尽量兼容各种编码和格式
首先判断文件情况, 继而尝试读取, 后续计划采用多种方式.

* Pandas 适用于 较小的数据集。
* Dask 适用于 较大的数据集和并行计算的场景。
* Vaex 适用于超大规模的数据集。

500M以下, 且内存充足直接读取, 可设置
(0, 10G] 以内, pandas, 可设置
(10, 100G] 以内, dask, 可设置
100G 以上用vaex



### save(file_path, **kwarg)
写入数据


### read(file_path, **kwarg)




# example: 
```python
for x in get_files("dataset/xx.jsonl"):
    dataset = read(x, pandas=1)
    for x in dataset.to_dict('records'):
        save("re/xx.jsonl", x, mode='a')
        print(x['prompt'])
```

