from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
# for add all messages to state
from langgraph.graph.message import add_messages
from datetime import time

# chat state
class ChatState(TypedDict):
    thread_id: str
    user_id: str
    messages: Annotated[list[BaseMessage], add_messages]
    track_stage: str
    doctors: list[str]
    departments: list[str]
    doctor_ids: list[str]
    appointment_doctor_id: str
    selected_appointment_day: str
    selected_appointment_date: str
    preferred_time: str
    selected_appointment_start_time: str
    selected_appointment_end_time: str
    name: str
    age: str
    dob: str
    phone_number: str