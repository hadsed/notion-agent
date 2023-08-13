from notion_agent.actor import NotionActor
from notion_agent.plan import NotionPlanner


class NotionAgent:
    def __init__(self, ):
        self.planner = NotionPlanner()
        self.actor = NotionActor()

    def not_accomplished(self, goal: str) -> bool:
        return True

    def run(self, goal: str):
        while self.not_accomplished(goal):
            plan = self.planner.generate_plan(goal)
            self.actor.execute(plan)
            break
