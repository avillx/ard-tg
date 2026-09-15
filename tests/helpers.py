from typing import Any

from agent.tool import SafeTool


class FakeTool(SafeTool):
    """Test double for SafeTool that records executed args and returns a fixed result."""

    def __init__(self, name: str = "fake", description: str = "desc", schema: dict[str, Any] | None = None, result: str = "ok"):
        super().__init__(name=name, description=description, schema=schema or {"type": "object"})
        self.result = result
        self.executed_args: dict[str, Any] | None = None

    def _execute(self, args: dict[str, Any]) -> str:
        self.executed_args = args
        return self.result


class FailingTool(SafeTool):
    """Test double whose execution always raises."""

    def __init__(self, name: str = "boom"):
        super().__init__(name=name, description="d", schema={"type": "object"})

    def _execute(self, args: dict[str, Any]) -> str:
        raise RuntimeError("kaboom")