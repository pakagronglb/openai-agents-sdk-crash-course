from agents import Agent, AgentHooks, Runner

class MyAgentHooks(AgentHooks):
    async def on_start(self, context, agent):
        print('On start hook event triggered.')
        print(f"Agent {agent.name} is starting...")

    async def on_end(self, context, agent, result):
        print('On end hook event triggered.')
        print(f"Agent {agent.name} has finished.")
        

agent = Agent(
    name="SupportAgent",
    model='gpt-4o-mini',
    instructions="Help customers with support issues.",
    hooks=MyAgentHooks(),
)

response = Runner.run_sync(agent, "Where is Toyota's HQ?")