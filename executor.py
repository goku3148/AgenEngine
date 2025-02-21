import time
from turtledemo.sorting_animate import instructions1

from GIt.agents import BaseAgent
from GIt.agents.agentval import AgentVal
from GIt.tools.tool_manager import ToolVal,PackageVal
from typing import *
import re
import json
from GIt.callback import CallbackHandler, AgentLog
import logging

logging.basicConfig(level=logging.ERROR,filename='action_error',filemode='a')
logger = logging.getLogger(__name__)


class AgentConstructor():
    def __init__(self, agents: AgentVal):
        self.agents = agents

    def schema(self,agent_type:str,head_agent:str,sub_agent:List[str],single_agent:str):
        HEAD_AGENT_KEY = "head_agent"
        SUB_AGENTS_KEY = "sub_agents"
        AGENT_KEY = "agent"
        if agent_type == "multi_agent":
            agent_schema = agent_schema_multi = {
                    "multi_agent": {
                     HEAD_AGENT_KEY: "head_agent_name",  # Name of the head agent
                     SUB_AGENTS_KEY: ["sub_agent_1", "sub_agent_2"]  # List of sub-agent names
                     }}
            return agent_schema
        elif agent_type == "single_agent":
            agent_schema = agent_schema_single = {
                    "single_agent": {
                     AGENT_KEY:  single_agent}} # Name of the agent
            return agent_schema
        else:
            return None
    
    def get_agents(self, agent_schema: dict):
        if "multi_agent" in agent_schema:
            schema = agent_schema["multi_agent"]
            head_agent_name = schema["head_agent"]
            sub_agents_names = schema["sub_agents"]

            head_agent = self.agents.agent_retrieval(head_agent_name)
            sub_agents = self.agents.agents_retrieval(sub_agents_names)

            return {"head_agent": head_agent, "sub_agents": sub_agents}

        elif "single_agent" in agent_schema:
            schema = agent_schema["single_agent"]
            agent_name = schema["agent"]

            agent = self.agents.agent_retrieval(agent_name)
            return {"agent": agent}

        else:
            raise ValueError("Unknown agent schema")

class AgentState:
    def __init__(self,agent:BaseAgent=None,
                 callback:CallbackHandler=None,
                 max_iterations:int=5,
                 instruct_continuety:bool=True,
                 user_input:str="",
                 history:List[Dict]=[],
                 memory_limit:int=5,
                 ):
        self.memory_limit = memory_limit
        self.agent = agent
        self.iteration = 0
        self.anchore = time.time()
        self.max_ite = max_iterations
        self.instruction = instruct_continuety
        self.states = []
        self.gate = True
        self.hustory = history
        self.user_input = user_input

    def should_continue(self):
        if self.instruction:
            gate = True
            mid_cont = int(0.7*self.max_ite)
            if mid_cont - self.interation > 0:
                instruction = f"You have {self.iteration - mid_cont} only iteration steps left to converge to solution"
            elif mid_cont - self.iteration == 0:
                instruction = f"You should converge!"
            elif self.max_ite - self.iteration >= 1:
                instruction = f"You must converge in this step!"
            else :
                instruction = f"!!Stopping!!"
            return instruction, gate
        else :
            if self.max_ite - self.iteration < 0:
                gate = False
            else :
                gate = True
            return gate

    def timestamp(self,anchore=None) -> int:
        if anchore is None:
            anchore = self.anchore
        return int((time.time() - anchore)*10)/10

    def stop(self):
        pass
    
    def s_step(self):
        pass

    def agent_scratchpad() -> Dict:
        return {}
    
    def update(self,action) -> None:
        self.iteration += 1
        cont_inst, gate = self.should_continue()
        step = {'ite':self.iteration,'action_type':action.type,
                'action_name':action.name,'action':action.output,
                'timestamp':self.timestamp(),'should_continue':cont_inst}
        self.states.append(step)

    def history(self) -> List:
        if not self.history:
            history = self.history.append({'called':0,'user':self.user_input,"agent":self.states[-1]['action'],'time':time.localtime()})
            return history
        else:
            prev = self.history[-1]
            history = history.append({'called':prev['called']+1,'user':self.user_input,"agent":self.states[-1]['action'],'time':time.localtime()})
            history = history[:self.memory_limit]
            return history
    
    def final_response(self) -> Dict:
        user_input = self.user_input
        final_output = self.states[-1]['action']
        return {'user_input':user_input,'final_output':final_output, "time":self.timestamp()}
    

