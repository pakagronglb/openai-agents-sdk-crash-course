import asyncio
from rich import print
from agents import (Agent, Runner, AsyncOpenAI, OpenAIResponsesModel, function_tool)

llm_model = OpenAIResponsesModel(model='gpt-4o-mini', openai_client=AsyncOpenAI())

@function_tool
async def funcA():
    print('Function A started')
    await asyncio.sleep(10)
    print('Function A finished')
    return "This is function A."

@function_tool
async def funcB():
    print('Function B started')
    await asyncio.sleep(5)
    print('Function B finished')
    return "This is function B."

user_facing_agent = Agent(
    name='My agent',
    model=llm_model,
    output_type=str,
    tools=[funcA, funcB],
)

async def main():
    response = await Runner.run(
        starting_agent=user_facing_agent,
        input='Call funcA and funcB.',
    )
    return response.final_output

asyncio.run(main())