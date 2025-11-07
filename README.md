# MyAgent
## 功能
- 提供搜索并返回公司相关政策；
- 提供搜索和管理存储在数据库中的航班、酒店、租车和旅游产品等数据；
- 提供预定/改签航班，酒店等功能；
- 提供预定租车和旅游产品的功能；

## 项目使用说明
### 环境
- 环境安装依赖全在`requirements.txt`文件中，创建一个新的虚拟环境后，cd到`requirements.txt`文件对应的路径下，执行以下命令即可
```pip install -r requirements.txt```
### 工程执行
- 关于llm模型（`llm_tavily.py`）：本项目用的在线智谱`GLM-4.5`，需要配置openai_api_key和openai_api_base，也可以用本地部署的llm，修改key和base_url即可；
- 执行脚本：

## 需求描述
### 