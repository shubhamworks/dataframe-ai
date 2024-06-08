import os
import pandas as pd

from dotenv import load_dotenv
from jinja2 import Environment, BaseLoader
from openai import OpenAI

MODEL_NAME = "gpt-3.5-turbo"
prompt_template_path = os.path.join(os.path.dirname(__file__), "prompt.tmpl")
SYSTEM_PROMPT = open(prompt_template_path, "r").read().strip()
load_dotenv()

def parse_response(response):
    response = response.strip()
    result_code = None
    current_code = []
    code_block = False

    for line in response.split("\n"):
        if line.startswith("```py"):
            code_block = not code_block
        elif line.startswith("```"):
            code_block = not code_block
        else:
            if code_block:
                current_code.append(line)

    if current_code:
        result_code = "\n".join(current_code)

    return result_code

def run_code(code_block, scope):
    exec(code_block, scope)

class Agent:
    def __init__(
        self,
        df: pd.DataFrame,
        description: str = None
    ):
        self.df = df
        self.description = description
        self.initial_setup()

    def initial_setup(self):
        self.df_size = self.df.shape
        self.sample_df = self.df.sample(n=3).to_string()
        self.client = OpenAI()
        self.system_prompt = self.prepare_system_prompt()

    def prepare_system_prompt(self):
        env = Environment(loader=BaseLoader())
        template = env.from_string(SYSTEM_PROMPT)
        template = template.render(
            dataframe_description = self.description, 
            dataframe_size=self.df_size, 
            sample_df=self.sample_df
        )
        return template

    def query(self, prompt):
        response = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        response = response.choices[0].message.content
        code_block = parse_response(response)

        exec_scope = {'df': self.df}
        run_code(code_block, exec_scope)

        response = {
            "code_block": code_block,
            "result": exec_scope["result"]
        }
        return response