class Action:
    action = ["package_call","method_call","final_call","default_call","agent_call","final_call"]
    def __init__(self,
                 agents:AgentVal,
                 tools:ToolVal,
                 packages:PackageVal,
                 callback:CallbackHandler):
        self.agent = agents
        self.tools = tools
        self.packages = packages
        self.callback = callback
        pass

    def  response(self,step):
        action_type, action, action_input = step

        if action_type == 'package_call':
            return self.package_call(action, action_input)
        
        elif action_type == "method_call":
            return self.method_call(action, action_input)

        elif action_type == "final_call":
            return self.final_call(action, action_input)
        
        elif action_type == "agent_call":
            return self.agent_call(action, action_input)

        else:
            self.default_call()

    def package_call(self,action,action_input):
        packagen = action[0]
        tooln = action[1]
        package = self.packages.package_retrieval(packagen)
        if self.packages.package_retrieval(packagen) != False:
            self.callback.package_response(tool=action,inputs=action_input,error='Not Found')
            if package.method_validation(tooln):
                try : 
                    params = action_input
                    response = package.run(tool=tooln, params=params)
                    response = {'action':f"{packagen} : {tooln}",'input':action_input,'response':response}
                except TypeError as te:
                    logger.error(f"Type Error : {te}")
                    response = self.callback.call_response(tool=action,inputs=action_input,error="Type Error")
                except Exception as e:
                    logger.error(f"Execution Error: {e}")
                    response = self.callback.call_response(tool=action,inputs=action_input,error="Execution Error")
            else:
                response = self.callback.package_response(tool=action,inputs=action_input,error="method validation")
                logger.error(f"method {tooln} not found")
    
        else : 
            response = self.callback.package_response(tool=action,inputs=action_input,error="package validation")
            logger.error(f"package {packagen} not found")
        
        return response

    def method_call(self,action,action_input):
        try :
            tool = self.tools.tool_retrieval(action)
            try :
                parmas = action_input
                response = tool.run(params=parmas)
                response = {'action':action,'input':action_input,'response':response}
            except TypeError as ty:
                logger.error(f"Type Error : {ty}")
                response = self.callback.tool_response(tool=tool,inputs=action_input,error=ty)
        except Exception as te:
            logger.error(f"Tool Error : {te}")
            response = self.callback.tool_response(tool=action,inputs=action_input,error=te)
        return response
    
    def agent_call(self, action, action_input):
        #for multi agent execution

        pass

    def final_call(self,action,action_input):
        pass

    def default_call(self):
        pass


