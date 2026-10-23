import json
import subprocess
from internal.tools.interface import BaseTool

MAX_OUTPUT_LEN = 8000

class BashTool(BaseTool):
    def __init__(self, work_dir: str):
        self.work_dir = work_dir

    def name(self) -> str:
        return "bash"

    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": self.name(),
                "description": "在工作目录执行bash命令",
                "parameters": {
                    "type": "object",
                    "required": ["command"],
                    "properties": {"command": {"type": "string"}}
                }
            }
        }

    def execute(self, args: str) -> str:
        try:
            input_args = json.loads(args)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"参数解析失败: {e}") from e

        cmd = input_args["command"]
        try:
            proc = subprocess.run(
                ["bash", "-c", cmd],
                cwd=self.work_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
        except subprocess.TimeoutExpired as e:
            out = e.stdout if e.stdout else ""
            err = e.stderr if e.stderr else ""
            total = out + err
            total += "\n[警告: 命令执行超时(30s)，已被系统强制终止。]"
            return self._truncate(total)

        combined = proc.stdout + proc.stderr
        if proc.returncode != 0:
            result = f"执行报错: exit status {proc.returncode}\n输出:\n{combined}"
        else:
            if not combined.strip():
                result = "命令执行成功，无终端输出。"
            else:
                result = combined
        return self._truncate(result)

    def _truncate(self, text: str) -> str:
        if len(text) > MAX_OUTPUT_LEN:
            return text[:MAX_OUTPUT_LEN] + f"\n...[输出截断，超过{MAX_OUTPUT_LEN}字符]"
        return text