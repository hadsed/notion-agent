import json
from pydantic import BaseModel, Field


class Message(BaseModel):
    pass


class ObservationMessage(Message):
    pass


class ActionMessage(Message):
    goal: str = Field(description="The subgoal of this action")
    tool_name: str = Field(description="The name of the tool")
    function_name: str = Field(description="The name of the function or API")
    function_parameters: dict = Field(
        description="The arguments to the function")


def parse_message(message_json: str) -> Message:
    message_dict = json.loads(message_json)
    return ActionMessage(**message_dict)


