# AutoPlanAgent Minimax-2-1

基于 LangChain 的自主规划数据分析智能体。覆盖任务理解、任务拆解、交互确认、动态执行与报告生成，并提供可扩展工具与 API 接口。

## 目录结构

- autoplan_agent: 核心代码
- state: 运行状态与中断恢复数据
- data: 数据缓存与样例

## 快速开始

1. 复制环境变量模板并填写

```
cp .env.example .env
```

2. 运行命令行模式

```
python -m autoplan_agent.cli plan --task "分析某公司近三年营收趋势"
python -m autoplan_agent.cli run --task "分析某公司近三年营收趋势"
python -m autoplan_agent.cli ingest --companies 迈为股份 捷佳伟创 拉普拉斯 奥特维 晶盛机电 连城数控 --years 2024 2023 2022
```

3. 运行 API 服务

```
python -m autoplan_agent.api
```

## 功能覆盖

- 任务理解与解析，输出结构化理解报告
- 自动拆解为数据提取、清洗、EDA、建模、可视化等步骤
- 交互确认与二次修订
- 连接 MySQL 执行 SQL，支持安全约束与性能限制
- 统计分析、异常检测、趋势分析与图表生成
- 生成 Markdown/HTML/PDF 报告

## 说明

未提供外部 API Key 时会自动切换为规则化理解与规划模式，便于离线测试。
