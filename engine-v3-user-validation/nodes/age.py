from utilities.states.input_state import ChatState
from langchain_core.messages import AIMessage
from utilities.messages.messages import all_messages
from utilities.validations.age_validation import age_validation

def age(state: ChatState):
    # get age ai message
    get_age_message = all_messages["age_message_ai"]
    ask_dob_message = AIMessage(
        content=get_age_message
    )
    print("age node executed")
    # get user input from chatbot
    user_input = state["messages"][-1].content
    # extract the age with llm if user provide other info with age
    user_age = age_validation(user_input)

    # get invalid age message from messages.py
    invalid_age_message = all_messages["invalid_age_message_ai"]
    invalid_age_message = AIMessage(content=invalid_age_message)
    # check if age is valid
    if user_age == False:
        return {
            "track_stage": "2",
            "messages": [invalid_age_message]
        }
    else:
        # put the age in the state
        state["age"] = user_age
        print("Age extracted: ", user_age)
        # ask for date of birth
        return {
            "messages": [ask_dob_message],
            "track_stage": "3",
            "age": user_age
        }