import argparse
import json

from .config import Settings
from .planner import TaskPlanner
from .executor import TaskExecutor
from .state import StateStore
from .tools import public_data_ingest, build_default_registry
from .schemas import ExecutionPlan, TaskUnderstanding


def _print(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command")

    plan_cmd = sub.add_parser("plan")
    plan_cmd.add_argument("--task", required=True)
    plan_cmd.add_argument("--feedback")

    run_cmd = sub.add_parser("run")
    run_cmd.add_argument("--task", required=True)
    run_cmd.add_argument("--feedback")
    run_cmd.add_argument("--yes", action="store_true")
    run_cmd.add_argument("--run-id")

    resume_cmd = sub.add_parser("resume")
    resume_cmd.add_argument("--run-id", required=True)

    ingest_cmd = sub.add_parser("ingest")
    ingest_cmd.add_argument("--companies", nargs="*")
    ingest_cmd.add_argument("--years", nargs="*")

    status_cmd = sub.add_parser("status")
    status_cmd.add_argument("--run-id", required=True)

    args = parser.parse_args()
    settings = Settings.load()
    planner = TaskPlanner(settings)
    executor = TaskExecutor(settings)
    state = StateStore(settings)

    if args.command == "plan":
        understanding = planner.understand(args.task)
        plan = planner.replan(understanding, args.feedback) if args.feedback else planner.plan(understanding)
        _print({"understanding": understanding.model_dump(), "plan": plan.model_dump()})
        return

    if args.command == "run":
        understanding = planner.understand(args.task)
        plan = planner.replan(understanding, args.feedback) if args.feedback else planner.plan(understanding)
        _print({"understanding": understanding.model_dump(), "plan": plan.model_dump()})
        if not args.yes:
            confirm = input("是否确认执行计划? (y/n): ").strip().lower()
            if confirm != "y":
                feedback = input("请输入需要调整的要求: ").strip()
                if feedback:
                    plan = planner.replan(understanding, feedback)
                    _print({"plan": plan.model_dump()})
                    confirm = input("是否确认执行计划? (y/n): ").strip().lower()
                    if confirm != "y":
                        return
                else:
                    return
        result = executor.run(plan, understanding, run_id=args.run_id)
        _print(result)
        return

    if args.command == "resume":
        if not state.exists(args.run_id):
            print("run_id 不存在")
            return
        data = state.load(args.run_id)
        plan_data = data.get("plan")
        understanding_data = data.get("understanding")
        if not plan_data or not understanding_data:
            print("缺少计划或理解数据，无法续跑")
            return
        plan = ExecutionPlan.model_validate(plan_data)
        understanding = TaskUnderstanding.model_validate(understanding_data)
        result = executor.run(plan, understanding, run_id=args.run_id)
        _print(result)
        return

    if args.command == "ingest":
        registry = build_default_registry()
        context = {}
        params = {"companies": args.companies or [], "years": args.years or []}
        result = registry.get("public_data_ingest")(settings, context, params)
        _print(result)
        return

    if args.command == "status":
        if not state.exists(args.run_id):
            print("run_id 不存在")
            return
        _print(state.load(args.run_id))
        return


if __name__ == "__main__":
    main()
