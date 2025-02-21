from typing import Dict
import json
import re
from GIt.tools.tool_manager import ToolVal, PackageVal
from agents.agentval import AgentVal

class BaseAgent:
    def __init__(self, prefix: str,
                 agent_type: str = "head_agent" & "sub_agent",
                 agent_name: str = 'agent',
                 instruction_format: str = "Please provide the {agents} with the following information: {agent_names}",
                 suffix: str= "Please provide the information requested above."):
        self.agent_type = agent_type
        self.agent_name = agent_name
        self.prefix = prefix
        self.suffix = suffix
        self.instruction_format_template = instruction_format
        

    def prompt(self, chain: str = '') -> str:
        """
        Generate a formatted prompt for the agent.

        Args:
            chain (str): Additional context or chain of actions.

        Returns:
            str: The formatted prompt.
        """
        instruction_format = self.generate_instruction_format()
        prompt = f"{self.prefix}\n{instruction_format}\n{self.suffix}\n{self.previous_history}\n{chain}"
        return prompt

    def generate_instruction_format(self) -> str:
        """
        Generate the instruction format by populating the template with agent details.

        Returns:
            str: Formatted instruction string.
        """
        agents_description = self.action_val.agents_description()
        agent_names = self.action_val.names()
        return self.instruction_format_template.format(agents=agents_description,
                                                       agent_names=agent_names)

    def parser(self, gen_output: str = '') -> dict:
        """
        Parse the generated output for structured data.

        Args:
            gen_output (str): The raw output from the agent.

        Returns:
            dict: Parsed action details, or None if parsing fails.
        """
        pattern = re.compile(r"```(?:json\s+)?(\{.*?\})```", re.DOTALL)

        match = pattern.search(gen_output)
        if not match:
            return None

        try:
            return json.loads(match.group(1).strip(), strict=False)
        except json.JSONDecodeError:
            # Attempt to fix common issues and retry parsing
            try:
                fixed_text = match.group(1).replace("{{", "{").replace("}}", "}")
                return json.loads(fixed_text, strict=False)
            except Exception as e:
                print(f"Parsing error: {e}")
                return None

    def _action(self, gen_output, action):
        """
        Determine the action type, name, and input based on the parse and action provided.

        Args:
            parse (dict or None): Parsed input data containing action details.
            action (tuple): Tuple containing agent, package, or tool validators.

        Returns:
            tuple: A tuple (action_type, action_name, action_input) representing the determined action.
        """
        parse = self.parser(gen_output)
        action_type = "default"
        action_name = "parse"
        action_input = "parser failed"


        if not parse:
            return action_type, action_name, action_input


        if isinstance(parse, dict):

            if "Final Answer" in parse.get("action", ""):
                action_type = "final action"
                action_name = "Final Answer"
                action_input = parse.get("action_input", "final input failed")


            elif isinstance(action, AgentVal) and parse["action"] in action.names():
                action_type = "agent action"
                action_name = parse["action"]
                action_input = parse.get("action_input", "agent input failed")


            elif (
                    isinstance(action[1], PackageVal)
                    and "#" in parse["action"]
                    and parse["action"].split("#")[0] in action[1].names().keys()
            ):
                package = parse["action"].split("#")
                action_type = "package action"
                action_name = package
                action_input = parse.get("action_input", "package input failed")


            elif isinstance(action[0], ToolVal) and parse["action"] in action[0].names():
                action_type = "tool action"
                action_name = parse["action"]
                action_input = parse.get("action_input", "tool input failed")


            else:
                action_type = "default"
                action_name = "name"
                action_input = "default"


        return action_type, action_name, action_input



