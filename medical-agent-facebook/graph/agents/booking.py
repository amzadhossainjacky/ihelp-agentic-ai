from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from graph.state import ConversationState, BookingStage
from tools.db_tools import get_available_slots, book_appointment
import re

llm = ChatOpenAI(model="gpt-4o", temperature=0)


def build_booking_prompt(state: ConversationState) -> str:
    """Builds a dynamic system prompt based on the current booking stage."""
    base = """You are a medical appointment booking assistant.
Be warm, concise, and guide the user step by step through booking.
Messages may appear on WhatsApp or Facebook, so keep responses brief.\n\n"""

    context = f"""Current booking context:
- Stage: {state.booking_stage.value}
- Doctor: {state.selected_doctor_name or 'not selected'} (ID: {state.selected_doctor_id or 'N/A'})
- Slot: {state.selected_slot or 'not selected'}
- Patient name: {state.patient_name or 'not collected'}
- Patient phone: {state.patient_phone or 'not collected'}
- Symptoms: {', '.join(state.symptoms) if state.symptoms else 'none'}\n\n"""

    instructions = {
        BookingStage.DOCTOR_SELECTION: (
            "The user has been shown doctors. "
            "Confirm which doctor they want and ask what date they prefer."
        ),
        BookingStage.SLOT_SELECTION: (
            "Call get_available_slots with the doctor_id and date. "
            "Present the available times clearly and ask which they prefer."
        ),
        BookingStage.CONFIRMING: (
            "You have a doctor and slot. "
            "If patient_name or patient_phone is missing, ask for them now. "
            "Once you have both, summarize the booking and ask for confirmation. "
            "When user confirms, call book_appointment."
        ),
        BookingStage.BOOKED: (
            "The booking is done. Thank the user and share the confirmation ID."
        ),
    }
    stage_instruction = instructions.get(state.booking_stage, "Guide the user through booking.")
    return base + context + "Your task: " + stage_instruction



async def booking_agent_node(state: ConversationState) -> dict:
    prompt = build_booking_prompt(state)
    agent = create_agent(
        model=llm,
        tools=[book_appointment],
        system_prompt=prompt
    )
    result = await agent.ainvoke({"messages": state.messages})
    last_msg = result["messages"][-1]

    updates: dict = {"messages": [last_msg]}

    # Advance the booking stage by looking at tool calls made
    for msg in result["messages"]:
        # If book_appointment was called, we're done
        if hasattr(msg, "name") and msg.name == "book_appointment":
            conf_match = re.search(r"Confirmation ID: ([a-f0-9\-]{36})", msg.content)
            if conf_match:
                updates["booking_stage"] = BookingStage.BOOKED
                updates["confirmation_id"] = conf_match.group(1)

        # If get_available_slots was called, we moved to slot selection
        if hasattr(msg, "name") and msg.name == "get_available_slots":
            if state.booking_stage == BookingStage.DOCTOR_SELECTION:
                updates["booking_stage"] = BookingStage.SLOT_SELECTION

    # Extract patient info from the last AI message if mentioned
    content = last_msg.content
    phone_match = re.search(r"\+?\d[\d\s\-]{9,14}", content)
    if phone_match and not state.patient_phone:
        updates["patient_phone"] = phone_match.group(0)

    # If stage hasn't changed, advance it forward
    if "booking_stage" not in updates:
        stage_flow = {
            BookingStage.DOCTOR_SELECTION: BookingStage.SLOT_SELECTION,
            BookingStage.SLOT_SELECTION: BookingStage.CONFIRMING,
        }
        if state.booking_stage in stage_flow:
            updates["booking_stage"] = stage_flow[state.booking_stage]

    return updates