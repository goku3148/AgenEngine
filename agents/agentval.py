import time
import json
import logging
from typing import List, Dict, Any, Tuple
from .agents import BaseAgent
from GIt.callback import CallbackHandler, AgentLog

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AgentVal")

class AgentVal:
    def __init__(self, agents: List[BaseAgent]):
        self.agents = agents

    def names(self):
        agent_names = [agent.type for agent in self.agents]
        return agent_names if agent_names else "No Action Agents"

    def agent_description(self):
        agent_descriptions = [agent.description for agent in self.a_agents]
        return agent_descriptions if agent_descriptions else "No Action Agents"

    def a_format(self):
        formats = [
            {
                "type": agent.type,
                "description": agent.description,
                "schema": agent.schema
            }
            for agent in self.agents
        ]
        return formats

    def agent_retrieval(self, agent_name: str):
        try : 
            agent_idx = self.names().index(agent_name)
            return self.agents[agent_idx]
        except KeyError as ke:
            logger.error(f"{agent_name} not found in AgentVal : {ke}") 
    
    def agents_retrieval(self, agent_names:List[str]):
        retrieved_agents = []
        for agent_name in agent_names:
            try:
                agent_idx = self.names().index(agent_name)
                agent_names.append(self.agents[agent_idx])
            except KeyError as ke:
                logger.error(f"{agent_name} not found in AgentVal : {ke}")
                continue
        
        if not retrieved_agents:
            raise ValueError(f"None of the agents found in AgentVal: {agent_names}")
        return retrieved_agents
        
    def filter_agents(self, key: str, value: str) -> List[BaseAgent]:
        return [
            agent for agent in self.a_agents
            if getattr(agent, key, "").lower() == value.lower()
        ]

    def execute_agent(self, agent: str, params: Dict[str, Any] = None):
        agent = self.agent_retrieval(agent)
        start_time = time.time()
        result = agent.perform_action(params or {})
        elapsed_time = time.time() - start_time
        print(f"Execution time for agent '{cagent}': {elapsed_time:.4f}s")
        return result

    def execute_with_logging(self, cagent: str, params: Dict[str, Any] = None):
        try:
            logger.info(f"Executing agent '{cagent}' with params: {params}")
            result = self.execute_agent(cagent, params)
            logger.info(f"Result of agent '{cagent}': {result}")
            return result
        except Exception as e:
            logger.error(f"Error executing agent '{cagent}': {e}")
            raise

    def batch_execute(self, agent_sequence: List[Tuple[str, Dict[str, Any]]]):
        results = []
        for agent_name, params in agent_sequence:
            try:
                result = self.execute_agent(agent_name, params)
                results.append((agent_name, result))
            except Exception as e:
                results.append((agent_name, f"Error: {e}"))
        return results

    def reset_agent_state(self, cagent: str):
        agent = self.agent_retrieval(cagent)
        if hasattr(agent, "reset_state"):
            agent.reset_state()
        else:
            print(f"Agent '{cagent}' does not support state resetting.")

    def resolve_dependencies(self, dependency_chain: List[Tuple[str, Dict[str, Any]]]):
        data = None
        for agent_name, params in dependency_chain:
            if data:
                params.update(data)
            data = self.execute_agent(agent_name, params)
        return data

    def export_agents(self, filename: str = "agents.json"):
        agent_data = self.a_format()
        with open(filename, "w") as f:
            json.dump(agent_data, f, indent=4)
        print(f"Agent details exported to {filename}.")

    def generate_docs(self, filename: str = "agent_docs.md"):
        with open(filename, "w") as f:
            for agent in self.a_agents:
                f.write(f"### {agent.type}\n")
                f.write(f"- Description: {agent.description}\n")
                f.write(f"- Schema: {agent.schema}\n\n")
        print(f"Documentation generated: {filename}")
