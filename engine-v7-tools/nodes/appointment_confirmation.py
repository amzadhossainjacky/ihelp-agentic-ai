from utilities.states.input_state import ChatState
from datetime import time, datetime
from pydantic import BaseModel, Field
from utilities.llms.chat_llm import chat_llm
from service.date_extract import get_next_date_from_day
from service.store_appointments import store_appointments
from langchain_core.messages import HumanMessage

# output class for appointment confirmation llm
class AppointmentConfirmationOutput(BaseModel):
    selected_doctor_id: str = Field(..., description="The selected doctor id")
    appointment_date: str = Field(..., description="The selected appointment date (day name, ex: sunday, monday, etc.)")
    preferred_time: time = Field(..., description="The preferred time (12:00pm, 1:00pm, etc..)")
    

# appointment confirmation node
def appointment_confirmation(state: ChatState):
    print("appointment confirmation node executed")
    # get user input from chatbot
    user_input = state["messages"][-1].content

    # get the list of doctors and departments from the state
    doctors = state["doctors"]
    departments = state["departments"]
    doctor_ids = state["doctor_ids"]
    doctor_state = [doctors, departments, doctor_ids]
    print("doctor state: ", doctor_state)
    # extract the selected appointment date and time from the user input using llm
    llm_prompt_appointment_confirmation = f"""
You are a medical appointment booking system.

Extract:
- doctor id
- day name (capitalize first letter, ex: Monday)
- preferred time in 24-hour format HH:MM:SS
- appointment start time in 24-hour format HH:MM:SS
- appointment end time in 24-hour format HH:MM:SS

IMPORTANT:
- Return time ONLY in HH:MM:SS format.
- Do NOT return timezone.
- Do NOT return datetime.
- Only return pure time.

User input: {user_input}
Doctor list with id: {doctor_state}
"""

    # structured llm
    structured_llm = chat_llm.with_structured_output(AppointmentConfirmationOutput)
    ai_response  = structured_llm.invoke([HumanMessage(content=llm_prompt_appointment_confirmation)])

    # extract the appointment date and time from the llm response
    selected_doctor_id = ai_response.selected_doctor_id
    appointment_day = ai_response.appointment_date
    user_preferred_time = ai_response.preferred_time

    # get appointment date from day name
    appointment_date = get_next_date_from_day(appointment_day)


    # print the extracted appointment date and time
    print("selected doctor id: ", selected_doctor_id)
    print("appointment day by name: ", appointment_day)
    print("user preferred time: ", user_preferred_time)
    print("appointment date: ", appointment_date)

    # check if the appointment date and time is valid
    if selected_doctor_id == "Unknown" or appointment_day == "Unknown" or user_preferred_time == "Unknown":
        return {
            "messages": ["I'm sorry, I didn't get the appointment date and time or doctor name. Please tell me the doctor name, day name and preferred time again."],
            "track_stage": "appointment_confirmation"
        }
    
    
    
    return {
        "messages": ["Thank you for letting me know. I will confirm the appointment with you. Please tell me your name."],
        "appointment_doctor_id": selected_doctor_id,
        "selected_appointment_day": appointment_day,
        "selected_appointment_date": appointment_date,
        "preferred_time": user_preferred_time.strftime("%H:%M:%S"),
        "track_stage": "1"
    }

# test the appointment_confirmation function
# if __name__ == "__main__":
#     appointment_confirmation()