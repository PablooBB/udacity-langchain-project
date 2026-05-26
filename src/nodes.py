import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from .state import FlowState
from .prompts import SUMMARY_PROMPT, QUESTION_PROMPT, GRADING_PROMPT
from .tools import get_tavily_tool


def _get_llm():
    kwargs = {
        "model": "gpt-4o-mini",
        "api_key": os.getenv("OPENAI_API_KEY"),
        "temperature": 0,
    }
    base_url = os.getenv("OPENAI_API_BASE")
    if base_url:
        kwargs["base_url"] = base_url
    return ChatOpenAI(**kwargs)


def node_get_topic(state: FlowState) -> dict:
    print("\n" + "="*60)
    print("LEARNING FLOW - Topic Selection")
    print("="*60)
    topic = input("Enter a topic you want to learn about: ").strip()
    while not topic:
        topic = input("Topic cannot be empty. Please enter a topic: ").strip()
    return {"topic": topic, "messages": [HumanMessage(content=f"I want to learn about: {topic}")]}


def node_search(state: FlowState) -> dict:
    print(f"\nSearching for information about: {state['topic']}...")

    tavily = get_tavily_tool()
    llm_with_tools = _get_llm().bind_tools([tavily])

    # OpenAI generates a tool call to Tavily
    ai_response = llm_with_tools.invoke([
        SystemMessage(content="You are a research assistant. Use the search tool to find information about the given topic."),
        HumanMessage(content=f"Search for information about: {state['topic']}"),
    ])

    messages = [ai_response]
    search_text = ""

    # Execute tool calls made by OpenAI
    for tool_call in ai_response.tool_calls:
        result = tavily.invoke(tool_call["args"])
        if isinstance(result, list):
            search_text = "\n\n".join(
                f"Source: {r.get('url', 'N/A')}\n{r.get('content', '')}"
                for r in result
            )
        else:
            search_text = str(result)

        messages.append(ToolMessage(
            content=search_text,
            tool_call_id=tool_call["id"],
            name=tool_call["name"],
        ))

    return {
        "search_results": search_text,
        "messages": messages,
    }


def node_summarize(state: FlowState) -> dict:
    print("Generating summary...")
    llm = _get_llm()
    prompt = SUMMARY_PROMPT.format(search_results=state["search_results"])
    response = llm.invoke([
        SystemMessage(content="You are a helpful learning assistant. Use only the provided search results."),
        HumanMessage(content=prompt),
    ])
    summary = response.content
    return {
        "summary": summary,
        "messages": [AIMessage(content=f"SUMMARY:\n{summary}")],
    }


def node_generate_question(state: FlowState) -> dict:
    print("Generating quiz question...")
    llm = _get_llm()
    prompt = QUESTION_PROMPT.format(summary=state["summary"])
    response = llm.invoke([
        SystemMessage(content="You are a quiz creator. Use only the provided summary."),
        HumanMessage(content=prompt),
    ])
    question = response.content
    return {
        "quiz_question": question,
        "messages": [AIMessage(content=f"QUIZ QUESTION:\n{question}")],
    }


def node_get_answer(state: FlowState) -> dict:
    print("\n" + "-"*60)
    print("SUMMARY:")
    print(state["summary"])
    print("\n" + "-"*60)
    print("QUIZ QUESTION:")
    print(state["quiz_question"])
    print("-"*60)
    answer = input("Your answer: ").strip()
    while not answer:
        answer = input("Answer cannot be empty: ").strip()
    return {
        "user_answer": answer,
        "messages": [HumanMessage(content=f"My answer: {answer}")],
    }


def node_grade(state: FlowState) -> dict:
    print("\nGrading your answer...")
    llm = _get_llm()
    prompt = GRADING_PROMPT.format(
        summary=state["summary"],
        question=state["quiz_question"],
        answer=state["user_answer"],
    )
    response = llm.invoke([
        SystemMessage(content="You are an academic grader. Use only the provided summary."),
        HumanMessage(content=prompt),
    ])
    raw = response.content
    grade = "?"
    justification = raw

    for line in raw.splitlines():
        if line.lower().startswith("grade:"):
            grade = line.split(":", 1)[1].strip()
        elif line.lower().startswith("justification:"):
            justification = line.split(":", 1)[1].strip()

    return {
        "grade": grade,
        "justification": justification,
        "messages": [AIMessage(content=raw)],
    }


def node_show_results(state: FlowState) -> dict:
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"Topic:     {state['topic']}")
    print(f"Question:  {state['quiz_question']}")
    print(f"Your answer: {state['user_answer']}")
    print(f"\nGrade: {state['grade']}")
    print(f"Justification: {state['justification']}")
    print("="*60)
    return {}


def node_decide(state: FlowState) -> dict:
    print("\nWhat would you like to do next?")
    print("  1. Learn about a new topic")
    print("  2. Exit")
    choice = input("Enter 1 or 2: ").strip()
    while choice not in ("1", "2"):
        choice = input("Please enter 1 or 2: ").strip()
    decision = "restart" if choice == "1" else "exit"
    return {"decision": decision}


def route_decision(state: FlowState) -> str:
    return state.get("decision", "exit")
