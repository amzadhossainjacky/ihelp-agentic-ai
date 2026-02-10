from utilities.states.input_state import ChatState

def appointment_confirmation(state: ChatState):
    print("appointment confirmation node executed")
    return {
        "messages": ["Thank you for letting me know. I will confirm the appointment with you. Please tell me your name."],
        "track_stage": "1"
    }