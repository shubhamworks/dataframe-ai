import inspect
from typing import Any, Callable, List

class Tools:
    func: Callable[..., Any]
    name: str
    doc: str
    signature: inspect.Signature
    registry: List['Tools'] = []  # Class attribute to store all instances

    def __init__(self, func: Callable[..., Any]) -> None:
        self.func = func
        self.name = func.__name__
        self.doc = func.__doc__
        if not self.doc:
            raise ValueError("Function must have a docstring")
        self.signature = inspect.signature(func)
        Tools.registry.append(self)  # Add this instance to the registry

    def __call__(self, *args, **kwargs) -> Any:
        return self.func(*args, **kwargs)

    def __str__(self) -> str:
        return f"""
def {self.name}{self.signature}:
    \"\"\"{self.doc}\"\"\"
"""

def tools(func: Callable[..., Any]) -> Tools:
    return Tools(func)