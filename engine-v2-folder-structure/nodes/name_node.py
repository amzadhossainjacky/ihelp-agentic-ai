from utilities.states.input_state import ChatState
from langchain_core.messages import AIMessage
from utilities.messages.messages import all_messages

def name(state: ChatState):
    get_age_message = all_messages["name_message_ai"]
    ask_age_message = AIMessage(content=get_age_message)
    print("name node executed")
    return {
        "messages": [ask_age_message],
        "track_stage": "2"
    }