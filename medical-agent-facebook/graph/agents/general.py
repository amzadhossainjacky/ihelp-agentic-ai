from langchain_openai import ChatOpenAI
# from langgraph.prebuilt import create_react_agent
from langchain.agents import create_agent
from langchain_core.messages import SystemMessage
from graph.state import ConversationState
from tools.clinic_tools import get_clinic_info
from tools.db_tools import db_operation_test, get_available_slots, book_appointment
from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

SYSTEM = """You are a friendly receptionist for a medical clinic.
Answer general questions about the clinic (hours, address, fees, insurance).
Use the get_clinic_info tool when needed.
If the user seems to need a doctor or wants to book, 
use the appropriate database tools to assist them.
db tools available: db_operation_test, get_available_slots, book_appointment.
Keep responses short and friendly — messages may come from WhatsApp or Facebook."""


async def general_agent_node(state: ConversationState) -> dict:
    agent = create_agent(
        model=llm,
        tools=[get_clinic_info, db_operation_test, get_available_slots, book_appointment],
        system_prompt=SYSTEM
        
    )
    result = await agent.ainvoke({"messages": state.messages})
    return {
        "messages": [result["messages"][-1]],
        "next_stage": "booking should start"
        }