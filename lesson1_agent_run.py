import asyncio
from rich import print
from openai.types.responses import ResponseTextDeltaEvent
from agents import (Agent, Runner, AsyncOpenAI, OpenAIResponsesModel, RunConfig)

llm_model = OpenAIResponsesModel(model='gpt-4o-mini', openai_client=AsyncOpenAI())

user_facing_agent = Agent(
    name='User Interaction Agent',
    model=llm_model,
    output_type=str,
    instructions='You are a user-facing agent. Your job is to interact with the user and help them their tasks.',
)

response = Runner.run_sync(
    starting_agent=user_facing_agent,
    input='What is the capital of Japan?',
    run_config=RunConfig(model='gpt-4o-mini', tracing_disabled=True)
)

print('Token Usage', response.raw_responses[0].usage, '')
print(f'{response.last_agent.name}:\n{response.final_output}')


async def main():
    response = await Runner.run(
        starting_agent=user_facing_agent,
        input='What is the capital of Japan?'
    )

    print('Token Usage', response.raw_responses[0].usage, '')

    print(f'{response.last_agent.name}:\n{response.final_output}')

asyncio.run(main())

async def run_stream():
    result = Runner.run_streamed(
        starting_agent=user_facing_agent,
        input='Give me the instruction how to make boba tea',
    )
    
    async for stream_response in result.stream_events():
        if stream_response.type == 'raw_response_event' and isinstance(stream_response.data, ResponseTextDeltaEvent):
            print(stream_response.data.delta, end='', flush=True)

asyncio.run(run_stream())