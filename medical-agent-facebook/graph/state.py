from typing import TypedDict, Annotated
from enum import Enum
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

# booking state
class BookingState(str, Enum):
    """
    Tracks exactly where the user is in the booking funnel.
    The supervisor and booking agent both use this to decide what to do next.
    """
    IDLE               = "idle"                # no active booking in progress
    SYMPTOM_COLLECTION = "symptom_collection"  # user described symptoms
    DOCTOR_SELECTION   = "doctor_selection"    # user chose or was shown a doctor
    SLOT_SELECTION     = "slot_selection"      # showing/picking time slots
    CONFIRMING         = "confirming"          # collecting name/phone, final confirm
    BOOKED             = "booked"              # appointment confirmed
    CANCELLING         = "cancelling"          # cancel flow in progress
    

# chat conversation state
class ConversationState(BaseModel):
    """
    The full state of one conversation. LangGraph passes this between every node.
    Each node receives it, does its work, and returns a dict of fields to update.
    LangGraph merges those updates back into the state automatically.
    """
    
    booking_stage: str
    user_symptoms: str
    next_stage: str
    tool_call_made: str
    next_agent: str
    
    messages: Annotated[list[BaseMessage], add_messages] = Field(default_factory=list)