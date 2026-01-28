from utilities.states.input_state import ChatState
from utilities.llms.chat_llm import chat_llm


def chat_node(state: ChatState):
    llm_response = chat_llm.invoke(state["messages"])
    return {"messages": [llm_response]}

