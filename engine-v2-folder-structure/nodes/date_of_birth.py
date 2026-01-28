from utilities.states.input_state import ChatState
from langchain_core.messages import AIMessage
from utilities.messages.messages import all_messages

def date_of_birth(state: ChatState):
    get_dob_ai_message = all_messages["date_of_birth_ai"]
    acknowledge_message = AIMessage(
        content=get_dob_ai_message
    )
    print("date of birth node executed")
    return {
        "messages": [acknowledge_message],
        "track_stage": "4"
    }