from rich import print
from agents import Agent, Runner, function_tool
from pydantic import BaseModel

class OutpuType(BaseModel):
    api_key: str

@function_tool
def get_aws_api_key() -> str:
    return 'AWS12345678'

@function_tool
def get_gcp_api_key() -> str:
    return 'GCP12345678'


aws_agent = Agent(
    name="AWS API Key Gatekeeper Agent",
    model='gpt-4o-mini',
    instructions='You are equipped with function to retrieve AWS API key',
    tools=[get_aws_api_key],
)

gcp_agent = Agent(
    name="GCP API Key Gatekeeper Agent",
    model='gpt-4o-mini',
    instructions='You are equipped with function to retrieve GCP API key',
    tools=[get_gcp_api_key],
)

agent = Agent(
    name='My Agent',
    instructions='Always response in one sentence',
    model='gpt-4o-mini',
    output_type=OutpuType, # structured output
    tools=[
        aws_agent.as_tool(
            tool_name='aws_api_key_agent_tool',
            tool_description='Get the AWS API key from the AWS agent',
        ),
        gcp_agent.as_tool(
            tool_name='gcp_api_key_agent_tool',
            tool_description='Get the GCP API key from the GCP agent',
        ),
    ],
)

response = Runner.run_sync(
    starting_agent=agent,
    input='Can you please retrieve my AWS API key?'
)
print(response.final_output)

for raw_response in response.raw_responses:
    print(raw_response)