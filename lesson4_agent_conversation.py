from rich import print
from rich.prompt import Prompt
from agents import (Agent, Runner, AsyncOpenAI, OpenAIResponsesModel,
                    RunConfig, RunContextWrapper, function_tool, Model, ModelSettings)
from pydantic import BaseModel, Field

class UserInfo(BaseModel):
    name: str = Field(..., description='User name')
    location: str = Field(..., description='User location')
    occupation: str = Field(..., description='User occupation')

@function_tool
def get_user_info(wrapper: RunContextWrapper[UserInfo]) -> UserInfo:
    """Get user information."""
    user_name = wrapper.context.name
    user_location = wrapper.context.location
    user_occupation = wrapper.context.occupation
    return f'User name: {user_name}, User location: {user_location}, User occupation: {user_occupation}'

context = UserInfo(
    name='Pakagrong',
    location='Chiang Mai',
    occupation='Full-Stack Developer',
)

llm_model = OpenAIResponsesModel(model='gpt-4o-mini', openai_client=AsyncOpenAI())

my_agent = Agent(
    name='My agent',
    model=llm_model,
    output_type=str, 
    tools=[get_user_info]
)

conversation = []

while True:
    user_input = Prompt.ask("User")
    if user_input.lower() == 'exit' or user_input.lower() == 'quit':
        raise Exception("Exiting the conversation.")

    conversation.append({"role": "user", "content": user_input})

    response = Runner.run_sync(
        starting_agent=my_agent,
        input=conversation,
        max_turns=3,
        context=context,
        run_config=RunConfig(
            model='gpt-4',
            model_settings=ModelSettings(temperature=0.4, parallel_tool_calls=True),
            workflow_name='JJ Workflow'
        )
    )
    print(response.final_output)

    conversation = response.to_input_list()