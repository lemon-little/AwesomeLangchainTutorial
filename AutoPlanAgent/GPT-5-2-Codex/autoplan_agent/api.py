from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

from .config import Settings
from .planner import TaskPlanner
from .executor import TaskExecutor
from .state import StateStore


class PlanRequest(BaseModel):
    task: str
    feedback: Optional[str] = None


class ExecuteRequest(BaseModel):
    task: str
    feedback: Optional[str] = None
    run_id: Optional[str] = None


def create_app() -> FastAPI:
    settings = Settings.load()
    planner = TaskPlanner(settings)
    executor = TaskExecutor(settings)
    state = StateStore(settings)

    app = FastAPI(title="AutoPlanAgent API")

    @app.post("/plan")
    def plan(req: PlanRequest):
        understanding = planner.understand(req.task)
        if req.feedback:
            plan = planner.replan(understanding, req.feedback)
        else:
            plan = planner.plan(understanding)
        return {"understanding": understanding.model_dump(), "plan": plan.model_dump()}

    @app.post("/execute")
    def execute(req: ExecuteRequest):
        understanding = planner.understand(req.task)
        if req.feedback:
            plan = planner.replan(understanding, req.feedback)
        else:
            plan = planner.plan(understanding)
        result = executor.run(plan, understanding, run_id=req.run_id)
        return {"run": result}

    @app.get("/status/{run_id}")
    def status(run_id: str):
        if not state.exists(run_id):
            return {"error": "run_id 不存在"}
        return state.load(run_id)

    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(create_app(), host="0.0.0.0", port=8000)
