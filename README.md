# Awesome LangChain Tutorial

这是一个关于 LangChain 的深度学习与实践教程仓库，涵盖了从基础入门到高级 Agent 架构的多个阶段。本项目旨在通过实际的代码示例和 Notebook 教程，帮助开发者掌握 LangChain 生态系统的核心概念与最新特性。

## 📁 项目结构

本仓库分为三个主要模块，分别对应不同的学习阶段和技术栈：

- **[AutoPlanAgent](./AutoPlanAgent)**: 专注于自主规划 Agent 的实现。
  - 使用 Qwen 系列模型（如 Qwen3-30B-A3B-Instruct）进行复杂任务规划。
  - 提供了自定义模型集成和日志记录工具。
- **[langchain0.3](./langchain0.3)**: 基于 LangChain v0.3 的基础教程与服务示例。
  - 包含数学运算服务 (`math_server.py`) 和天气查询服务 (`weather_server.py`)。
  - 丰富的 Notebook 教程（Task 1-6），涵盖了核心组件的使用。
- **[langchain1.x](./langchain1.x)**: 适配 LangChain v1.x 的进阶内容。
  - 使用 `uv` 进行现代化的 Python 依赖管理。
  - 涵盖 Agentic RAG、自定义 RAG Agent、DeepAgents 快速入门、中间件（Middleware）机制、多智能体（Multi-Agent）系统以及 Agent Skills 等高级主题。

## 🚀 快速开始

### 环境配置

本项目推荐使用 `uv` 管理依赖。在 `langchain1.x` 目录下，你可以快速初始化环境：

```bash
cd langchain1.x
uv sync
```

### 核心内容概览

#### LangChain 1.x 进阶任务
1. **Quickstart**: 快速上手 LangChain 1.x。
2. **Agentic RAG**: 构建具备自主决策能力的 RAG 系统。
3. **Custom RAG Agent**: 深度定制 RAG Agent 流程。
4. **DeepAgents**: 探索 DeepAgents 框架。
5. **Middleware**: 理解并实现 LangChain 中的中间件机制。
6. **Multi-Agent**: 构建多智能体协同系统。

#### LangChain 0.3 基础任务
- 提供了从 Task 1 到 Task 6 的系列教程，适合初学者了解 LangChain 0.3 的基本用法。

## 🛠️ 技术栈

- **Core**: LangChain, LangGraph, LangSmith
- **Models**: OpenAI, Qwen (via ModelScope/SiliconFlow)
- **Tools**: Tavily, Playwright, Trafilatura
- **Environment**: Python 3.11+, `uv`


希望这个教程能帮助你在 LangChain 的学习道路上更进一步！
