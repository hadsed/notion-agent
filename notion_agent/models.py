import json
import logging
from textwrap import dedent
from typing import Dict, List
import openai

from notion_agent.messaging import ActionMessage, Message, parse_message


logger = logging.getLogger(__name__)


def openai_chat_completion(model: str, prompt: str, system_prompt: str, **kwargs):
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        **kwargs
    )
    return response.choices[0]['message']['content']


class ToolAugmentedPlanningModel:
    STEP_DELIMITER = "<break>"

    def __init__(self, model: str = "gpt-4"):
        self.model = model

    def construct_goal_decomposition_prompt(
        self,
        goal: str,
        tools: List['notion_agent.tools.Tool'],
    ) -> str:
        tool_description_blocks = [
            f"Functions in {tool.name}:\n{tool.description}" for tool in tools]
        message_schema = ActionMessage.model_json_schema()['properties']
        message_attributes = '- ' + '\n- '.join([
            f"{attr_name}: {attr_props['description']}"
            for attr_name, attr_props in message_schema.items()
        ])
        return (
            dedent(f"""
                You have access to the following tools and their functions:
                ----
                """) + 
            '\n----\n'.join(tool_description_blocks) +
            dedent(f"""
            ----
            Your goal: "{goal}"
            ----
            Output a plan as a series of JSON objects delimited with {ToolAugmentedPlanningModel.STEP_DELIMITER}.
            Do not output a single JSON object with a list of steps, use the delimiter instead.
            It is important that you output valid JSON at all times.
            The following attributes are required:\n""") +
            message_attributes +
            dedent(f"""
            ----
            Plan:
            """)
        )

    def parse_plan_descriptions(self, plan_descriptions: str) -> List[Message]:
        descriptions = plan_descriptions.split(
            ToolAugmentedPlanningModel.STEP_DELIMITER)
        plan = []
        for message_json in descriptions:
            try:
                plan.append(parse_message(message_json))
            except json.decoder.JSONDecodeError as e:
                logger.error(f"Failed to parse message:\n{message_json}\n\n"
                             f"Raw plan: {descriptions}")
                raise e
        return plan

    def run(self, goal: str, tools: List['notion_agent.tools.Tool']) -> List[Message]:
        prompt = self.construct_goal_decomposition_prompt(goal, tools)
        system_prompt = "You are an expert at planning tasks using APIs."
        logger.info(f"Prompt:\n{prompt}")
        plan_descriptions = openai_chat_completion(
            self.model, prompt, system_prompt, temperature=0)
        return self.parse_plan_descriptions(plan_descriptions)


class OpenApiRequestBuilderModel:
    def __init__(self, model: str = "gpt-4"):
        self.model = model

    def construct_request_prompt(
        self, api_name: str, spec: str, api_parameters: str,
    ) -> str:
        return dedent(f"""
            OpenAPI spec for {api_name}:
            {spec}
            ----
            Given parameters for the request:
            {api_parameters}
            ----
            Output a JSON object for the request headers and payload.
            ----
            Request:
        """)

    def run(self, api_name: str, api_parameters: str, spec: dict) -> Dict:
        prompt = self.construct_request_prompt(api_name, spec, api_parameters)
        system_prompt = "You are an expert at constructing requests to APIs from OpenAPI specs."
        request = openai_chat_completion(
            self.model, prompt, system_prompt, temperature=0)
        try:
            request = json.loads(request)
            return request
        except json.decoder.JSONDecodeError:
            print(f"Failed to parse request: {request}")
            return {}
