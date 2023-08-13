from typing import List
from notion_agent.models import ToolAugmentedPlanningModel
from notion_agent.tools import CodeTool, OpenApiTool


class NotionPlanner:
    def __init__(self):
        self.tools = [
            OpenApiTool('notion'),
            CodeTool(),
        ]
        self.planning_model = ToolAugmentedPlanningModel('gpt-4')

    def generate_plan(self, goal: str) -> List['notion_agent.messaging.Message']:
        messages = self.planning_model.run(goal, self.tools)
        return messages
