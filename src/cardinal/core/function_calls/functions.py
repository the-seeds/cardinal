from ..schema import FunctionAvailable, FunctionCall
from ..function_calls.code_interpreter import CodeInterpreter
from typing import List, Any


CI = FunctionAvailable(function={
    'name': 'code_interpreter',
    'description': 'interpreter for code, which use for executing python code',
    'parameters': [{
        'type': 'string',
        'properties': {
            "code": {
                "type": "string",
                "description": "the code to be executed, which Enclose the code within triple backticks (```) at the beginning and end of the code."
            }
        }
    }],
    'args_format': 'code'
})


def parse_function_availables(question: str) -> List[FunctionAvailable]:
    tools = []
    if "/code" in question:
        question = question.replace("/code", "")
        tools.append(CI)
    return question, tools


def execute_function_calls(function_calls: List[FunctionCall]) -> List[Any]:
    response = []
    for function_call in function_calls:
        if function_call.function.name == 'code_interpreter':
            response.append(CodeInterpreter().code_interpreter(
                function_call.arguments.code))
    return response
