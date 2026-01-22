import re
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated, Literal
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
# for add all messages to state
from langgraph.graph.message import add_messages
# for memory saver (local ram)
from langgraph.checkpoint.memory import MemorySaver
import os
import json
from dotenv import load_dotenv
load_dotenv()


llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o-mini")

# define state
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    user_name: str
    user_age: int
    user_email: str
    current_stage: str  # Tracks where we are in the flow

# define node functions
# node - 1
def greeting_node(state: ChatState):
    """
    Purpose: Send initial greeting and ask for name
    Input: state (current conversation state)
    Output: Updates state with greeting message and sets stage
    """
    greeting_message = AIMessage(
        content="Hello! I am a user validation chatbot. Please tell me your name."
    )
    
    return {
        'messages': [greeting_message],
        'current_stage': 'extract_name'      # Move to next stage
    }

# Node 2: Extract Name Node
def extract_name_node(state: ChatState):
    """
    Purpose: Extract name from user's message using LLM
    Process:
    1. Find the last user message
    2. Ask LLM to extract just the name
    3. If valid, save it and move to ask_age stage
    4. If invalid, ask again
    """
    
    # Get the last user message
    last_user_message = None
    for msg in reversed(state['messages']):
        if isinstance(msg, HumanMessage):
            last_user_message = msg.content
            break
    
    # If no user message found, stay in same stage
    if not last_user_message:
        return {'current_stage': 'extract_name'}
    
    # Use LLM to extract the name
    extraction_prompt = f"""Extract only the person's name from the following message. 
Return ONLY the name, nothing else. If you cannot find a name, return "INVALID".

User message: "{last_user_message}"

Name:"""
    
    response = llm.invoke([HumanMessage(content=extraction_prompt)])
    extracted_name = response.content.strip()
    
    # Check if name is valid
    if extracted_name and extracted_name != "INVALID" and len(extracted_name) > 0:
        # Name is valid! Save it and move to next stage
        return {
            'messages': [AIMessage(content=f"Great! I've got your name as {extracted_name}. Now, how old are you?")],
            'user_name': extracted_name,
            'current_stage': 'ask_age'
        }
    
    else:
        # Name is invalid, ask again
        error_message = AIMessage(
            content="I couldn't understand your name. Please tell me your name clearly."
        )

        return {
            'messages': [error_message.content],
            'current_stage': 'extract_name'  # Stay in same stage
        }


# Node 3: Ask Age Node
def ask_age_node(state: ChatState):
    """
    Purpose: Ask for user's age
    Process:
    1. Get the user's name from state
    2. Create a personalized message asking for age
    3. Set stage to 'extract_age' so next user input goes to extract_age_node
    """
    user_name = state.get('user_name', 'there')
    age_message = AIMessage(
        content=f"Nice to meet you, {user_name}! How old are you?"
    )
    return {
        'messages': [age_message.content],
        'current_stage': 'extract_age'
    }


# Node 4: Extract Age Node
def extract_age_node(state: ChatState):
    """
    Purpose: Extract and validate age from user's message using LLM
    Process:
    1. Find the last user message
    2. Ask LLM to extract age and validate it (must be 1-120)
    3. If valid, save it and move to ask_email stage
    4. If invalid, ask again
    """
    
    # Get the last user message
    last_user_message = None
    for msg in reversed(state['messages']):
        if isinstance(msg, HumanMessage):
            last_user_message = msg.content
            break
    
    if not last_user_message:
        return {'current_stage': 'extract_age'}
    
    # Use LLM to extract and validate age
    extraction_prompt = f"""Extract the age from the following message and validate it.
Rules:
- Age must be a number between 1 and 120
- Return ONLY a JSON object with format: {{"age": number, "valid": true/false}}
- If age is invalid or not found, set valid to false

User message: "{last_user_message}"

JSON Response:"""
    
    response = llm.invoke([HumanMessage(content=extraction_prompt)])
    
    # Parse the LLM response
    try:
        response_text = response.content.strip()
        
        # Remove markdown code blocks if LLM adds them
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        # Parse JSON
        result = json.loads(response_text)
        
        # Check if valid
        if result.get('valid', False):
            age = int(result.get('age', 0))
            if 1 <= age <= 120:
                # Age is valid! Save it and move to next stage
                return {
                    'user_age': age,
                    'current_stage': 'ask_email'
                }
    except:
        pass  # If anything fails, treat as invalid
    
    # Age is invalid, ask again
    error_message = AIMessage(
        content="Please provide a valid age (a valid age between 1 and 120)."
    )
    return {
        'messages': [error_message.content],
        'current_stage': 'extract_age'  # Stay in same stage
    }

