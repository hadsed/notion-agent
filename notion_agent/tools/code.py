import inspect

from notion_agent.tools.base import Tool
import notion_agent.tools._code_functions as code_functions


class CodeTool(Tool):
    def __init__(self):
        self._methods_structured = [
            {
                'name': f_name,
                'signature': inspect.signature(f),
                'doc': f.__doc__,
            }
            for f_name, f in inspect.getmembers(code_functions, inspect.isfunction)
        ]
        self._methods = [
            f'{f["name"]}{f["signature"]}: {f["doc"]}'
            for f in self._methods_structured]
        self._description = '- ' + '\n- '.join(self._methods)

    @property
    def methods(self):
        return self._methods_structured

    @property
    def description(self):
        return self._description

    def execute(self, function_name: str, function_parameters: dict):
        func = self.methods_structured[function_name]
        return func(**function_parameters)
