from pydantic import BaseModel, Field

# output class for rag node
class RagOutput(BaseModel):
    AI_response: str = Field(..., description="Response from the AI")
    doctor_names: list[str] = Field(..., description="List of doctor names")
    department_names: list[str] = Field(..., description="List of department names")
    doctor_ids: list[str] = Field(..., description="List of doctor ids")
    