from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
# for add all messages to state
from langgraph.graph.message import add_messages
# for memory saver (local ram)
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig
import os
from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o-mini")

# define state
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    track_stage: str



# routing flow staging
routing_stage = {
    "1" : "greeting",
    "2" : "name",
    "3" : "age",
    "4" : "date_of_birth"
}

# define functions
def greeting_node(state: ChatState):
    greeting_message = AIMessage(
        content="Hello! I am a user validation chatbot. Please tell me your name."
    )
    print("greeting node executed")
    return {
        "messages": [greeting_message],
        "track_stage": "1"
    }

def name(state: ChatState):
    ask_age_message = AIMessage(
        content="Thank you for sharing your name. Please tell me your age."
    )
    print("name node executed")
    return {
        "messages": [ask_age_message],
        "track_stage": "2"
    }

def age(state: ChatState):
    ask_dob_message = AIMessage(
        content="Thank you for sharing your age. Please tell me your date of birth."
    )
    print("age node executed")
    return {
        "messages": [ask_dob_message],
        "track_stage": "3"
    }
    
def date_of_birth(state: ChatState):
    acknowledge_message = AIMessage(
        content="Thank you for sharing your date of birth. I have all the information I need. What you want from me?"
    )
    print("date of birth node executed")
    return {
        "messages": [acknowledge_message],
        "track_stage": "4"
    }

# def chat_node(state: ChatState):
#     all_messages = state['messages']
#     llm_response = llm.invoke(all_messages)
#     return {'messages': [llm_response]}

def chat_node(state: ChatState):
    llm_response = llm.invoke(state["messages"])
    return {"messages": [llm_response]}


# define tracking node
def tracking_node(state: ChatState):
    if state["track_stage"] == "":
        return {"track_stage": "0"}
    else:
        print("track stage: ", state["track_stage"])
        pass


# define routing node
def routing_node(state: ChatState):
    if state["track_stage"] == "0":
        return "greeting"
    elif state["track_stage"] == "1":
        return "name"
    elif state["track_stage"] == "2":
        return "age"
    elif state["track_stage"] == "3":
        return "date_of_birth"
    
    return "chat_node"
    

# define memory
check_pointer = MemorySaver()

# define state
graph = StateGraph(ChatState)
# define nodes
graph.add_node("tracking_node", tracking_node)
graph.add_node("routing_node", routing_node)
graph.add_node("greeting", greeting_node)
graph.add_node("name", name)
graph.add_node("age", age)
graph.add_node("date_of_birth", date_of_birth)
graph.add_node("chat_node", chat_node)
# define edges
graph.add_edge(START, "tracking_node")
graph.add_conditional_edges("tracking_node", routing_node)
graph.add_edge("greeting", END)
graph.add_edge("name", END)
graph.add_edge("age", END)
graph.add_edge("date_of_birth", END)
graph.add_edge("chat_node", END)


chatbot = graph.compile(checkpointer=check_pointer)

thread_id = "1"

config = {'configurable': {"thread_id": thread_id}}

# print all the history/checkpoints
history = chatbot.get_state_history(config)
print(history)