from fastapi import FastAPI
from graph.graph import build_graph
from graph.state import ConversationState
from langchain.messages import HumanMessage, AIMessage

app = FastAPI()

# Build the graph once at startup
graph = build_graph()

@app.post("/message")
async def handle_message(user_message: str):
    """
    This endpoint receives a user message from the frontend (WhatsApp/Facebook).
    It creates or updates the conversation state, runs the graph, and returns the agent's response.
    """
    
    # For simplicity, we're not implementing persistent storage here.
    # In a real app, you'd look up the conversation by user ID and load its state.
    
    # Create initial state with the user's message
    state = ConversationState(
        booking_stage="idle",
        user_symptoms="",
        next_stage="",
        tool_call_made="",
        next_agent="",
        messages=[HumanMessage(content=user_message)]
    )
    
    # Run the graph with the current state
    result = await graph.ainvoke(state)
    
    # print the full state for debugging
    print("Updated Conversation State:", result)
    
    # Extract the agent's response (last message in the updated state)
    agent_response = result
    
    
    
    return {
        "response": agent_response}