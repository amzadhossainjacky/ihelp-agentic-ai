from langgraph.graph import StateGraph, START, END
# for memory saver (local ram)
from langgraph.checkpoint.memory import MemorySaver
# import nodes + state
from nodes.greeting_node import greeting_node
from nodes.name_node import name
from nodes.age import age
from nodes.date_of_birth import date_of_birth
from nodes.general_chat import chat_node
from nodes.node_tracking import tracking_node
from nodes.routing import routing_node
from nodes.invalid_name import invalid_name
from utilities.states.input_state import ChatState

# define memory
check_pointer = MemorySaver()

# define state
graph = StateGraph(ChatState)
# define nodes
graph.add_node("tracking_node", tracking_node)
graph.add_node("routing_node", routing_node)
graph.add_node("greeting", greeting_node)
graph.add_node("name", name)
graph.add_node("age", age)
graph.add_node("date_of_birth", date_of_birth)
graph.add_node("chat_node", chat_node)
# # validation nodes
# graph.add_node("invalid_name", invalid_name)
# define edges
graph.add_edge(START, "tracking_node")
graph.add_conditional_edges("tracking_node", routing_node)
graph.add_edge("greeting", END)
graph.add_edge("name", END)
graph.add_edge("age", END)
graph.add_edge("date_of_birth", END)
graph.add_edge("chat_node", END)


chatbot = graph.compile(checkpointer=check_pointer)

thread_id = "1"

config = {'configurable': {"thread_id": thread_id}}

# print all the history/checkpoints
history = chatbot.get_state_history(config)
# print(history)