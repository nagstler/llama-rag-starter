"""Custom callbacks for capturing agent reasoning."""

from typing import Any, Dict, List, Optional
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentAction, AgentFinish


class AgentReasoningCallback(BaseCallbackHandler):
    """Callback handler to capture agent reasoning steps."""
    
    def __init__(self):
        self.steps = []
        self.current_step = {}
    
    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any) -> None:
        """Called when chain starts."""
        if "agent" in serialized.get("name", "").lower():
            self.steps.append({
                "type": "thinking",
                "content": "Analyzing your request..."
            })
    
    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> None:
        """Called when agent decides to use a tool."""
        self.current_step = {
            "type": "tool_decision",
            "tool": action.tool,
            "input": action.tool_input,
            "reasoning": f"I need to use the {action.tool} tool to find information about: {action.tool_input}"
        }
        self.steps.append(self.current_step)
    
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> None:
        """Called when tool starts."""
        tool_name = serialized.get("name", "Unknown Tool")
        self.steps.append({
            "type": "tool_execution",
            "tool": tool_name,
            "status": "running",
            "content": f"Searching for: {input_str}"
        })
    
    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """Called when tool ends."""
        if self.current_step:
            self.current_step["output"] = output
            self.steps.append({
                "type": "tool_result",
                "content": "Found relevant information. Processing..."
            })
    
    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> None:
        """Called when agent finishes."""
        self.steps.append({
            "type": "conclusion",
            "content": "Formulating response based on the information found..."
        })
    
    def get_steps(self) -> List[Dict[str, Any]]:
        """Get all captured steps."""
        return self.steps