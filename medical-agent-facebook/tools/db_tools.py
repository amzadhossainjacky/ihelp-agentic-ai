from langchain_core.tools import tool
from graph.state import ConversationState
import os
import datetime
import asyncpg
from dotenv import load_dotenv
load_dotenv()

DB_URL = os.getenv("DB_URI")

# Helper to get a DB connection. 
async def get_conn():
    """Helper to get a DB connection."""
    return await asyncpg.connect(DB_URL)


# test db operation tool
@tool
def db_operation_test(query: str) -> str:
    """Test database operation."""
    # update conversation state
    ConversationState.tool_call_made = "db_operation_test"
    print(f"tool: Database operation tool called with query: {query}")
    return "Database operation tool call successful!"

# print("DB_URI from .env:", DB_URL)

# Example of a more complex tool that interacts with the database to get available slots for a doctor on a given date.
@tool
async def get_available_slots(doctor_id: str, date: datetime.date) -> str:
    """
    Get available appointment slots for a doctor on a given date.
    Args:
        doctor_id: The UUID of the doctor.
        date: Date in YYYY-MM-DD format.
    Returns a formatted string of available time slots.
    """
    conn = await get_conn()
    
    print(f"tool: get_available_slots called with doctor_id: {doctor_id}, date: {date}")
    
    try:
        rows = await conn.fetch(
            """SELECT slot_time FROM slots
               WHERE doctor_id=$1
               AND DATE(slot_time)=$2
               AND is_booked=FALSE
               ORDER BY slot_time""",
            doctor_id, date
        )
        if not rows:
            return f"No available slots for {date}. Try another date."
        times = [r["slot_time"].strftime("%I:%M %p") for r in rows]
        return f"Available slots on {date}: " + ", ".join(times)
    finally:
        await conn.close()
    
    
# Example of a tool that books an appointment in the database.
@tool
async def book_appointment(
    doctor_id: str,
    slot_time: datetime.datetime,
    patient_name: str,
    patient_phone: str,
    symptoms: str = ""
) -> str:
    """
    Book an appointment in the database.
    Args:
        doctor_id: UUID of the doctor.
        slot_time: Exact slot datetime string e.g. '2024-12-20 10:00:00'.
        patient_name: Full name of the patient.
        patient_phone: Phone number of the patient.
        symptoms: Comma-separated symptoms (optional).
    Returns confirmation ID on success.
    """
    conn = await get_conn()
    try:
        symptoms_list = [s.strip() for s in symptoms.split(",")] if symptoms else []
        row = await conn.fetchrow(
            """INSERT INTO appointments
               (doctor_id, slot_time, patient_name, patient_phone, symptoms, status)
               VALUES ($1, $2::timestamp, $3, $4, $5, 'confirmed')
               RETURNING id""",
            doctor_id, slot_time, patient_name, patient_phone, symptoms_list
        )
        await conn.execute(
            "UPDATE slots SET is_booked=TRUE WHERE doctor_id=$1 AND slot_time=$2::timestamp",
            doctor_id, slot_time
        )
        return f"Appointment confirmed! Confirmation ID: {row['id']}"
    finally:
        await conn.close()