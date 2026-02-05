from typing import List

from .config import Settings
from .llm import build_llm, llm_structured_output
from .schemas import TaskUnderstanding, ExecutionPlan, PlanStep


class TaskPlanner:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.llm = build_llm(settings)

    def understand(self, task: str) -> TaskUnderstanding:
        system_prompt = "你是资深数据分析规划助手，输出结构化任务理解。"
        if self.llm is None:
            return TaskUnderstanding(
                objective=task,
                data_scope="待确认",
                time_range="待确认",
                business_context="待确认",
                constraints=[],
                risks=[],
                assumptions=["尚未提供外部数据细节"],
            )
        return llm_structured_output(
            self.llm,
            TaskUnderstanding,
            system_prompt,
            task,
        )

    def plan(self, understanding: TaskUnderstanding) -> ExecutionPlan:
        system_prompt = "你是数据分析任务规划引擎，输出可执行步骤与依赖。"
        if self.llm is None:
            steps: List[PlanStep] = [
                PlanStep(
                    name="data_extract",
                    description="连接数据源并获取所需数据",
                    inputs=["任务理解"],
                    outputs=["原始数据"],
                    tool="mysql_query",
                    parameters={},
                ),
                PlanStep(
                    name="data_clean",
                    description="清洗缺失值、重复值与异常值",
                    inputs=["原始数据"],
                    outputs=["清洗数据"],
                    tool="data_clean",
                    parameters={},
                ),
                PlanStep(
                    name="eda",
                    description="描述性统计与相关性分析",
                    inputs=["清洗数据"],
                    outputs=["EDA结果"],
                    tool="eda",
                    parameters={},
                ),
                PlanStep(
                    name="modeling",
                    description="异常检测与趋势分析",
                    inputs=["清洗数据"],
                    outputs=["模型结果"],
                    tool="modeling",
                    parameters={},
                ),
                PlanStep(
                    name="visualization",
                    description="生成图表与仪表盘素材",
                    inputs=["EDA结果", "模型结果"],
                    outputs=["图表文件"],
                    tool="visualization",
                    parameters={},
                ),
                PlanStep(
                    name="report",
                    description="汇总报告并生成多格式输出",
                    inputs=["全部分析结果"],
                    outputs=["报告文件"],
                    tool="report",
                    parameters={},
                ),
            ]
            return ExecutionPlan(summary="默认离线规划", steps=steps)
        return llm_structured_output(
            self.llm,
            ExecutionPlan,
            system_prompt,
            understanding.model_dump_json(),
        )

    def replan(self, understanding: TaskUnderstanding, feedback: str) -> ExecutionPlan:
        enhanced = TaskUnderstanding(
            objective=understanding.objective,
            data_scope=understanding.data_scope,
            time_range=understanding.time_range,
            business_context=f"{understanding.business_context}\n用户补充: {feedback}",
            constraints=understanding.constraints,
            risks=understanding.risks,
            assumptions=understanding.assumptions,
        )
        return self.plan(enhanced)