# Node 5: Ask for Email
def ask_email_node(state: ChatState):
    """Ask for user's email"""
    email_message = AIMessage(content="Great! Now, please provide your email address.")
    return {
        'messages': [email_message],
        'current_stage': 'extract_email'
    }


# Node 6: Extract and Validate Email using LLM
def extract_email_node(state: ChatState):
    """Extract and validate email from user input using LLM"""
    last_user_message = None
    for msg in reversed(state['messages']):
        if isinstance(msg, HumanMessage):
            last_user_message = msg.content
            break
    
    if not last_user_message:
        return {'current_stage': 'extract_email'}
    
    # Use LLM to extract and validate email
    extraction_prompt = f"""Extract the email address from the following message and validate it.
Rules:
- Email must have format: something@domain.extension
- Return ONLY a JSON object with format: {{"email": "extracted_email", "valid": true/false}}
- If email is invalid or not found, set valid to false

User message: "{last_user_message}"

JSON Response:"""
    
    response = llm.invoke([HumanMessage(content=extraction_prompt)])
    
    try:
        # Extract JSON from response
        response_text = response.content.strip()
        # Remove markdown code blocks if present
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(response_text)
        
        if result.get('valid', False):
            email = result.get('email', '').strip()
            # Additional regex validation
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if re.match(email_pattern, email):
                return {
                    'user_email': email,
                    'current_stage': 'complete'
                }
    except:
        pass
    
    error_message = AIMessage(content="Please provide a valid email address (e.g., example@email.com).")
    
    return {
        'messages': [error_message],
        'current_stage': 'extract_email'
    }

    

# Node 7: Complete and Thank User
def complete_node(state: ChatState):
    """Thank user and confirm all information"""
    user_name = state.get('user_name', 'User')
    user_age = state.get('user_age', 'N/A')
    user_email = state.get('user_email', 'N/A')
    
    completion_message = AIMessage(
        content=f"""Thank you, {user_name}! I have successfully validated your information:

• Name: {user_name}
• Age: {user_age}
• Email: {user_email}

All information has been validated and saved. How can I help you today?"""
    )
    return {
        'messages': [completion_message.content],
        'current_stage': 'complete'
    }

# Node 8: General Chat (after completion)
def general_chat_node(state: ChatState):
    """Handle general conversation after validation is complete"""
    user_name = state.get('user_name', 'User')
    user_age = state.get('user_age', 'unknown')
    user_email = state.get('user_email', 'unknown')
    
    system_prompt = f"""You are a helpful assistant. The user's information:
- Name: {user_name}
- Age: {user_age}
- Email: {user_email}

Answer their questions helpfully and professionally."""
    
    # Get last few messages for context
    recent_messages = state['messages'][-6:]
    messages_for_llm = [SystemMessage(content=system_prompt)] + recent_messages
    
    response = llm.invoke(messages_for_llm)
    
    return {
        'messages': [response],
        'current_stage': 'complete'
    }
    
# previous chat node
def chat_node(state: ChatState):
    all_messages = state['messages']
    llm_response = llm.invoke(all_messages)
    return {'messages': [llm_response]}


############ Routing Functions ###################

