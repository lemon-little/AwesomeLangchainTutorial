import json
import sys

from autoplan_agent.config import Settings
from autoplan_agent.planner import TaskPlanner


def main():
    task = "分析光伏行业公司近三年营收趋势"
    if len(sys.argv) > 1:
        task = sys.argv[1]
    settings = Settings.load()
    planner = TaskPlanner(settings)
    understanding = planner.understand(task)
    plan = planner.plan(understanding)
    print(json.dumps({"understanding": understanding.model_dump(), "plan": plan.model_dump()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
