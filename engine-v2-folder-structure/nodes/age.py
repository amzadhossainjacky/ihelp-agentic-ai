from utilities.states.input_state import ChatState
from langchain_core.messages import AIMessage
from utilities.messages.messages import all_messages

def age(state: ChatState):
    # get age ai message
    get_age_message = all_messages["age_message_ai"]
    ask_dob_message = AIMessage(
        content=get_age_message
    )
    print("age node executed")
    return {
        "messages": [ask_dob_message],
        "track_stage": "3"
    }