# This decides which node to go to next based on current_stage
def route_after_start(state: ChatState) -> Literal["greeting_node", "extract_name_node", "ask_age_node", "ask_email_node", "complete_node", "general_chat_node"]:
    """Route based on current stage and whether there's a new user message"""
    current_stage = state.get('current_stage', 'greeting')
    
    # Check if there's a new user message (last message is from user)
    has_new_user_message = False
    if state.get('messages'):
        last_message = state['messages'][-1]
        has_new_user_message = isinstance(last_message, HumanMessage)
    
    # Initial greeting
    if not current_stage or current_stage == 'greeting':
        return "greeting_node"
    
    # If we're in complete stage and user sends a message, go to general chat
    if current_stage == 'complete' and has_new_user_message:
        return "general_chat_node"
    
    # If complete but no new message, stay at complete
    if current_stage == 'complete':
        return "complete_node"
    
    # Route based on current stage
    stage_map = {
        'extract_name': 'extract_name_node',
        'ask_age': 'ask_age_node',
        'extract_age': 'extract_age_node',
        'ask_email': 'ask_email_node',
        'extract_email': 'extract_email_node',
    }
    
    return stage_map.get(current_stage, 'greeting_node')

def route_after_extraction(state: ChatState) -> Literal["ask_age_node", "ask_email_node", "complete_node", "extract_name_node", "extract_age_node", "extract_email_node", END]:
    """Route to next step after extraction"""
    current_stage = state.get('current_stage', 'greeting')
    
    if current_stage == 'ask_age':
        return "ask_age_node"
    elif current_stage == 'extract_age':
        return END
    elif current_stage == 'ask_email':
        return "ask_email_node"
    elif current_stage == 'extract_email':
        return END
    elif current_stage == 'complete':
        return "complete_node"
    elif current_stage == 'extract_name':
        return END
    
    return END


# define memory
check_pointer = MemorySaver()

# define state
graph = StateGraph(ChatState)

# define nodes
graph.add_node("greeting_node", greeting_node)
graph.add_node("extract_name_node", extract_name_node)
graph.add_node("ask_age_node", ask_age_node)
graph.add_node("extract_age_node", extract_age_node)
graph.add_node("ask_email_node", ask_email_node)
graph.add_node("extract_email_node", extract_email_node)
graph.add_node("complete_node", complete_node)
graph.add_node("general_chat_node", general_chat_node)
# graph.add_node("chat_node", chat_node)

# define edges
# Add conditional edge from START
# This will call route_from_start() to decide where to go
graph.add_conditional_edges(
    START,
    route_after_start,
    {
        "greeting_node": "greeting_node",
        "extract_name_node": "extract_name_node",
        "ask_age_node": "ask_age_node",
        "extract_age_node": "extract_age_node",
        "ask_email_node": "ask_email_node",
        "extract_email_node": "extract_email_node",
        "complete_node": "complete_node",
        "general_chat_node": "general_chat_node",
    }
)

# Both nodes end the conversation for now
graph.add_conditional_edges("greeting_node", route_after_extraction)
graph.add_conditional_edges("extract_name_node", route_after_extraction)
graph.add_conditional_edges("ask_age_node", route_after_extraction)
graph.add_conditional_edges("extract_age_node", route_after_extraction)
graph.add_conditional_edges("ask_email_node", route_after_extraction)
graph.add_conditional_edges("extract_email_node", route_after_extraction)
graph.add_conditional_edges("complete_node", route_after_extraction)
graph.add_edge("general_chat_node", END)

chatbot = graph.compile(checkpointer=check_pointer)

thread_id = "1"

config = {'configurable': {"thread_id": thread_id}}



# response = chatbot.invoke({'messages': [SystemMessage(content="You are a helpful chatbot."),
#                                         HumanMessage(content="Hello, my name is pranto")]}, config=config)
# print(chatbot.get_state(config=config).values['messages'])
   

# initial_state = {'messages': [SystemMessage(content="You are a helpful chatbot."),
#                                   HumanMessage(content=user_input)]}
# response = chatbot.invoke(initial_state, config=config)
# print("Chatbot: " + response['messages'][-1].content)