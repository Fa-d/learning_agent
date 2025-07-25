import os

# Set USER_AGENT before any other imports to suppress warnings
if not os.getenv("USER_AGENT"):
    os.environ["USER_AGENT"] = "VizLearn/1.0 (https://github.com/Fa-d/learning_agent)"

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain import hub
from langchain.tools import tool, Tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_community.document_loaders import WebBaseLoader
import asyncio
import aiohttp
import warnings
from pydantic import SecretStr
from ddgs import DDGS

# Load environment variables from .env file
load_dotenv()

# 1. Set up the LLM
# Point to the local server
llm_base_url = os.getenv("LLM_BASE_URL", "http://localhost:1234/v1")
llm = ChatOpenAI(
    streaming=True,  # Enable streaming
    base_url=llm_base_url,
    api_key=SecretStr("sk-not-needed"),  # Local server doesn't validate this
    model="local-model"  # This will be ignored by the local server, but is required
)

# 2. Set up the tools
# Custom DuckDuckGo search tool using the new ddgs package
def _search_duckduckgo(query: str) -> str:
    """Search DuckDuckGo for the given query and return results."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
            if not results:
                return "No search results found."
            
            formatted_results = []
            for result in results:
                title = result.get('title', 'No title')
                body = result.get('body', 'No description')
                href = result.get('href', 'No URL')
                formatted_results.append(f"Title: {title}\nDescription: {body}\nURL: {href}\n")
            
            return "\n".join(formatted_results)
    except Exception as e:
        return f"Error searching DuckDuckGo: {str(e)}"

duckduckgo_search = Tool.from_function(
    func=_search_duckduckgo,
    name="duckduckgo_search",
    description="Search the web using DuckDuckGo. Input should be a search query string."
)

# In this case, we'll use DuckDuckGo for web searches and a custom tool for scraping
async def _scrape_website(url: str) -> str:
    """Scrape content from a website and return it as a string."""
    try:
        async with aiohttp.ClientSession() as session:
            loader = WebBaseLoader(url, session=session)
            docs = loader.aload()
            return "".join(doc.page_content for doc in docs)
    except Exception as e:
        return f"Error scraping website: {str(e)}"

scrape_website = Tool.from_function(
    func=_scrape_website,
    name="scrape_website",
    description="Scrape content from a website and return it as a string."
)

tools = [duckduckgo_search, scrape_website]

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
                print(event["data"]["chunk"].content, end="", flush=True)
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
    # Suppress specific warnings
    warnings.filterwarnings("ignore", category=ResourceWarning)
    
    try:
        while True:
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                break
            asyncio.run(run_agent_and_stream(user_input))
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        # Clean up any remaining tasks
        try:
            loop = asyncio.get_event_loop()
            if not loop.is_closed():
                pending = asyncio.all_tasks(loop)
                if pending:
                    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        except Exception:
            pass