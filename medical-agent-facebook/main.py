from fastapi import FastAPI, HTTPException
from graph.graph import build_graph
from graph.state import ConversationState
from langchain_core.messages import HumanMessage, AIMessage
from typing import Optional
from memory.checkpointer import get_checkpointer
from contextlib import asynccontextmanager
from pydantic import BaseModel
import traceback
from dotenv import load_dotenv

load_dotenv()

# Graph is built once at startup and reused for every request
_graph = None

# lifespan function to initialize resources at startup and cleanup at shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs at startup and shutdown."""
    global _graph
    checkpointer = await get_checkpointer()
    print(f"Checkpointer type: {type(checkpointer)}")  # this will tell you exactly what it is
    _graph = build_graph(checkpointer)
    print("✅ Agent graph ready")
    yield
    # Cleanup: Close DB connections, etc. if needed
    print("👋 Shutting down")


# checkpointer = await get_checkpointer()
# graph = build_graph(checkpointer)



app = FastAPI(
    title="Medical Booking Agent",
    description="Multi-agent appointment booking system",
    lifespan=lifespan
    
)

# Pydantic model for incoming chat requests to API
class ChatRequest(BaseModel):
    message: str
    user_id: str        # phone number, FB PSID, etc.
    channel: str = "web"   # "web" | "whatsapp" | "facebook"
    
    
# Pydantic model for API responses
class ChatResponse(BaseModel):
    reply: str
    booking_stage: str
    thread_id: str
    selected_doctor: Optional[str] = None
    confirmation_id: Optional[str] = None



@app.post("/message")
async def handle_message(request: ChatRequest):
    """
    This endpoint receives a user message from the frontend (WhatsApp/Facebook).
    It creates or updates the conversation state, runs the graph, and returns the agent's response.
    """
    
    
    
    # For simplicity, we're not implementing persistent storage here.
    # In a real app, you'd look up the conversation by user ID and load its state.
    
    if _graph is None:
        raise HTTPException(status_code=503, detail="Graph not initialized")

    # Create a unique thread ID for this user (could be more complex in real app)
    thread_id = f"{request.channel}:{request.user_id}"

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    print(f"Received message from {thread_id}: {request.message}")
    
    try:
        result = await _graph.ainvoke(
            {
                "messages": [HumanMessage(content=request.message)],
                
                "user_symptoms": "",
                "next_stage": "",
                "tool_call_made": "",
                
            },
            config=config
        )
        
    except Exception as e:
        error_detail = {
            "type": type(e).__name__,
            "message": str(e) or repr(e),   # repr() as fallback
            "traceback": traceback.format_exc()
    }
        print("❌ ERROR:", error_detail)     # always log server-side
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: [{type(e).__name__}] {repr(e)}"
    )
    
    # Extract the agent's response (last message in the updated state)
    last_message = result["messages"][-1]
    
    return {"response": last_message}
    
    # Create initial state with the user's message
    # state = ConversationState(
    #     booking_stage="idle",
    #     user_symptoms="",
    #     next_stage="",
    #     tool_call_made="",
    #     next_agent="",
    #     messages=[HumanMessage(content=request.message)]
    # )
    
    # # Run the graph with the current state
    # result = await _graph.ainvoke(state, config=config)
    
    # # print the full state for debugging
    # print("Updated Conversation State:", result)
    
    # # Extract the agent's response (last message in the updated state)
    # agent_response = result
    
        
    # return {
    #     "response": agent_response}