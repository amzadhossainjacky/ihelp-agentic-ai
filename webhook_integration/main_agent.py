from langchain.tools import tool
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import create_agent
import os
import requests
from dotenv import load_dotenv
load_dotenv()

# define llm
llm = ChatOpenAI( model="gpt-4o-mini")

search = DuckDuckGoSearchRun(description="Search for information on the internet")

# define tools
@tool
# search tool
def search_tool(query: str) -> str:
    """Search for information on the internet."""
    return search.run(query)
    

@tool
# get weather tool
def get_weather(location: str) -> str:
    """Get weather information for a location."""
    return f"Weather in {location}: Sunny, 72°F"


# job search tool
def get_jobs_tool(job_title: str):
    """Useful for when you need to find jobs. Input should be a job title."""
    url = "https://jobs-api14.p.rapidapi.com/v2/linkedin/search"

    querystring = {"query":job_title,"experienceLevels":"intern;entry;associate;midSenior;director","workplaceTypes":"remote;hybrid;onSite","location":"Bangladesh","datePosted":"month","employmentTypes":"contractor;fulltime;parttime;intern;temporary"}

    headers = {
        "x-rapidapi-key": "1fe1f28520msh1e8fbf05c7c6a94p1a35ecjsnd51a81fb3246",
        "x-rapidapi-host": "jobs-api14.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    return response.json()


# RAG tool
def rag_tool():
    """Retrieve relevant doctor information from the doctor database."""
    
    return "Relevant information from the doctor database."



tools = [search_tool, get_weather, get_jobs_tool, rag_tool]

# create agent
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="Answer the user's question using the available tools. If you don't know the answer, say you don't know. Always use the tools when necessary to get the correct answer."
)

agent_response = agent.invoke(
    {"messages": [{"role": "user", "content": "Is there any job for python developer?"}]}
)

print(agent_response)