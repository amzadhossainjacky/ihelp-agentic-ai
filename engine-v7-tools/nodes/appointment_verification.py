from utilities.states.input_state import ChatState


def appointment_verification(state: ChatState):
    print("appointment verification node executed")
    return {
        "messages": ["I have Gathered all the information I need. I am verifying the appointment."],
        "track_stage": "5"
    }