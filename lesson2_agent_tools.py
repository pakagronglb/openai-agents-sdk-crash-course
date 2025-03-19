from typing import Literal
from rich import print
from agents import (Agent, Runner, AsyncOpenAI, OpenAIResponsesModel, 
                    FunctionTool, WebSearchTool, FileSearchTool, function_tool)
from pydantic import BaseModel, Field
from duckduckgo_search import DDGS

class SearchResult(BaseModel):
    title: str = Field(..., description='Title of the search result')
    link: str = Field(..., description='Link to the search result')
    snippet: str = Field(..., description='Snippet of the search result')

class SearchResults(BaseModel):
    results: list[SearchResult] = Field(..., description='List of search results')

@function_tool
def search_duckduckgo(query: str, max_results: int, search_type: Literal['web', 'news']) -> list:
    """
    DuckDuckGo tool to search for web or news results.

    Args:
        query (str): The search query.
        max_results (int): The maximum number of results to return.
        search_type (str): Type of search ('web' or 'news').

    Returns:
        list: A list of dictionaries containing the search results.

    """
    results = []
    
    with DDGS() as ddgs:
        if search_type == "news":
            search_results = ddgs.news(query, max_results=max_results)
        else: 
            search_results = ddgs.text(query, max_results=max_results)

        for result in search_results:
            results.append(SearchResult(
                title=result['title'],
                link=result['href'],
                snippet=result['body']
            ))

    return SearchResults(results=results)

llm_model = OpenAIResponsesModel(model='gpt-4o-mini', openai_client=AsyncOpenAI())

web_search_agent = Agent(
    name='Web Search Agent',
    model=llm_model,
    output_type=str,
    instructions='You are a web search agent. Your job is to search the web for the user and return the results.',
    tools=[search_duckduckgo]  # Using custom DuckDuckGo search tool
)

response = Runner.run_sync(
    starting_agent=web_search_agent,
    input='Search for the latest news about OpenAI Agents SDK.',
)

print('Token Usage', response.raw_responses[0].usage)
print(f'{response.last_agent.name}:')
print(response.final_output)

for raw_response in response.raw_responses:
    print(raw_response)