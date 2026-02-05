from pydantic import BaseModel, Field
from typing import Any, List, Dict


class TaskUnderstanding(BaseModel):
    objective: str = Field(default="")
    data_scope: str = Field(default="")
    time_range: str = Field(default="")
    business_context: str = Field(default="")
    constraints: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)


class PlanStep(BaseModel):
    name: str
    description: str
    inputs: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    tool: str = Field(default="")
    parameters: Dict[str, Any] = Field(default_factory=dict)


class ExecutionPlan(BaseModel):
    summary: str
    steps: List[PlanStep]


class StepResult(BaseModel):
    step_name: str
    status: str
    payload: Dict[str, Any] = Field(default_factory=dict)


class AnalysisReport(BaseModel):
    executive_summary: str
    data_sources: List[str]
    methods: List[str]
    findings: List[str]
    recommendations: List[str]
    artifacts: List[str]
