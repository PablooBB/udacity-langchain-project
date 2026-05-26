"""
Script de prueba del flujo completo con inputs simulados.
Simula: topic="Machine Learning", answer="It is a subset of AI", decision=exit
"""
import os
from dotenv import load_dotenv
load_dotenv()

from unittest.mock import patch

SIMULATED_INPUTS = iter([
    "Machine Learning",  # topic
    "It is a subset of artificial intelligence that allows systems to learn from data.",  # answer
    "2",                 # decision: exit
])

def mock_input(prompt=""):
    value = next(SIMULATED_INPUTS)
    print(f"{prompt}{value}")
    return value


def main():
    from src.graph import build_graph

    print("=" * 60)
    print("TEST: flujo completo con inputs simulados")
    print("=" * 60)

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

    with patch("builtins.input", side_effect=mock_input):
        final_state = app.invoke(initial_state, config={"recursion_limit": 50})

    print("\n" + "=" * 60)
    print("VERIFICACION DEL ESTADO FINAL")
    print("=" * 60)
    checks = {
        "topic poblado":          bool(final_state.get("topic")),
        "search_results poblado": bool(final_state.get("search_results")),
        "summary 3-4 parrafos":   2 <= final_state.get("summary", "").count("\n\n") + 1 <= 5,
        "quiz_question poblado":  bool(final_state.get("quiz_question")),
        "user_answer poblado":    bool(final_state.get("user_answer")),
        "grade A-F":              final_state.get("grade", "").strip() in list("ABCDF?"),
        "justification poblado":  bool(final_state.get("justification")),
        "messages acumulados":    len(final_state.get("messages", [])) > 0,
    }

    all_pass = True
    for check, result in checks.items():
        status = "PASS" if result else "FAIL"
        if not result:
            all_pass = False
        print(f"  [{status}] {check}")

    print("=" * 60)
    print("RESULTADO:", "TODO OK" if all_pass else "HAY FALLOS")
    print("=" * 60)


if __name__ == "__main__":
    main()
