"""
Base agent configuration for Deep Agents using LangChain patterns
Following the architecture documented in the repository
"""
from typing import List, Optional, Dict, Any
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import BaseTool
from config.settings import settings


class BaseDeepAgent:
    """Base class for Deep Agents with middleware support"""

    def __init__(
        self,
        name: str,
        system_prompt: str,
        model: str,
        tools: List[BaseTool],
        subagents: Optional[Dict[str, Any]] = None,
        max_iterations: int = 20,
        max_execution_time: Optional[float] = None,
    ):
        self.name = name
        self.system_prompt = system_prompt
        self.model = model
        self.tools = tools
        self.subagents = subagents or {}
        self.max_iterations = max_iterations
        self.max_execution_time = max_execution_time

        # Initialize LLM
        self.llm = ChatAnthropic(
            model=model,
            anthropic_api_key=settings.anthropic_api_key,
            temperature=0.7,
        )

        # Create agent
        self.agent_executor = self._create_agent()

    def _create_agent(self) -> AgentExecutor:
        """Create the agent executor with tools"""

        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # Create agent
        agent = create_structured_chat_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt,
        )

        # Create executor
        executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=self.max_iterations,
            max_execution_time=self.max_execution_time,
            handle_parsing_errors=True,
            return_intermediate_steps=True,
        )

        return executor

    async def run(self, input_text: str, chat_history: Optional[List] = None) -> Dict[str, Any]:
        """Run the agent with the given input"""
        result = await self.agent_executor.ainvoke({
            "input": input_text,
            "chat_history": chat_history or []
        })

        return result

    def get_tools(self) -> List[BaseTool]:
        """Get the tools available to this agent"""
        return self.tools


class TodoListMiddleware:
    """
    TodoList Middleware for agents
    Based on Deep Agents Middleware documentation
    """

    def __init__(self):
        self.todos: List[Dict[str, str]] = []

    def add_todo(self, task: str, status: str = "pending"):
        """Add a todo item"""
        self.todos.append({
            "task": task,
            "status": status,
        })

    def update_todo(self, index: int, status: str):
        """Update todo status"""
        if 0 <= index < len(self.todos):
            self.todos[index]["status"] = status

    def get_todos(self) -> List[Dict[str, str]]:
        """Get all todos"""
        return self.todos

    def format_todos(self) -> str:
        """Format todos as string"""
        if not self.todos:
            return "No todos yet."

        formatted = "Current todos:\n"
        for i, todo in enumerate(self.todos):
            status_icon = "✓" if todo["status"] == "completed" else "○"
            formatted += f"{i + 1}. [{status_icon}] {todo['task']} ({todo['status']})\n"

        return formatted


class FilesystemMiddleware:
    """
    Filesystem Middleware for agents
    Based on Deep Agents Middleware documentation
    """

    def __init__(self, base_path: str = "./data/agent_workspace"):
        self.base_path = base_path
        import os
        os.makedirs(base_path, exist_ok=True)

    async def read_file(self, file_path: str) -> str:
        """Read a file"""
        full_path = f"{self.base_path}/{file_path}"
        try:
            with open(full_path, "r") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

    async def write_file(self, file_path: str, content: str) -> str:
        """Write a file"""
        full_path = f"{self.base_path}/{file_path}"
        try:
            # Create directory if needed
            import os
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            with open(full_path, "w") as f:
                f.write(content)
            return f"File written successfully: {file_path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"

    async def list_files(self) -> List[str]:
        """List all files in workspace"""
        import os
        files = []
        for root, dirs, filenames in os.walk(self.base_path):
            for filename in filenames:
                rel_path = os.path.relpath(os.path.join(root, filename), self.base_path)
                files.append(rel_path)
        return files
