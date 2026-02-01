from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
# for add all messages to state
from langgraph.graph.message import add_messages


# chat state
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    track_stage: str
    name: str
    age: str
    dob: str