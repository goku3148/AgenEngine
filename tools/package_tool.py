from typing import List, Tuple, Dict
import inspect


class PACKAGES:
    NAME: str = ""
    DESCRIPTION: str = ""
    DEFAULT_ARGUS: Dict[str, any] = {}

    def __init__(self):
        self.methods = [name for name, func in inspect.getmembers(self, predicate=inspect.ismethod) if
                        name.startswith('t_')]
        self.context = {}

    def c_format(self):
        return {
            "package_name": self.NAME,
            "package_description": self.DESCRIPTION,
            "default_args": self.DEFAULT_ARGUS,
            "tools": self.tool_format()
        }

    def run(self, tool: str, params: Dict[str, any] = None):
        tooln = 't_' + tool
        func = getattr(self, tooln, None)
        if not func:
            return f"Tool {tool} not found in package {self.NAME}."

        params = params or {}
        try:
            return func(**params)
        except Exception as e:
            return f"Error executing {tool}: {e}"
        
    def method_validation(self,tool:str):
        tooln = 't_'+ tool
        return hasattr(self,tooln)

    def tool_format(self):
        method_descriptions = {}
        for method_name in self.methods:
            method = getattr(self, method_name)
            signature = inspect.signature(method)
            arguments = {}
            description = ''
            for param_name, param in signature.parameters.items():
                param_type = param.annotation if param.annotation != inspect.Parameter.empty else str
                param_type = param_type.__name__ if hasattr(param_type, "__name__") else str(param_type)
                if param_name == "description":
                    description = param.default
                else:
                    arguments[param_name] = {'type': param_type, "description": param.default}
            method_descriptions[method_name.removeprefix('t_')] = {
                'description': description,
                'arguments': arguments
            }
        return method_descriptions

    def batch_execute(self, tool_sequence: List[Tuple[str, Dict[str, any]]]):
        results = []
        for tool_name, params in tool_sequence:
            results.append(self.call(tool_name, params))
        return results

