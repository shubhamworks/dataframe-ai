import os
import pathlib
from os.path import abspath, dirname, join

current_dir = dirname(abspath(__file__))
prompt_paths = list(pathlib.Path(join(current_dir)).glob('*.jinja2')) # includes hidden files

all_prompts = {}
for pp in prompt_paths:
    filename = os.path.splitext(os.path.basename(pp))[0]
    with open(pp, 'r') as file:
        all_prompts[filename] = file.read()

def get_prompts():
    return all_prompts