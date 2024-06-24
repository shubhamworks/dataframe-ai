import os
import pandas as pd

from dotenv import load_dotenv
from jinja2 import Environment, BaseLoader
from openai import OpenAI
from typing import List, Union

from dataframeai.tools import Tools
from dataframeai.utils import parser
from dataframeai.prompts.prompt_loader import get_prompts

MODEL_NAME = "gpt-4-turbo"
load_dotenv()

def run_code(code_block, scope):
    exec(code_block, scope)

class Agent:
    def __init__(
        self,
        dfs: List[pd.DataFrame],
        role: str = None
    ):
        self.context = {
            "dfs": dfs,
            "role": role,
            "fn_tools": [],
            "last_query": None,
            "last_code": None,
            "last_result": None
        }
        self.client = OpenAI()
        self.prompts = get_prompts()

    def add_tools(self, tools: Union[Tools, List[Tools]]):
        if isinstance(tools, Tools):
            if tools not in self.context["fn_tools"]:
                self.context["fn_tools"].append(tools)
        else:
            for tool in tools:
                if tool not in self.context["fn_tools"]:
                    self.context["fn_tools"].extend(tools)
    
    def render(self, json_data, prompt: str):
        environment = Environment(loader=BaseLoader())
        prompt = environment.from_string(self.prompts[prompt])
        prompt = prompt.render(json_data)
        return prompt
    
    def refine_prompt(self, prompt):
        prompt = self.render({'context': self.context, 'query': prompt}, 'reflect_query')
        response = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    
    def query(self, prompt, history=True, refine=False, full_response=False):
        if refine:
            prompt = self.refine_prompt(prompt)
            
        prompt = self.render({'context': self.context, 'query': prompt}, 'generate_python_code')
        response = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        model_response = response.choices[0].message.content
        code_block = parser.parse_python_code(model_response)
        print(code_block)

        exec_scope = {'dfs': self.context["dfs"]}
        run_code(code_block, exec_scope)

        # Update the generated result as last values
        self.context["last_query"] = prompt
        self.context["last_code"] = code_block
        self.context["last_result"] = exec_scope["result"]["value"]

        if full_response:
            response = {
                "prompt": prompt,
                "code_block": code_block,
                "result": exec_scope["result"],
                "model_response": model_response
            }
        else:
            response = exec_scope["result"]["value"]
        return response
