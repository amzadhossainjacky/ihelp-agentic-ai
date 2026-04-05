from langchain_openai import ChatOpenAI
# from langgraph.prebuilt import create_react_agent
from langchain.agents import create_agent
from graph.state import ConversationState
from tools.search_tools import search_symptom_info
from dotenv import load_dotenv
load_dotenv()


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

SYSTEM = """You are a compassionate medical triage assistant.
Steps to follow:
1. Acknowledge the user's symptoms with empathy.
2. Call search_symptom_info to understand what specialist they need.


IMPORTANT: Tell the user you are not a doctor and cannot provide a diagnosis.
Only provide information about what type of doctor they should see based on their symptoms."""


async def symptom_agent_node(state: ConversationState) -> dict:
    agent = create_agent(
        model=llm,
        tools=[search_symptom_info],
        system_prompt=SYSTEM
    )
    result = await agent.ainvoke({"messages": state.messages})
    last_msg = result["messages"][-1]

    # Collect symptoms from recent user messages
    recent_symptoms = [
        m.content for m in state.messages[-2:]
        if hasattr(m, "type") and m.type == "human"
    ]

    return {
        "messages": [last_msg],
        "user_symptoms": recent_symptoms,
        "booking_stage": "symptom_collection",
        "next_stage": "doctor search should start"
    }