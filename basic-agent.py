from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated, Optional
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
# for add all messages to state
from langgraph.graph.message import add_messages
# for memory saver (local ram)
from langgraph.checkpoint.memory import MemorySaver
import os
import json
from dotenv import load_dotenv
load_dotenv()

# define llm
# api_key = os.getenv("GOOGLE_API_KEY")
# llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",api_key=api_key)
llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o-mini")

# define state
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# define functions

def chat_node(state: ChatState):
    all_messages = state['messages']
    llm_response = llm.invoke(all_messages)
    return {'messages': [llm_response]}

# def greeting_node(state:ChatState):
#     # return a AI message
#     return {'messages': [AIMessage(content="Hello, I'm a chatbot. What is your name?")]}

# define memory
check_pointer = MemorySaver()

# define state
graph = StateGraph(ChatState)

graph.add_node("chat_node", chat_node)



# define edges

graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

# complie the graph
chatbot = graph.compile(checkpointer=check_pointer)

thread_id = "chat-1"
config = {'configurable': {"thread_id": thread_id}}

print("Type 'exit' to quit.\n")


# make the loop for the chatbot
while True:
    user_input = input("User: ")
    if user_input == "exit":
        break
    response = chatbot.invoke({'messages': [HumanMessage(content=user_input)]}, config=config)
    print("Chatbot: " + response['messages'][-1].content)