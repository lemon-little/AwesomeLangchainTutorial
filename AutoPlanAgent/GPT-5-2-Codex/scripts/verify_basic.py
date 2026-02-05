import importlib

modules = [
    "autoplan_agent",
    "autoplan_agent.config",
    "autoplan_agent.planner",
    "autoplan_agent.executor",
    "autoplan_agent.tools",
    "autoplan_agent.report",
    "autoplan_agent.api",
]

for name in modules:
    importlib.import_module(name)

print("basic import ok")
