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
from dotenv import load_dotenv
load_dotenv()

# define llm
api_key = os.getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",api_key=api_key)

# define state
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    name: Optional[str]
    age: Optional[int]
    email: Optional[str]
    step: str  # greeting | ask_name | ask_age | ask_email | done

# define functions
def greeting_node(state: ChatState):
    return {
        "state": ""
    }
def ask_name_node(state: ChatState):
    pass
def ask_age_node(state: ChatState):
    pass
def ask_email_node(state: ChatState):
    pass

def chat_node(state: ChatState):
    all_messages = state['messages']
    llm_response = llm.invoke(all_messages)
    return {'messages': [llm_response]}

# Router
def router(state: ChatState):
    return state["step"]


# define memory
check_pointer = MemorySaver()

# define state
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)

graph.add_node("greeting", greeting_node)
graph.add_node("ask_name", ask_name_node)
graph.add_node("ask_age", ask_age_node)
graph.add_node("ask_email", ask_email_node)

graph.add_edge(START, "greeting")

graph.add_conditional_edges("greeting", router, {
    "ask_name": "ask_name"
})

graph.add_conditional_edges("ask_name", router, {
    "ask_age": "ask_age"
})

graph.add_conditional_edges("ask_age", router, {
    "ask_age" : "ask_age",
    "ask_email": "ask_email"
})

graph.add_conditional_edges("ask_email", router, {
    "ask_email": "ask_email",
    "done": END
})

graph.add_edge("chat_node", END)


chatbot = graph.compile(checkpointer=check_pointer)

thread_id = "chat-1"

config = {'configurable': {"thread_id": thread_id}}

# make the loop for the chatbot
while True:
    user_input = input("User: ")
    if user_input == "exit":
        break
    response = chatbot.invoke({'messages': [HumanMessage(content=user_input)]}, config=config)
    print("Chatbot: " + response['messages'][-1].content)