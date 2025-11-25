from typing import Any, Dict, List, Optional

from src.evaluator import evaluate_answer


def ask_one_question(
    question_item: Dict[str, Any],
    job_text: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Pose une question (via le terminal), récupère la réponse et l'évalue.

    Args:
        question_item: un élément du plan, ex:
            {
              "type": "technique",
              "topic": "Python",
              "question": "Parlez-moi de votre expérience avec Python."
            }
        job_text: texte de l'offre pour aider l'évaluation.

    Returns:
        Un dict de la forme :
        {
          "question": "...",
          "type": "...",
          "topic": "...",
          "answer": "...",
          "evaluation": {...}
        }
    """
    q_type = question_item.get("type", "inconnu")
    topic = question_item.get("topic", "")
    question = question_item.get("question", "")

    print("\n==============================")
    print(f"TYPE   : {q_type}")
    if topic:
        print(f"THÈME  : {topic}")
    print(f"QUESTION : {question}")
    print("==============================")

    answer = input("\nVotre réponse (candidat) :\n> ")

    evaluation = evaluate_answer(question=question, answer=answer, job_text=job_text)

    print("\n---- FEEDBACK AUTOMATIQUE ----")
    print(f"Score global   : {evaluation.get('score', '?')} / 10")
    print(f"Clarté         : {evaluation.get('clarity', '?')} / 5")
    print(f"Pertinence     : {evaluation.get('relevance', '?')} / 5")
    print(f"Alignement     : {evaluation.get('alignment', '?')} / 5")
    print(f"Profondeur     : {evaluation.get('depth', '?')} / 5")

    strengths = evaluation.get("strengths", [])
    weaknesses = evaluation.get("weaknesses", [])
    improvements = evaluation.get("improvements", [])

    if strengths:
        print("\nPoints forts :")
        for s in strengths:
            print(f"  - {s}")

    if weaknesses:
        print("\nPoints faibles :")
        for w in weaknesses:
            print(f"  - {w}")

    if improvements:
        print("\nPistes d'amélioration :")
        for i in improvements:
            print(f"  - {i}")

    # On retourne tout pour l'historique
    return {
        "question": question,
        "type": q_type,
        "topic": topic,
        "answer": answer,
        "evaluation": evaluation,
    }


def run_interview(
    plan: List[Dict[str, Any]],
    cv_text: str,
    job_text: Optional[str] = None,
    max_questions: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Lance une simulation d'entretien interactive dans le terminal.

    Args:
        plan: liste de questions produites par generate_interview_plan().
        cv_text: texte du CV (non utilisé directement ici mais disponible si tu veux l'afficher plus tard).
        job_text: description de l'offre (utilisée pour évaluer l'alignement).
        max_questions: limite du nombre de questions (si None, on utilise tout le plan).

    Returns:
        Une liste 'history' :
        [
          {
            "question": "...",
            "type": "...",
            "topic": "...",
            "answer": "...",
            "evaluation": {...}
          },
          ...
        ]
    """
    history: List[Dict[str, Any]] = []

    if max_questions is None or max_questions > len(plan):
        max_q = len(plan)
    else:
        max_q = max_questions

    print("\n========================================")
    print(" DÉBUT DE LA SIMULATION D'ENTRETIEN ")
    print("========================================")
    print(f"Nombre de questions prévues : {max_q}\n")

    for i, q_item in enumerate(plan[:max_q], start=1):
        print(f"\n>>> QUESTION {i} / {max_q}")
        record = ask_one_question(q_item, job_text=job_text)
        history.append(record)

        # Option : proposer de stopper avant la fin du plan
        cont = input("\nContinuer l'entretien ? (Entrée = oui, 'n' = non) : ").strip().lower()
        if cont == "n":
            print("\nFin anticipée de l'entretien à la demande du candidat.")
            break

    print("\n========================================")
    print(" FIN DE LA SIMULATION D'ENTRETIEN ")
    print("========================================\n")

    return history
