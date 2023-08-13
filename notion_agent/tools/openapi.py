from collections import Iterable
import json
import requests

from notion_agent.models import OpenApiRequestBuilderModel
from notion_agent.tools.base import Tool


HTTP_METHODS = {'GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS', 'PATCH'}


class OpenApiTool(Tool):
    def __init__(self, api_name: str):
        self.spec = get_openapi_spec(api_name)
        self._methods = get_endpoint_descriptions(self.spec)
        self._description = summarize_api(self.spec)
        self.request_builder_model = OpenApiRequestBuilderModel()

    @property
    def methods(self):
        return self._methods

    @property
    def description(self):
        return self._description

    def build_http_request(
        self, endpoint: str, method: str, function_parameters: dict
    ) -> [dict, dict]:
        spec = self.spec['paths'][endpoint][method.lower()]
        headers_and_payload = self.request_builder_model.run(
            endpoint, function_parameters, spec)
        headers, payload = headers_and_payload['headers'], headers_and_payload['payload']
        return headers, payload

    def execute(self, function_name: str, function_parameters: dict):
        endpoint, method, _ = description_to_endpoint(function_name)
        headers, payload = self.build_http_request(
            endpoint, method, function_parameters)
        url = f'{self.spec["servers"][0]["url"]}{endpoint}'
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=payload,
        )
        return response.json()


def get_openapi_spec(api_name: str) -> dict:
    with open('openpm.json', 'r') as f:
        openpm_raw = json.load(f)
    openpm = {}
    for package in openpm_raw:
        openpm[package['id']] = json.loads(package['openapi'])
    try:
        return openpm[api_name]
    except KeyError:
        raise KeyError(f'No OpenAPI spec found for {api_name}')


def get_endpoint_descriptions(spec) -> dict:
    """Returns a dict of endpoint descriptions keyed by (endpoint, method)"""
    endpoint_descriptions = {}
    endpoints = spec['paths']
    for endpoint_name, endpoint in endpoints.items():
        for method_name, method in endpoint.items():
            if method_name.upper() not in HTTP_METHODS:
                continue
            if isinstance(method, Iterable):
                description = [
                    v
                    for k, v in method.items()
                    if k in {'description', 'summary'}
                ][0]
                endpoint_descriptions[(endpoint_name, method_name)] = description
            else:
                description = method.get('description')
                summary = method.get('summary')
                if description or summary:
                    endpoint_descriptions[(endpoint_name, method_name)] = (
                        description or summary
                    )

    return endpoint_descriptions


def endpoint_to_description(endpoint: str, method: str, description: str) -> str:
    return f"{method.upper():8} {endpoint}: {description}"


def description_to_endpoint(description: str) -> str:
    method_and_endpoint = description.split(': ')[0]
    method, endpoint = method_and_endpoint.split(' ')
    description = ': '.join(description.split(': ')[1:])
    return endpoint, method, description


def prettyfy_endpoint_descriptions(descriptions: dict) -> None:
    return [
        endpoint_to_description(endpoint, method, description)
        for (endpoint, method), description in descriptions.items()]


def summarize_api(spec: dict) -> str:
    endpoint_descriptions = get_endpoint_descriptions(spec)
    pretty_descriptions = prettyfy_endpoint_descriptions(endpoint_descriptions)
    return '- ' + '\n- '.join(pretty_descriptions)
