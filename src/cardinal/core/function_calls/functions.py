from typing import List

from ..function_calls.code_interpreter import CodeInterpreter
from ..schema import FunctionAvailable, FunctionCall


# function description

CI = FunctionAvailable(
    function={
        "name": "code_interpreter",
        "description": "interpreter for code, which use for executing python code",
        "parameters": {
            "type": "string",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "the code to be executed, which Enclose the code within triple backticks (```) at the beginning and end of the code.",
                }
            },
            "required": ["code"],
        },
    }
)

GET_RIVER_ENVIRONMENT = FunctionAvailable(
    function={
        "name": "get_river_environment",
        "description": "get river environment at a specific location",
        "parameters": {
            "type": "string",
            "properties": {
                "river": {
                    "type": "string",
                    "description": "the river name to be queried",
                },
                "location": {"type": "string", "description": "the location of the river environment to be queried"},
            },
            "required": ["river", "location"],
        },
    }
)

GET_ENVIRONMENT_AIR = FunctionAvailable(
    function={
        "name": "get_environment_air",
        "description": "get environment air at a specific location",
        "parameters": {
            "type": "string",
            "properties": {
                "location": {"type": "string", "description": "the location of the environment air to be queried"}
            },
            "required": ["location"],
        },
    }
)


def parse_function_availables(question: str) -> List[FunctionAvailable]:
    tools = []
    if "/code" in question:
        question = question.replace("/code", "")
        tools.append(CI)
    if "/get_river_environment" in question:
        question = question.replace("/get_river_environment", "")
        tools.append(GET_RIVER_ENVIRONMENT)
    if "/get_environment_air" in question:
        question = question.replace("/get_environment_air", "")
        tools.append(GET_ENVIRONMENT_AIR)
    return question, tools


def execute_function_call(function_call: FunctionCall):
    response = None
    if function_call.name == "code_interpreter":
        response = CodeInterpreter().code_interpreter(**function_call.arguments)
    if function_call.name == "get_river_environment":
        response = str(function_call.arguments)
    if function_call.name == "get_environment_air":
        response = str(function_call.arguments)
    return response
