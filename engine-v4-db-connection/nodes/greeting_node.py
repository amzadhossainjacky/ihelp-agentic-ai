from utilities.states.input_state import ChatState
from langchain_core.messages import AIMessage
from utilities.messages.messages import all_messages
# define functions
def greeting_node(state: ChatState):
    get_greeting_message = all_messages["greeting_message_ai"]
    greeting_message = AIMessage(content=get_greeting_message)
    print("greeting node executed")
    return {
        "messages": [greeting_message],
        "track_stage": "1"
    }