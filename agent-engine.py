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
api_key = os.getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",api_key=api_key)

# LLM Validator
def llm_validate(field: str, value: str):
    prompt = f"""
You are a validator AI.

Validate the following user input.

Field: {field}
Value: "{value}"

Rules:
- Name: must look like a real human name
- Age: must be a number between 1 and 120
- Email: must be a realistic valid email

Respond ONLY with valid JSON.
No markdown. No explanation.

Format:
{{"valid": true, "reason": "short reason"}}
"""
    response = llm.invoke(prompt)
    return json.loads(response.content.strip())


# define state
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    name: Optional[str]
    age: Optional[str]
    email: Optional[str]
    step: str  # greeting | ask_name | ask_age | ask_email | done

# define functions
def greeting_node(state: ChatState):

    return {
        "messages": [AIMessage(content="My name is pranto")],
        "step": "ask_name"
    }

def ask_name_node(state: ChatState):
    # get the data from the messages state
    user_input = state["messages"][-1].content.strip()
    result = llm_validate("name", user_input)
    # if valid = false
    if not result["valid"]:
        return {
            "messages": [AIMessage(content=f"{result['reason']}. Please enter your name again.")],
            "step": "ask_name"
        }
    return {
        "name": user_input,
        "messages": [AIMessage(content=f"Nice to meet you! {user_input}. How old are you?")],
        "step": "ask_age"
    }

def ask_age_node(state: ChatState):
    user_input = state["messages"][-1].content.strip()
    result = llm_validate("age", user_input)
    if not result["valid"]:
        return {
            "messages": [AIMessage(content=f"{result['reason']}. Please enter your age again.")],
            "step": "ask_age"
        }
    return {
        "age": user_input,
        "messages": [AIMessage(content="Great! Now tell me your email address")],
        "step": "ask_email"
    }


def ask_email_node(state: ChatState):
    user_input = state["messages"][-1].content.strip()
    result = llm_validate("email", user_input)

    if not result["valid"]:
        return {
            "messages": [AIMessage(content=f"{result['reason']}. Please enter your email again.")],
            "step": "ask_email"
        }
    return {
        "email": user_input,
        "messages": [AIMessage(content="Thank you! All information collected successfully. Now tell me how can I help you?")],
        "step": "done"
    }

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
    "ask_name": "ask_name",
})

graph.add_conditional_edges("ask_name", router, {
    "ask_name": "ask_name",
    "ask_age": "ask_age",
})

graph.add_conditional_edges("ask_age", router, {
    "ask_age" : "ask_age",
    "ask_email": "ask_email"
})

graph.add_conditional_edges("ask_email", router, {
    "ask_email": "ask_email",
    "done": "chat_node"
})

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