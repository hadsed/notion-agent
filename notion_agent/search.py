import requests

from notion_agent import config


def search(query: str, object_type: str = None, page_size: int = 5) -> dict:
    payload = {
        "query": query,
        "sort": {
            "direction": "ascending",
            "timestamp": "last_edited_time"
        },
        "page_size": page_size,
    }
    if object_type:
        payload["filter"] = {
            "value": object_type,
            "property": "object"
        }

    response = requests.request(
        'POST', 'https://api.notion.com/v1/search',
        headers={
            "Authorization": config.NOTION_API_KEY,
            "Notion-Version": "2022-06-28",
        },
        json=payload
    )

    return response.json()
