| 参数含义 | 长命令 | 短命令 | 必选 | 默认值 | 输入域 |
| --- | --- | --- | --- | --- | --- |
| 标准模型路径 | --gold | -G | 是 | - | swc文件的绝对/相对路径 |
| 重建模型路径 | --test | -T | 是 | - | swc文件的绝对/相对路径。可输入文件夹，计算文件夹中所有模型的重建评分 |
| 重建结果输出路径 | --output | -O | 否 | $(pyneval)/output/ | 输出文件的路径（相对路径以neu\_metric所在文件夹为起点）。如果路径不存在，则创建相应文件夹。如果该参数不存在，结果打印到屏幕上 |
| 评价指标选择 | --metric | -M | 是 | - | DM,overlap_length,matched_lengthBM,diadem_metric,netmets中的一个或者多个 |
| json参数文件路径 | --config | -C | 是 | - | json配置文件的绝对/相对路径 |
| 是否显示调试信息 | --debug | -D | 否 | False | ALL/IO/METRIC 可选择相关模块的调试信息 |
