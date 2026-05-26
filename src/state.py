from typing import Annotated, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class FlowState(TypedDict):
    messages: Annotated[list, add_messages]
    topic: str
    search_results: str
    summary: str
    quiz_question: str
    user_answer: str
    grade: str
    justification: str
    decision: str  # "restart" | "exit"
