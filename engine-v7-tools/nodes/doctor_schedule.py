from utilities.states.input_state import ChatState
from langchain_core.tools import tool

def schedule_node(state: ChatState):
    print("schedule node executed")
    # get user input from chatbot
    user_input = state["messages"][-1].content

    # get the doctor, department names from the state
    doctors = state["doctors"]
    departments = state["departments"]
    doctor_ids = state["doctor_ids"]

    check_state = [doctors, departments, doctor_ids]
    print("check state: ", check_state)
   



    # sample Ai message
    ai_message = "Thank you for providing the information. I will schedule the appointment for you."
    # return the message
    return {
        "messages": [ai_message],
        "track_stage": "4"
    }