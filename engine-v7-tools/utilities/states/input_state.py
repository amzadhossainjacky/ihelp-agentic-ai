from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
# for add all messages to state
from langgraph.graph.message import add_messages


# chat state
class ChatState(TypedDict):
    thread_id: str
    user_id: str
    messages: Annotated[list[BaseMessage], add_messages]
    track_stage: str
    doctors: list[str]
    departments: list[str]
    doctor_ids: list[str]
    name: str
    age: str
    dob: str
    phone_number: str