import json
import os
from internal.tools.interface import BaseTool
from internal.schema.message import ToolDefinition

class WriteFileTool(BaseTool):
    def __init__(self, work_dir: str):
        self.work_dir = work_dir

    def name(self) -> str:
        return "write_file"

    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name=self.name(),
            description="创建或覆盖写入一个文件。如果目录不存在会自动创建。请提供相对于工作区的相对路径。",
            input_schema={
                "type": "object",
                "required": ["path", "content"],
                "properties": {
                    "path": {"type": "string", "description": "相对于工作区的文件路径"},
                    "content": {"type": "string", "description": "要写入的文件内容"}
                }
            },
        )

    def execute(self, args: str) -> str:
        try:
            input_args = json.loads(args)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"参数解析失败: {e}") from e

        path = input_args["path"]
        content = input_args["content"]
        full_path = os.path.join(self.work_dir, path)
        parent_dir = os.path.dirname(full_path)
        os.makedirs(parent_dir, exist_ok=True)

        try:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            raise RuntimeError(f"写入文件失败: {e}") from e

        return f"成功将内容写入到文件: {full_path}"