class AgentExecutor:
    def __init__(self,
                 llm,
                 agents: AgentVal,
                 tools: ToolVal,
                 packages: PackageVal,
                 callback: CallbackHandler,
                 agent_scheme: str,
                 ):
        self.llm = llm
        self.agents = agents
        self.tools = tools
        self.packages = packages
        self.agent_schema = agent_scheme
        self.default_callback = CallbackHandler()
        self.agent_constructor = AgentConstructor(agents)

    def agent_validation(self):
        """
        Validate the agents according to the agent_schema.
        """
        if self.agent_schema == "multi_agent":
            schema = self.agent_schema["multi_agent"]
            head_agent_name = schema["head_agent"]
            sub_agents_names = schema["sub_agents"]

            # Validate head agent
            try:
                head_agent = self.agents.agent_retrieval(head_agent_name)
                print(f"Head agent '{head_agent_name}' is valid.")
            except ValueError as e:
                logger.error(f"Head agent validation failed: {e}")
                return False

            # Validate sub-agents
            try:
                sub_agents = self.agents.agents_retrieval(sub_agents_names)
                print(f"Sub-agents '{sub_agents_names}' are valid.")
            except ValueError as e:
                logger.error(f"Sub-agent validation failed: {e}")
                return False

        elif self.agent_schema == "single_agent":
            schema = self.agent_schema["single_agent"]
            agent_name = schema["agent"]

            # Validate single agent
            try:
                agent = self.agents.agent_retrieval(agent_name)
                print(f"Single agent '{agent_name}' is valid.")
            except ValueError as e:
                logger.error(f"Single agent validation failed: {e}")
                return False

        else:
            logger.error(f"Unknown agent schema: {self.agent_schema}")
            return False

        return True


    def generate(self, prompt):
        MAX_RETRIES = 3
        retries = 0
        while retries < MAX_RETRIES:
            try:
                output = self.model(prompt=prompt)
                break
            except KeyError as e:
                print(f"Generation KeyError encountered: {e}. Retrying...")
                retries += 1

            except Exception as e:
                print(f"Generation An error occurred: {e}. Retrying...")
                retries += 1
        else:
            print("Maximum retries reached. Terminating execution.")
            self.stop()
        return output

    def single_agent(self,singel_agent:str) -> BaseAgent:
        try:
           agent = self.agents.agent_retrieval(singel_agent)
        except KeyError as ke:
            logger.error(f"Agent not found : {ke}")

        return agent

    def step(self,agent:BaseAgent
             ,agent_state:AgentState):
        agent_scratchpad = agent_state.agent_scratchpad()
        user_input = agent_state.user_input
        agent_history = agent_state.history()
        
        pass

    def s_call(self,
    agent: BaseAgent,
    agent_state: AgentState,
    callback: CallbackHandler,
    ) -> AgentState:
            
        action = Action(callback=callback)

        while agent_state.gate:

            step = self.step(scratchpad=agent_state.s_step(),agent=agent)
            response = action.response(step,callback)
            agent_state.update(response)
        
        return agent_state

    def m_call(self,
                head_agent: BaseAgent,
                sub_agents: BaseAgent,
                agent_state: AgentState,
                callback: CallbackHandler) -> AgentState:

        action = Action(callback=callback)

        while agent_state.gate:
            step = self.step(scratchpad=agent_state.s_step(),agent=head_agent)
            response = action.response(step)

            if response['action'] == 'agent_call':
                try :
                    sub_agent = self.agents.agent_retrieval(response['agent'])
                    sub_callback = CallbackHandler()
                    subagent_state = AgentState(agent=sub_agent,callback=callback)
                    subagent_state = self.s_call(agent=sub_agent,
                                                      agent_state=agent_state,
                                                      callback=callback)
                    response = subagent_state.final_output()
                except KeyError as ke:
                    logger.error(f"Agent not found : {ke}")
                    response = callback.agentcall_response(agent=response['agent'],inputs=response['inputs'],error=ke)
                agent_state.update(response)         
            else : 
                step = self.step(scratchpad=agent_state.s_step())
                response = action.response(step,callback)
                agent_state.update(response)

        return agent_state

    def execute(self,
                 user_input: str,
                   history: List[Dict]):

        if self.agent_validation():
            raise ValueError("Agent validation failed.")

        if self.agent_schema == "multi_agent":
            agents = self.agent_constructor.get_agents(self.agent_schema)
            head_agent = agents["head_agent"]
            sub_agents = agents["sub_agents"]

            callback = CallbackHandler()
            agent_state = AgentState(agent=head_agent,
                                            callback=callback,
                                            sub_agents=sub_agents,
                                              user_input=user_input,
                                                history=history)

            agent_state = self.m_call(head_agent, agent_state)
            final_output = agent_state.final_response()
            agent_history = agent_state.history()
            return final_output, agent_history

        elif self.agent_schema == "single_agent":
            agents = self.agent_constructor.get_agents(self.agent_schema)
            agent = agents["agent"]
            
            callback = CallbackHandler()
            agent_state = AgentState(agent=agent, callback=callback, user_input=user_input, history=history)

            agent_state = self.s_call(agent=agent, agent_state=agent_state, callback=callback)
            final_output = agent_state.final_response()
            return final_output, agent_state.history()

        else:
            logger.error(f"Executor Schema not found: {self.agent_schema}")
            return None    



