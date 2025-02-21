from typing import List, Dict
from GIt.tools.base_tool import BaseTool, simple_addition_,simple_subtraction_
from GIt.tools.package_tool import PACKAGES

class PackageVal:
    def __init__(self, package_list):
        self.package_list = package_list

    def names(self):
        return {pkg.NAME: list(pkg.tool_format().keys()) for pkg in self.package_list}

    def package_retrieval(self, package_name: str) -> PACKAGES:
        for pkg in self.package_list:
            if pkg.NAME == package_name:
                return pkg
            else : 
                return False
        raise ValueError(f"Package {package_name} not found.")

    def tool_args(self, package_name: str, tool_name: str):
        package = self.package_retrieval(package_name)
        tool_format = package.tool_format()
        if tool_name not in tool_format:
            raise ValueError(f"Tool {tool_name} not found in package {package_name}.")
        return tool_format[tool_name]['arguments']

    def package_format(self):
        return [pkg.c_format() for pkg in self.package_list]

    def search(self, query: str):
        results = []
        for pkg in self.package_list:
            for tool_name, tool_info in pkg.tool_format().items():
                if query in tool_name or query in tool_info['description']:
                    results.append((pkg.NAME, tool_name, tool_info))
        return results


class ToolVal:
    def __init__(self, tool_list: List[BaseTool] = None):
        self.tool_list = tool_list or []

    def names(self):
        return [tool.name for tool in self.tool_list]

    def tool_formats(self):
        return [tool.f_format() for tool in self.tool_list]

    def tool_retrieval(self, tool_name: str):
        for tool in self.tool_list:
            if tool.name == tool_name:
                return tool
        raise ValueError(f"Tool {tool_name} not found.")

    def add_tool(self, tool: BaseTool):
        self.tool_list.append(tool)

    def remove_tool(self, tool_name: str):
        self.tool_list = [tool for tool in self.tool_list if tool.name != tool_name]

    def safe_execute(self, tool_name: str, params: Dict[str, any], retries: int = 3):
        tool = self.tool_retrieval(tool_name)
        for attempt in range(retries):
            try:
                return tool.run(params)
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
        raise RuntimeError(f"Tool {tool_name} failed after {retries} attempts.")

    def monitor_execution(self, tool_name: str, params: Dict[str, any]):
        tool = self.tool_retrieval(tool_name)
        start_time = time.time()
        result = tool.run(params)
        execution_time = time.time() - start_time
        print(f"Execution time for {tool_name}: {execution_time:.4f}s")
        return result




tool_val = ToolVal([simple_addition_])

tool_val.add_tool(tool=simple_subtraction_)

tool = tool_val.tool_retrieval(tool_name="simple_subtraction")

params = {'a':1,'b':2}

exe = tool.run(params)

print(exe)