import logging
from typing import List
from notion_agent.messaging import ActionMessage, Message


logger = logging.getLogger(__name__)


class NotionActor:
    def __init__(self):
        pass

    def execute(self, messages: List[Message]):
        for message in messages:
            logger.info(f"Executing message:\n{message}")
            if isinstance(message, ActionMessage):
                self.execute_action(message)

    def execute_action(self, action: ActionMessage):
        pass
