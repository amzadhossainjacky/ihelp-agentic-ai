from utilities.states.input_state import ChatState
from langchain_core.tools import tool
from service.db_connection import db_executed
from utilities.llms.chat_llm import chat_llm
from langchain_core.messages import HumanMessage

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
   
    
    # connect to database and get the available time slots for the doctor
    # get doctors info from database
    # sql = "SELECT * FROM doctors WHERE doctor_id IN %s;"
    # values = tuple(doctor_ids)
    # doctor_info = db_executed("select", sql, values)
    # print("doctor info: ", doctor_info)
    # get the time slots for the doctor
    sql = """
SELECT d.name, s.day_of_week,
       TO_CHAR(s.start_time, 'HH12:MI AM') AS start_time,
       TO_CHAR(s.end_time, 'HH12:MI AM') AS end_time
FROM doctor_schedule s
JOIN doctors d ON d.doctor_id = s.doctor_id
WHERE s.doctor_id = ANY(%s)
  AND s.is_available = TRUE
ORDER BY d.name, s.day_of_week;
"""
    
    time_slots = db_executed("select", sql, (doctor_ids,))

    print("time slots: ", time_slots)

    # show the time slots to the user
    time_slot_message = f"""The available time slots for the doctor are: {time_slots}"""

    # llm prompt to get the day and time from the user
    llm_prompt_time_slot = f""" You are a medical appointment booking chatbot. You are given a list of time slots for a doctor. The time slots are in the following format: (doctor_name, day_of_week, start_time, end_time). The user input is: {user_input}. The time slots are: {time_slots}. Ask the user to select a day and time from the given time slots. """

    # invoke the llm to get the day and time from the user
    llm_response_time_slot = chat_llm.invoke([HumanMessage(content=llm_prompt_time_slot)])

    AI_response_time_slot = llm_response_time_slot.content
    # sample Ai message
    ai_message = "Thank you for providing the information. I will schedule the appointment for you."
    # return the message
    return {
        "messages": [AI_response_time_slot],
        "track_stage": "appointment_confirmation"
    }