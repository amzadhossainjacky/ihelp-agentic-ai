from utilities.states.input_state import ChatState
from langchain_core.messages import AIMessage
from utilities.messages.messages import all_messages
from utilities.validations.name_validation import name_validation

def name(state: ChatState):
    get_name_message = all_messages["name_message_ai"]
    ask_age_message = AIMessage(content=get_name_message)
    print("name node executed")

    # get user input from chatbot
    user_input = state["messages"][-1].content
    # extract the name with llm if user provide other info with name
    user_name = name_validation(user_input)

    # get invalid name message from messages.py
    invalid_name_message = all_messages["invalid_name_message_ai"]
    invalid_name_message = AIMessage(content=invalid_name_message)
    # check if name is valid
    if user_name == False:
        return {
            "track_stage": "1",
            "messages": [invalid_name_message]
        }
    else:
        # put the name in the state
        state["name"] = user_name
        print("Name extracted: ", user_name)
        return {
            "name": user_name,
            "messages": [ask_age_message],
            "track_stage": "2"
        }
        