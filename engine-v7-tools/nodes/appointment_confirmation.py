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
    

# output class for user intent llm
class UserIntentOutput(BaseModel):
    another_doctor_or_department: bool = Field(..., description="true if user wants to book another appointment, false if user asks something else")
    another_schedule: bool = Field(..., description="true if user wants to book another schedule for the same doctor, false if user asks something else")
    

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
Your task is to extract the following information from the user input:
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
- Only return lowercase output.

If user asks for another schedule for the same doctor or another doctor or department, return "unknown" for doctor id.
If user asks for another doctor or department, return "unknown" for day name and preferred time.
If user does not provide any information (appointment date and time), return "unknown" for all the fields.
If user wants to cancel the appointment, return "unknown" for all the fields.
If user asks something else, return "unknown" for all the fields.


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

    # print(f"selected doctor id: {selected_doctor_id}\nappointment day: {appointment_day}\nuser preferred time: {user_preferred_time}")


    # print the extracted appointment date and time
    print("selected doctor id: ", selected_doctor_id)
    print("appointment day by name: ", appointment_day)
    print("user preferred time: ", user_preferred_time)
    # print("appointment date: ", appointment_date)

    # check if the appointment date and time is valid
    if appointment_day == "unknown" or user_preferred_time == "unknown":

        # if user want another other things, 
        user_input_last = state["messages"][-1].content

        # check what user want or intent using llm
        llm_prompt_user_intent = f"""
        You are a medical appointment booking system.
        The user input is: {user_input_last}.
        The user can either want to book another appointment or ask something else.
        If the user wants to book another appointment with another doctor or department, return another_doctor_or_department as true, otherwise false.
        If the user wants to see another doctor's schedule, return another_schedule as true, otherwise false.
        If the user asks something else, return false for both.
        """
        # structured llm for user intent
        structured_llm = chat_llm.with_structured_output(UserIntentOutput)
        llm_response_user_intent = structured_llm.invoke([HumanMessage(content=llm_prompt_user_intent)])
        user_intent = llm_response_user_intent

        # if user want to book another appointment
        if user_intent.another_doctor_or_department:
            return {
                "messages": ["Sure. Please tell me the name of the doctor or department you want to book an appointment with."],
                "track_stage": "rag"
            }
        # if user want to book another schedule for the same doctor
        elif user_intent.another_schedule:
            return {
                "messages": ["Sure. Please tell me the name of the doctor again."],
                "track_stage": "schedule"
            }


        return {
            "messages": ["I'm sorry, I didn't get the appointment date and time or doctor name. Please tell me the doctor name, day name and preferred time again. Do you want to book another appointment with another doctor or ask something else?"],
            "track_stage": "appointment_confirmation"
        }
    
    # get appointment date from day name
    # if appointment_day.lower() != "unknown":
    appointment_date_db = get_next_date_from_day(appointment_day)
    
    
    return {
        "messages": ["Thank you for letting me know. I will confirm the appointment with you. Please tell me your name."],
        "appointment_doctor_id": selected_doctor_id,
        "selected_appointment_day": appointment_day,
        "selected_appointment_date": appointment_date_db,
        "preferred_time": user_preferred_time.strftime("%H:%M:%S"),
        "track_stage": "1"
    }

# test the appointment_confirmation function
# if __name__ == "__main__":
#     appointment_confirmation()