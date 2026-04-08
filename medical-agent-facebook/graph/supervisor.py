from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from graph.state import ConversationState
from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

SUPERVISOR_PROMPT = """You are a routing supervisor for a medical appointment booking system.
Read the latest user message and decide which specialist agent should handle it.

Available agents:
- symptom_agent: helps users understand their symptoms and recommends a type of doctor.
- general_agent: answers general questions about the clinic and can assist with booking.
- booking_agent: guides users through the appointment booking process step by step.

Current booking state:

- User symptoms: {symptoms}
- Next stage: {next_stage}

Respond with ONLY the agent name. Nothing else. No explanation."""


VALID_AGENTS = {"symptom_agent", "general_agent", "booking_agent"}

async def supervisor_node(state: ConversationState) -> dict:
    """
    The entry point for every user message.
    Reads current state + last message, picks the right agent.
    """
    
    prompt = SUPERVISOR_PROMPT.format(
        symptoms=state.user_symptoms or "none",
        next_stage=state.next_stage or "none"
    )
    
    # Only pass last 6 messages (3 turns) to save tokens
    recent_messages = state.messages[-6:] if len(state.messages) > 6 else state.messages
    
    response = await llm.ainvoke([
        SystemMessage(content=prompt),
        *recent_messages
    ])
    
    chosen_agent = response.content.strip().lower()
    
    print(f"Supervisor chose agent: {chosen_agent}")  # Debugging output
    
    # Safety fallback — if LLM hallucinates an agent name
    if chosen_agent not in VALID_AGENTS:
        chosen_agent = "general_agent"
        
    # update state with the chosen agent for the next node to read
    state.next_agent = chosen_agent

    return {"next_agent": chosen_agent}