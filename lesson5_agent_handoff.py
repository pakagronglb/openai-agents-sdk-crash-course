from rich import print
from rich.prompt import Prompt
from agents import (Agent, Runner, AsyncOpenAI, OpenAIResponsesModel, 
                    RunContextWrapper, handoff, function_tool)
from pydantic import BaseModel, Field

llm_model = OpenAIResponsesModel(model='gpt-4o-mini', openai_client=AsyncOpenAI())

class RefundReason(BaseModel):
    reason: str = Field(..., description='Reason for the refund')

def on_handoff_trigger(ctx: RunContextWrapper, input_data: RefundReason) -> None:
    print('Handoff called')
    print('CTX:', ctx)
    print('Input:', input_data)

@function_tool
def refund_status() -> bool:
    """Check if the refund is issued."""
    return 'refund issued'

@function_tool
def check_balance_due() -> float:
    """Check the balance due."""
    return 100.0

refund_agent = Agent(
    name='Refund agent',
    instructions='You are an agent that checks the refund status.',
    model=llm_model,
    output_type=str,  
    tools=[refund_status],
)

balance_due_agent = Agent(
    name='Balance Due agent',
    instructions='You are an agent that checks the balance due.',
    model=llm_model,
    output_type=str,  
    tools=[check_balance_due],
)

my_agent = Agent(
    name='Customer agent',
    instructions='You are a customer service agent.',
    model=llm_model,
    output_type=str,
    handoffs=[
        handoff(
            agent=refund_agent,
            on_handoff=on_handoff_trigger,
            input_type=RefundReason
        )
    ]
)

balance_due_agent.handoffs.append(my_agent)
balance_due_agent.handoffs.append(refund_agent)

refund_agent.handoffs.append(my_agent)
refund_agent.handoffs.append(balance_due_agent)

conversation = []
active_agent = my_agent

while True:
    user_input = Prompt.ask("User")
    if user_input.lower() == 'exit' or user_input.lower() == 'quit':
        raise Exception("Exiting the conversation.")

    conversation.append({"role": "user", "content": user_input})

    response = Runner.run_sync(
        starting_agent=active_agent,
        input=conversation,
    )
    
    active_agent = response.last_agent
    conversation = response.to_input_list()

    print(f'{active_agent.name}:')
    print(response.final_output)