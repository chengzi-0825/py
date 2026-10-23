from internal.tools.interface import BaseTool, Registry
from internal.schema.message import ToolCall, ToolResult, ToolDefinition

class RegistryImpl(Registry):
    def __init__(self):
        self.tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        # 职责1：动态挂载 Register
        tool_name = tool.name()
        if tool_name in self.tools:
            print(f"[Warning] 工具 '{tool_name}' 已经被注册，将被覆盖。")
        self.tools[tool_name] = tool
        print(f"[Registry] 成功挂载工具: {tool_name}")

    def get_available_tools(self) -> list[ToolDefinition]:
        # 职责2：描述暴露 Expose Schema
        return [tool.definition() for tool in self.tools.values()]

    def execute(self, call: ToolCall) -> ToolResult:
        # 职责3：路由分发与执行 Dispatch & Execute
        if call.name not in self.tools:
            return ToolResult(
                tool_call_id=call.id,
                content=f"错误：工具 {call.name} 不存在",
                is_error=True
            )
        tool = self.tools[call.name]
        try:
            output = tool.execute(call.arguments)
            return ToolResult(
                tool_call_id=call.id,
                content=output,
                is_error=False
            )
        except Exception as e:
            return ToolResult(
                tool_call_id=call.id,
                content=f"工具执行异常：{str(e)}",
                is_error=True
            )