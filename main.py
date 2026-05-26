import os
from dotenv import load_dotenv

load_dotenv()

from src.graph import build_graph


def main():
    _check_api_keys()
    app = build_graph()
    initial_state = {
        "messages": [],
        "topic": "",
        "search_results": "",
        "summary": "",
        "quiz_question": "",
        "user_answer": "",
        "grade": "",
        "justification": "",
        "decision": "",
    }
    app.invoke(initial_state, config={"recursion_limit": 50})
    print("\nThank you for using the Learning Flow. Goodbye!")


def _check_api_keys():
    missing = []
    if not os.getenv("OPENAI_API_KEY"):
        missing.append("OPENAI_API_KEY")
    if not os.getenv("TAVILY_API_KEY"):
        missing.append("TAVILY_API_KEY")
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            "Create a .env file based on .env.example and add your API keys."
        )
    if os.getenv("OPENAI_API_BASE"):
        print(f"Using custom OpenAI base URL: {os.getenv('OPENAI_API_BASE')}")


if __name__ == "__main__":
    main()
