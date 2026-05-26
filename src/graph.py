from langgraph.graph import StateGraph, START, END
from .state import FlowState
from .nodes import (
    node_get_topic,
    node_search,
    node_summarize,
    node_generate_question,
    node_get_answer,
    node_grade,
    node_show_results,
    node_decide,
    route_decision,
)


def build_graph() -> StateGraph:
    graph = StateGraph(FlowState)

    graph.add_node("get_topic", node_get_topic)
    graph.add_node("search", node_search)
    graph.add_node("summarize", node_summarize)
    graph.add_node("generate_question", node_generate_question)
    graph.add_node("get_answer", node_get_answer)
    graph.add_node("grade", node_grade)
    graph.add_node("show_results", node_show_results)
    graph.add_node("decide", node_decide)

    graph.add_edge(START, "get_topic")
    graph.add_edge("get_topic", "search")
    graph.add_edge("search", "summarize")
    graph.add_edge("summarize", "generate_question")
    graph.add_edge("generate_question", "get_answer")
    graph.add_edge("get_answer", "grade")
    graph.add_edge("grade", "show_results")
    graph.add_edge("show_results", "decide")

    graph.add_conditional_edges(
        "decide",
        route_decision,
        {
            "restart": "get_topic",
            "exit": END,
        },
    )

    return graph.compile()
