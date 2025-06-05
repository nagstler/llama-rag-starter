"""Base classes for LangChain agents and tools."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool
from .callbacks import AgentReasoningCallback


class BaseTool(ABC):
    """Standard interface for agent tools."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def run(self, *args, **kwargs) -> str:
        """Execute the tool and return result."""
        pass
    
    def to_langchain_tool(self) -> Tool:
        """Convert to LangChain Tool format."""
        return Tool(
            name=self.name,
            description=self.description,
            func=self.run
        )


class BaseAgent(ABC):
    """Abstract base class for all agents."""
    
    def __init__(
        self, 
        name: str, 
        description: str,
        model_name: str = "gpt-4",
        temperature: float = 0,
        verbose: bool = True
    ):
        self.name = name
        self.description = description
        self.tools: List[BaseTool] = []
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="output"  # Explicitly set output key
        )
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature
        )
        
        self.verbose = verbose
        self.agent_executor: Optional[AgentExecutor] = None
    
    def add_tool(self, tool: BaseTool):
        """Add a tool to the agent's toolkit."""
        self.tools.append(tool)
        # Rebuild agent executor when tools change
        self._build_agent()
    
    def _build_agent(self):
        """Build the agent executor with current tools."""
        if not self.tools:
            return
        
        # Convert tools to LangChain format
        langchain_tools = [tool.to_langchain_tool() for tool in self.tools]
        
        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create agent
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=langchain_tools,
            prompt=prompt
        )
        
        # Create executor
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=langchain_tools,
            memory=self.memory,
            verbose=self.verbose,
            max_iterations=5,
            handle_parsing_errors=True,
            return_intermediate_steps=True  # Important for capturing reasoning
        )
    
    @abstractmethod
    def _get_system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        pass
    
    def process(self, query: str) -> Dict[str, Any]:
        """Process a user query and return response with reasoning steps."""
        if not self.agent_executor:
            return {
                "response": "Agent not initialized. Please add tools first.",
                "steps": []
            }
        
        try:
            # Create callback to capture reasoning
            callback = AgentReasoningCallback()
            
            # Process with callback
            result = self.agent_executor.invoke(
                {"input": query},
                callbacks=[callback]
            )
            
            # Get captured steps
            steps = callback.get_steps()
            
            # If no steps captured by callback, try to extract from intermediate steps
            if not steps and "intermediate_steps" in result:
                steps.append({
                    "type": "thinking",
                    "content": "Analyzing your request..."
                })
                
                for action, observation in result["intermediate_steps"]:
                    steps.append({
                        "type": "tool_decision",
                        "tool": action.tool,
                        "input": str(action.tool_input),
                        "reasoning": f"Using {action.tool} to search for: {action.tool_input}"
                    })
                    steps.append({
                        "type": "tool_result",
                        "content": "Found relevant information"
                    })
                
                steps.append({
                    "type": "conclusion",
                    "content": "Formulating response based on findings..."
                })
            
            # Ensure we always have some steps to show agent is working
            if not steps:
                steps = [
                    {"type": "thinking", "content": "Processing your request..."},
                    {"type": "conclusion", "content": "Response prepared."}
                ]
            
            return {
                "response": result.get("output", "No response generated"),
                "steps": steps
            }
        except Exception as e:
            return {
                "response": f"Error processing query: {str(e)}",
                "steps": []
            }
    
    def clear_memory(self):
        """Clear conversation memory."""
        self.memory.clear()