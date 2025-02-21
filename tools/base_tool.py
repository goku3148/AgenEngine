from typing import Dict, List, Tuple
import inspect

class BaseTool:
    def __init__(self, name: str, description: str, function: callable, tags: List[str] = None, permissions: List[str] = None):
        self.name = name
        self.description = description
        self.func = function
        self.tags = tags or []
        self.permissions = permissions or []
        self.params_, self.types = self.parmas()

    def run(self, params: Dict[str, any]):
        params = self.object_conversion(params)
        return self.func(**params)

    def parmas(self):
        signature = inspect.signature(self.func)
        arguments = {}
        types = {}
        for param_name, param in signature.parameters.items():
            param_type = param.annotation if param.annotation != inspect.Parameter.empty else "No type specified"
            types[param_name] = param_type
            param_type = param_type.__name__ if hasattr(param_type, "__name__") else str(param_type)
            arguments[param_name] = {'type': param_type, "description": param.default}
        return arguments, types

    def f_format(self):
        format_ = {
            "name": self.name,
            "description": self.description,
            "tags": self.tags,
            "arguments": self.params_
        }
        return format_

    def object_conversion(self, params: Dict[str, any]):
        params_ = {}
        for key, value in params.items():
            params_[key] = self.types[key](value)
        return params_


def simple_addition(a:int="first digit",b:int="second digit") -> int:
    return a + b

def simple_subtraction(a:int="first digit",b:int="second digit") -> int:
    return a - b



simple_addition_ = BaseTool(description="simple addition",
                           name="simple_addition",
                           function=simple_addition,
                           )
simple_subtraction_ = BaseTool(description="simple subtraction",
                           name="simple_subtraction",
                           function=simple_subtraction,
                           )

params = {'a':1,'b':2}

print(simple_addition_.run(params))

