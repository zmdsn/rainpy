# rainpy_ts 
rainpy_ts 是用于时序数据处理的包, 包括时序数据预处理工具以及各种时序预测算法的二次集成.




statsmodels 提供传统统计模型
Prophet 专为节假日、趋势和季节性建模设计
sktime 机器学习库的时序扩展
TensorFlow 支持复杂模型（如 LSTM、Transformer、Attention）。
TSForecast / BATS/Theta-Forecasting 专精于高频率数据(
    如分钟级传感器数据), 提供自动化的模型选择和超参数优化。


TensorFlow 比较复杂, 如果我的工作不需要使用这个功能, 如何设计python包, 使得安装rainpy 的时候不安装tensorflow. 同时若需要的话又可以安装


基于pandas
规则: 分析各字段的数据类型, 然后自动设置时间字段为index
* 名字
* 可转化为datetime类型
* 高唯一性
* 时间戳值范围检查


