import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain import hub
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.tools import tool, Tool
from langchain_community.document_loaders import WebBaseLoader
import asyncio
import aiohttp

# Load environment variables from .env file
load_dotenv()

# 1. Set up the LLM
# Point to the local server
llm = ChatOpenAI(
    streaming=True,  # Enable streaming
    base_url="http://localhost:1234/v1",
    api_key="not-needed",
    model_name="local-model"  # This will be ignored by the local server, but is required
)

# 2. Set up the tools
# In this case, we'll use DuckDuckGo for web searches and a custom tool for scraping
async def _scrape_website(url: str) -> str:
    """Scrape content from a website and return it as a string."""
    async with aiohttp.ClientSession() as session:
        loader = WebBaseLoader(url, session=session)
        docs =  loader.aload()
        return "".join(doc.page_content for doc in docs)

scrape_website = Tool.from_function(
    func=_scrape_website,
    name="scrape_website",
    description="Scrape content from a website and return it as a string."
)

tools = [DuckDuckGoSearchRun(), scrape_website]

# 3. Create the Agent
# Get the prompt to use - you can modify this!
# See https://smith.langchain.com/hub/hwchase17/openai-tools-agent
prompt = hub.pull("hwchase17/openai-tools-agent")

# Construct the OpenAI Tools agent
agent = create_tool_calling_agent(llm, tools, prompt)

# Create an agent executor by passing in the agent and tools
agent_executor = AgentExecutor(agent=agent, tools=tools)

# 4. Run the Agent
print("Agent is ready. Ask a question that requires up-to-date information.")
print("For example: 'What is the current stock price of NVIDIA?' or 'What was the score of the last Lakers game?'")
print("Type 'exit' to quit.")

async def run_agent_and_stream(user_input: str):
    # Use stream_events to get a more detailed event stream
    async for event in agent_executor.astream_events({"input": user_input}, version="v1"):
        kind = event["event"]
        # Event that signifies the start of a new stream of tokens
        if kind == "on_chat_model_stream":
            if "chunk" in event["data"]:
                print(event["data"]["chunk"], end="", flush=True)
        # Optional: Print other events for debugging if needed
        # elif kind == "on_tool_start":
        #     print(f"\n--- Tool Start: {event['name']} with input {event['data'].get('input')} ---")
        # elif kind == "on_tool_end":
        #     print(f"\n--- Tool End: {event['name']} with output {event['data'].get('output')} ---")
        # elif kind == "on_agent_action":
        #     print(f"\n--- Agent Action: {event['data'].get('input')} ---")
        # elif kind == "on_agent_finish":
        #     print(f"\n--- Agent Finish: {event['data'].get('output')} ---")
    print() # Newline after the full response

if __name__ == "__main__":
    try:
        while True:
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                break
            asyncio.run(run_agent_and_stream(user_input))
    except KeyboardInterrupt:
        print("\nExiting...")