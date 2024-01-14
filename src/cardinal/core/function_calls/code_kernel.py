import os
from pprint import pprint
import queue
import re
from subprocess import PIPE

import jupyter_client
from PIL import Image

# make sure run "ipython kernel install --name code_kernel --user" before using code kernel
IPYKERNEL = os.environ.get('IPYKERNEL', 'code_kernel')


class CodeKernel(object):
    def __init__(self,
                 kernel_name='kernel',
                 kernel_id=None,
                 kernel_config_path="",
                 python_path=None,
                 ipython_path=None,
                 init_file_path="./startup.py",
                 verbose=1):
        self.kernel_name = kernel_name
        self.kernel_id = kernel_id
        self.kernel_config_path = kernel_config_path
        self.python_path = python_path
        self.ipython_path = ipython_path
        self.init_file_path = init_file_path
        self.verbose = verbose

        if python_path is None and ipython_path is None:
            env = None
        else:
            env = {"PATH": self.python_path + ":$PATH",
                   "PYTHONPATH": self.python_path}

        # Initialize the backend kernel
        self.kernel_manager = jupyter_client.KernelManager(kernel_name=IPYKERNEL,
                                                           connection_file=self.kernel_config_path,
                                                           exec_files=[
                                                               self.init_file_path],
                                                           env=env)
        if self.kernel_config_path:
            self.kernel_manager.load_connection_file()
            self.kernel_manager.start_kernel(stdout=PIPE, stderr=PIPE)
            print("Backend kernel started with the configuration: {}".format(
                self.kernel_config_path))
        else:
            self.kernel_manager.start_kernel(stdout=PIPE, stderr=PIPE)
            print("Backend kernel started with the configuration: {}".format(
                self.kernel_manager.connection_file))

        if verbose:
            pprint(self.kernel_manager.get_connection_info())

        # Initialize the code kernel
        self.kernel = self.kernel_manager.blocking_client()
        # self.kernel.load_connection_file()
        self.kernel.start_channels()
        print("Code kernel started.")

    def _execute(self, code):
        self.kernel.execute(code)
        try:
            shell_msg = self.kernel.get_shell_msg(timeout=30)
            io_msg_content = self.kernel.get_iopub_msg(timeout=30)['content']
            while True:
                msg_out = io_msg_content
                # Poll the message
                try:
                    io_msg_content = self.kernel.get_iopub_msg(timeout=30)[
                        'content']
                    if 'execution_state' in io_msg_content and io_msg_content['execution_state'] == 'idle':
                        break
                except queue.Empty:
                    break

            return shell_msg, msg_out
        except Exception as e:
            print(e)
            return None, None

    def clean_ansi_codes(self, input_string):
        ansi_escape = re.compile(r'(\x9B|\x1B\[|\u001b\[)[0-?]*[ -/]*[@-~]')
        return ansi_escape.sub('', input_string)

    def execute(self, code) -> tuple[str, str | Image.Image]:
        res = ""
        res_type = None
        code = code.replace("<|observation|>", "")
        code = code.replace("<|assistant|>interpreter", "")
        code = code.replace("<|assistant|>", "")
        code = code.replace("<|user|>", "")
        code = code.replace("<|system|>", "")
        msg, output = self._execute(code)
        if not msg and not output:
            return res_type, 'no output'

        if msg['metadata']['status'] == "timeout":
            return res_type, 'Timed out'
        elif msg['metadata']['status'] == 'error':
            return res_type, self.clean_ansi_codes('\n'.join(self.get_error_msg(msg, verbose=True)))

        if 'text' in output:
            res_type = "text"
            res = output['text']
        elif 'data' in output:
            for key in output['data']:
                if 'text/plain' in key:
                    res_type = "text"
                    res = output['data'][key]
                elif 'image/png' in key:
                    res_type = "image"
                    res = output['data'][key]
                    break

        if res_type == "text" or res_type == "traceback":
            res = res

        return res_type, res

    def get_error_msg(self, msg, verbose=False) -> str | None:
        if msg['content']['status'] == 'error':
            try:
                error_msg = msg['content']['traceback']
            except:
                try:
                    error_msg = msg['content']['traceback'][-1].strip()
                except:
                    error_msg = "Traceback Error"
            if verbose:
                print("Error: ", error_msg)
            return error_msg
        return None

    def shutdown(self):
        # Shutdown the backend kernel
        self.kernel_manager.shutdown_kernel()
        print("Backend kernel shutdown.")
        # Shutdown the code kernel
        self.kernel.shutdown()
        print("Code kernel shutdown.")

    def restart(self):
        # Restart the backend kernel
        self.kernel_manager.restart_kernel()
        # print("Backend kernel restarted.")

    def interrupt(self):
        # Interrupt the backend kernel
        self.kernel_manager.interrupt_kernel()
        # print("Backend kernel interrupted.")

    def is_alive(self):
        return self.kernel.is_alive()


if __name__ == "__main__":
    ck = CodeKernel()
    # shell_msg, msg_out = ck.execute("print('hello world')")
    res_type, res = ck.execute(
        '''import matplotlib.pyplot as plt\n\n# 数据\ncountries = ['英军', '美军', '德军']\ntroops = [300000, 700000, 500000]\n\n# 绘制柱状图\nplt.bar(countries, troops)\nplt.xlabel('国家')\nplt.ylabel('军力（万）')\nplt.title('各国军力')\nplt.show()''', CodeKernel())
    print("res_type:\n", res_type, "\n")
    print("res:\n", res, "\n")
