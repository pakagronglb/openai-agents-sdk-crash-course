import asyncio
import random
from typing import Any
from rich import print
from agents import Agent, RunContextWrapper, RunHooks, Runner, Tool, Usage, function_tool
from pydantic import BaseModel

class MyAgentHooks(RunHooks):
    def __init__(self):
        self.event_counter = 0

    def _usage_to_str(self, usage: Usage) -> str:
        """Convert usage statistics to a string."""
        return (f"{usage.requests} requests, {usage.input_tokens} input tokens, "
                f"{usage.output_tokens} output tokens, {usage.total_tokens} total tokens")

    async def on_agent_start(self, context: RunContextWrapper, agent: Agent) -> None:
        """Handle agent start event."""
        self.event_counter += 1
        print('On Agent Start Event fired')
        print(f"### {self.event_counter}: Agent {agent.name} started. "
              f"Usage: {self._usage_to_str(context.usage)}")

    async def on_agent_end(self, context: RunContextWrapper, agent: Agent, output: Any) -> None:
        """Handle agent end event."""
        self.event_counter += 1
        print('On Agent End Event fired')
        print(f"### {self.event_counter}: Agent {agent.name} ended with output {output}. "
              f"Usage: {self._usage_to_str(context.usage)}")

    async def on_tool_start(self, context: RunContextWrapper, agent: Agent, tool: Tool) -> None:
        """Handle tool start event."""
        self.event_counter += 1
        print('On Tool Start Event fired')
        print(f"### {self.event_counter}: Tool {tool.name} started. "
              f"Usage: {self._usage_to_str(context.usage)}")

    async def on_tool_end(
        self, context: RunContextWrapper, agent: Agent, tool: Tool, result: str
    ) -> None:
        """Handle tool end event."""
        self.event_counter += 1
        print('On Tool End Event fired')
        print(f"### {self.event_counter}: Tool {tool.name} ended with result {result}. "
              f"Usage: {self._usage_to_str(context.usage)}")

    async def on_handoff(
        self, context: RunContextWrapper, from_agent: Agent, to_agent: Agent
    ) -> None:
        """Handle handoff event."""
        self.event_counter += 1
        print('On Handoff Event fired')
        print(f"### {self.event_counter}: Handoff from {from_agent.name} to {to_agent.name}. "
              f"Usage: {self._usage_to_str(context.usage)}")

my_agent_hooks = MyAgentHooks()

@function_tool
def random_number(max: int) -> int:
    """Generate a random number up to the provided max."""
    return random.randint(0, max)

@function_tool
def multiply_by_two(x: int) -> int:
    """Return x times two."""
    return x * 2

class FinalResult(BaseModel):
    number: int


multiply_agent = Agent(
    name="Multiply Agent",
    model='gpt-4o-mini',
    instructions="Multiply the number by 2 and then return the final result.",
    tools=[multiply_by_two],
    output_type=FinalResult,
)

start_agent = Agent(
    name="My Agent",
    model='gpt-4o-mini',
    instructions=("Generate a random number. If it's even, stop. If it's odd, "
                  "hand off to the multipler agent."),
    tools=[random_number],
    output_type=FinalResult,
    handoffs=[multiply_agent],
)

async def main() -> None:
    """Main function to run the agent."""
    user_input = input("Enter a max number: ")
    await Runner.run(
        start_agent,
        hooks=my_agent_hooks,
        input=f"Generate a random number between 0 and {user_input}.",
    )

    print("Agent run completed")


if __name__ == "__main__":
    asyncio.run(main())