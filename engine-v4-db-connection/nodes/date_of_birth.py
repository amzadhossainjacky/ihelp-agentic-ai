from utilities.states.input_state import ChatState
from langchain_core.messages import AIMessage
from utilities.messages.messages import all_messages
from utilities.validations.dob_validation import dob_validation

def date_of_birth(state: ChatState):
    # get user input from chatbot
    user_input = state["messages"][-1].content
    # extract the date of birth with llm if user provide other info with date of birth
    user_dob = dob_validation(user_input)
    # get invalid date of birth message from messages.py
    invalid_dob_message = all_messages["invalid_dob_message_ai"]
    invalid_dob_message = AIMessage(content=invalid_dob_message)
    # check if date of birth is valid
    if user_dob == False:
        return {
            "track_stage": "3",
            "messages": [invalid_dob_message]
        }
    else:
        # put the date of birth in the state
        state["dob"] = user_dob
        print("Date of birth extracted: ", user_dob)
        get_dob_ai_message = all_messages["date_of_birth_ai"]
        acknowledge_message = AIMessage(
            content=get_dob_ai_message
        )
        print("date of birth node executed")
        return {
            "messages": [acknowledge_message],
            "track_stage": "4",
            "dob": user_dob
        }