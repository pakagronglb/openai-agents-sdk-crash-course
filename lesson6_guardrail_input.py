import asyncio
from typing import List, Union
from pydantic import BaseModel, Field
from agents import (Agent, GuardrailFunctionOutput, InputGuardrailTripwireTriggered, RunContextWrapper, 
                    Runner,AsyncOpenAI, OpenAIResponsesModel, TResponseInputItem, input_guardrail, 
                    function_tool)

llm_model = OpenAIResponsesModel(model='gpt-4o-mini', openai_client=AsyncOpenAI())

class GuardrailOutput(BaseModel):
    """Model for guardrail output."""
    is_python_question: bool = Field(
        ..., description="Is the question related to Python programming?"
    )
    reasoning: str = Field(
        ..., description="Reasoning behind the classification."
    )

guardrail_agent = Agent(
    name="Guardrail Agent",
    model=llm_model,
    instructions='Check if the question is related to Python programming.',
    output_type=GuardrailOutput,
)

@input_guardrail
async def python_guardrail(
    ctx: RunContextWrapper[None], 
    agent: Agent, 
    input: Union[str, List[TResponseInputItem]]
) -> GuardrailFunctionOutput:
    """Guardrail function to check if the input is a Python-related question."""
    print('Guardrail ctx:', ctx)
    print('Agent:', agent.name)
    print('Input:', input)

    result = await Runner.run(guardrail_agent, input, context=ctx.context)

    print('Guardrail result:', result.final_output)

    return GuardrailFunctionOutput(
        output_info=result.final_output, 
        tripwire_triggered=result.final_output.is_python_question
    )

@function_tool
def function_tool_call_simulator() -> str:
    """Simulate a function tool call."""
    print('------------>Function tool called!')
    return "Function tool called!"

agent = Agent(
    name="Customer Support Agent",
    model=llm_model,
    instructions="You are a customer support agent. Only help customers with their questions.",
    input_guardrails=[python_guardrail],
    tools=[function_tool_call_simulator],
)

async def main():
    """Main function to run the agent."""
    try:
        await Runner.run(agent, "Call the function_tool_call_simulator, and tell me how do you write a hello world program in Python")
        print("Guardrail didn't trip - this is unexpected")
    except InputGuardrailTripwireTriggered:
        print('---' * 20)
        print('Python guardrail tripwire triggered')


if __name__ == "__main__":
    asyncio.run(main())