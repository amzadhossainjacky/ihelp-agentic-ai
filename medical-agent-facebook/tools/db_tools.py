from langchain_core.tools import tool
from graph.state import ConversationState

# test db operation tool
@tool
def db_operation_test(query: str) -> str:
    """Test database operation."""
    # update conversation state
    ConversationState.tool_call_made = "db_operation_test"
    print(f"tool: Database operation tool called with query: {query}")
    return "Database operation tool call successful!"