import json
import click
from notion_agent.agent import NotionAgent

from notion_agent.plan import NotionPlanner
from notion_agent.search import search as notion_search

@click.group()
def cli():
    pass


@cli.command()
@click.argument("query", type=str)
def search(query: str):
    results = notion_search(query, page_size=100)
    titles = [
        result["properties"]["title"]["title"][0]["plain_text"]
        for result in results["results"]
        if result["object"] == "page" and result["properties"].get("title")
    ]
    print(json.dumps(titles))


@cli.command()
@click.argument("goal", type=str)
def plan(goal: str):
    planner = NotionPlanner(goal)
    plan = planner.generate_plan()
    for message in plan:
        print(json.dumps(message.dict(), indent=4))


@cli.command()
@click.argument("goal", type=str)
def execute(goal: str):
    agent = NotionAgent()
    agent.run(goal)
