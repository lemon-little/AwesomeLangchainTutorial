import importlib
from typing import Dict, Any, Optional

from .config import Settings
from .schemas import ExecutionPlan, TaskUnderstanding, StepResult
from .tools import build_default_registry, ToolRegistry
from .state import StateStore
from .logging_utils import setup_logging


class TaskExecutor:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.registry = build_default_registry()
        self._load_extensions(self.registry)
        self.state = StateStore(settings)
        self.logger = setup_logging("autoplan.executor", log_file=self.settings.log_file)

    def _load_extensions(self, registry: ToolRegistry) -> None:
        for module_name in self.settings.tool_modules:
            module = importlib.import_module(module_name)
            if hasattr(module, "register_tools"):
                module.register_tools(registry)

    def run(self, plan: ExecutionPlan, understanding: TaskUnderstanding, run_id: Optional[str] = None) -> Dict[str, Any]:
        if run_id is None:
            run_id = self.state.create()
        elif not self.state.exists(run_id):
            self.state.save(run_id, {"run_id": run_id, "created_at": "", "steps": []})
        state_data = self.state.load(run_id)
        if not state_data.get("understanding"):
            state_data["understanding"] = understanding.model_dump()
        if not state_data.get("plan"):
            state_data["plan"] = plan.model_dump()
        self.state.save(run_id, state_data)
        completed_steps = {s["step_name"] for s in state_data.get("steps", []) if s.get("status") == "success"}
        context: Dict[str, Any] = {"understanding": understanding.model_dump()}
        results: list[StepResult] = []
        for step in plan.steps:
            if step.name in completed_steps:
                continue
            tool = self.registry.get(step.tool)
            self.logger.info(f"执行步骤: {step.name}")
            try:
                payload = tool(self.settings, context, step.parameters)
                result = StepResult(step_name=step.name, status="success", payload=payload)
                results.append(result)
                state_data["steps"].append(result.model_dump())
                self.state.save(run_id, state_data)
            except Exception as e:
                result = StepResult(step_name=step.name, status="failed", payload={"error": str(e)})
                state_data["steps"].append(result.model_dump())
                self.state.save(run_id, state_data)
                raise
        return {"run_id": run_id, "steps": [r.model_dump() for r in results]}