class Action:
    def __init__(self,
                 tools: ToolVal | None,
                 agents: AgentVal | None,
                 packages: PackageVal | None,
                 ):
        self.tools = tools
        self.agents = agents
        self.packages = packages

    def action_def(self,action_,intermediate_state):
        action_n, action_t, action = action_

        step = True
        if action_t == "Final Action":
            step = False
            observation = self.final_call(action)
            intermediate_state.append({"Action_Type":action_t,"Action":action_n,"Observation":observation})
            return intermediate_state, step

        elif action_t == "Default":
            observation = self.default_call(action_n, action)
            intermediate_state.append({"Action_Type": action_t, "Action": action_n,"Input": action, "Observation": observation})
            return intermediate_state, step

        elif action_t == "Agent Action":
            name,action = self.agent_call(action_n,action)
            return self.agent_call(action_n, action), step

        elif action_t == "Package Action":
            package,tool = action_n
            observation = self.package_call(package,tool,action)
            intermediate_state.append({"Action_Type" : action_t, "Tool" : action_n,"Input": action, "Observation" : observation})
            #print(intermediate_state)
            return intermediate_state, step

        elif action_t == "Tool Action":
            observation = self.tool_call(action_n, action)
            intermediate_state.append({"Action_Type": action_t, "Tool": action_n,"Input": action, "Observation": observation})
            return intermediate_state, step

    def tool_call(self, name, action: dict):
        tool = self.tools.tool_retrival(name)
        tool_args = self.tools.tool_arguments(name)
        try:
            if tool_args.keys() == action.keys():
                try:
                   observation = tool.run(action)
                except Exception as e:
                    print(f"tool call error {e}. [line : 293]")
                    observation = f"Not able to run this tool."
                return str(observation)
            else:
                raise KeyError("Argument Mismatched Given by Agent")
        except Exception as e:
            print(f"{e} [line : 299]")
            observation = "Tool Arguments not matched - Reconsider"

    def package_call(self,package,tool,action : Dict):
        package_ = self.packages.package_retrival(package)
        action_keys = list(action.keys())
        if len(action_keys) == 0:
            tool_args = {}
            action = None
        else :
            tool_args = self.packages.tool_args(package_, tool)
        try :
            if tool_args == action_keys or action is None:
                try:
                   observation = package_().call(tool,action)
                except Exception as e:
                    print(f"package call error {e}. [line : 311]")
                    observation = "Not able to run this app."

                return  observation
            else :
                raise KeyError('Arguments are not matched!!')
        except KeyError as e:
            print("package call error. [line 318]")
            observation = "Arguments not matched - Reconsider"

    def agent_call(self, name, action):
        return name, action

    def default_call(self, name, action):
        if name == "parse":
            observation = "Problem Occurred In parsing - Reconsider The Action"
        else:
            observation = """Problem Occurred In Calling Name,
             You Have Missed Named Agent or Tool - Reconsider The Action"""
        return observation

    def final_call(self, action):
        observation = action
        return observation



agent_schema_multi = {"multi_agent":{'head_agent':"head_agent",'sub_agent':["names_of_subagents"]}}
agent_schema_single = {"single_agent":{'agent':"agent_name"}}

