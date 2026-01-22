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
    name:str
    age:str
    email:str

# define functions

def chat_node(state: ChatState):
    all_messages = state['messages']
    llm_response = llm.invoke(all_messages)
    return {'messages': [llm_response]}

def greeting_node(state:ChatState):
    # return a AI message
    AI_message = "Chatbot: Hello, I'm a chatbot. What is your name?"
    print(AI_message)
    state["messages"].append(AIMessage(content=AI_message))
    return state

def take_name(state:ChatState):
    # get the last message from state
    user_message = state["messages"][-1]
    # take name from user 
    user_input = input("User: ")
    # extract the name with llm if user provide other info with name
    name_llm_response = llm.invoke([SystemMessage(content="Extract only name from the user input. If there is no name, return 'Unknown'. Ex: my name is John, return John."), 
                                    HumanMessage(content=user_input)])
    if name_llm_response.content == "Unknown":
        print("Chatbot: I'm sorry, I didn't get your name. Please tell me your name again.")
        return state
    print(f"Chatbot: {name_llm_response.content}! Thats a good name. Now tell me your Age")
    # put the name to the state
    state["name"] = name_llm_response.content
    # put the user message to the state
    state["messages"].append(HumanMessage(content=user_input))
    return state

def take_age(state:ChatState):
    # get the last message from state
    user_message = state["messages"][-1]
    # take age from user 
    user_input_age = input("User: ")
    # check the valid age with llm 
    llm_age_response = llm.invoke([SystemMessage(content="Extract only age number from the user input. If there is no age, return 'Unknown'. Ex: I'm 10 years old/i'm 10/my age is 10/etc, return 10."), HumanMessage(content=user_input_age)])
    if llm_age_response.content == "Unknown":
        print("Chatbot: I'm sorry, I didn't get your age. Please tell me your age again.")
        return state
    print(f"Chatbot: Okay. Now tell me your email id")
    # put age in the state
    state["age"] = llm_age_response.content
    # put the user message to the state
    state["messages"].append(HumanMessage(content=user_input_age))
    return state

def take_email(state:ChatState):
    # get the last message from state
    user_message = state["messages"][-1]
    # take email from user 
    user_input_email = input("User: ")
    # check the valid email with llm 
    llm_email_response = llm.invoke([SystemMessage(content="Extract only email from the user input. If there is no email, return 'Unknown'. Ex: my email is test@test.com, return test@test.com. If the email is not valid, return 'Invalid'."), HumanMessage(content=user_input_email)])
    if llm_email_response.content == "Unknown" or llm_email_response.content == "Invalid":
        print("Chatbot: I'm sorry, I didn't get your email. Please tell me your email again.")
        return state
    print(f"Chatbot: Okay. Now I know your name, age and email. Lets chat.")
    # put email in the state
    state["email"] = llm_email_response.content
    # put the user message to the state
    state["messages"].append(HumanMessage(content=user_input_email))
    return state


# define memory
check_pointer = MemorySaver()

# define state
graph = StateGraph(ChatState)

graph.add_node("greeting_node", greeting_node)
graph.add_node("chat_node", chat_node)
graph.add_node("take_name", take_name)
graph.add_node("take_age", take_age)
graph.add_node("take_email", take_email)


# define edges
graph.add_edge(START, "greeting_node")
graph.add_edge("greeting_node", "take_name")
graph.add_edge("take_name", "take_age")
graph.add_edge("take_age", "take_email")
graph.add_edge("take_email", "chat_node")
graph.add_edge("chat_node", END)

# complie the graph
chatbot = graph.compile(checkpointer=check_pointer)

thread_id = "chat-1"
config = {'configurable': {"thread_id": thread_id}}

print("Type 'exit' to quit.\n")

# print all messages from state


# make the loop for the chatbot
while True:
    # user_input = input("User: ")
    # if user_input == "exit":
    #     break
    response = chatbot.invoke({'messages': []}, config=config)
    
    user_input = input("User: ")
    if user_input == "exit":
        break
    response = chatbot.invoke({'messages': [HumanMessage(content=user_input)]}, config=config)
    print("Chatbot: " + response['messages'][-1].content)