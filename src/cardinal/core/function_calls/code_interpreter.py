import logging
import os
import re

import json5
import matplotlib

from ..function_calls.code_kernel import CodeKernel


START_CODE = """
import signal
def _m6_code_interpreter_timeout_handler(signum, frame):
    raise TimeoutError("M6_CODE_INTERPRETER_TIMEOUT")
signal.signal(signal.SIGALRM, _m6_code_interpreter_timeout_handler)

def input(*args, **kwargs):
    raise NotImplementedError('Python input() function is disabled.')

import math
import re
import json

import seaborn as sns
sns.set_theme()

import matplotlib
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

import numpy as np
import pandas as pd

from sympy import Eq, symbols, solve
"""


class CodeInterpreter:
    def __init__(self):
        self.code_kernel = CodeKernel()

    # ensure Chinese font support, before launching app
    def fix_matplotlib_cjk_font_issue(self):
        local_ttf = os.path.join(
            os.path.abspath(os.path.join(matplotlib.matplotlib_fname(), os.path.pardir)), "fonts", "ttf", "simhei.ttf"
        )
        if not os.path.exists(local_ttf):
            logging.warning(
                f"Missing font file `{local_ttf}` for matplotlib. It may cause some error when using matplotlib."
            )

    # extract code from text
    def extract_code(self, text):
        # Match triple backtick blocks first
        triple_match = re.search(r"```[^\n]*\n(.+?)```", text, re.DOTALL)
        # Match single backtick blocks second
        single_match = re.search(r"`([^`]*)`", text, re.DOTALL)
        if triple_match:
            text = triple_match.group(1)
        elif single_match:
            text = single_match.group(1)
        else:
            try:
                text = json5.loads(text)["code"]
            except Exception:
                pass
        # If no code blocks found, return original text
        return text

    def code_interpreter(self, code: str, timeout=30, start_code=True):
        # convert action_input_list to code
        code = self.extract_code(code) + "\n"
        # add timeout
        if timeout:
            code = f"signal.alarm({timeout})\n{code}"
        # add start code
        if start_code:
            code = START_CODE + "\n" + code
        res_type, res = self.code_kernel.execute(code)
        return res if res_type == "image" else None


if __name__ == "__main__":
    ci = CodeInterpreter()
    image_b64 = ci.code_interpreter(
        [
            "```py\nimport matplotlib.pyplot as plt\n\n# 数据\ncountries = ['英军', '美军', '德军']\ntroops = [300000, 700000, 500000]\n\n# 绘制柱状图\nplt.bar(countries, troops)\nplt.xlabel('国家')\nplt.ylabel('军力（万）')\nplt.title('各国军力')\nplt.show()\n```\n"
        ]
    )
    print("res:\n", image_b64)
