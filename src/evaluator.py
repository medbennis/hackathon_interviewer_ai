from typing import Any, Dict, List, Optional

from src.llm_client import generate_json


def evaluate_answer(
    question: str,
    answer: str,
    job_text: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Évalue la réponse d'un candidat à une question d'entretien.

    Utilise le LLM pour produire une évaluation structurée, par exemple :

    {
      "score": 7,
      "clarity": 4,
      "relevance": 3,
      "alignment": 4,
      "depth": 3,
      "strengths": [...],
      "weaknesses": [...],
      "improvements": [...]
    }

    Args:
        question: La question posée par l'intervieweur.
        answer: La réponse donnée par le candidat.
        job_text: (optionnel) Description du poste / offre, pour évaluer l'alignement.

    Returns:
        Un dictionnaire contenant les scores et commentaires.
    """

    job_context = job_text or "Non spécifiée (concentre-toi sur la qualité générale de la réponse)."

    prompt = f"""
    Tu es un recruteur expérimenté qui évalue une réponse à une question d'entretien.

    Contexte du poste (offre) :
    \"\"\"{job_context}\"\"\"

    Question posée au candidat :
    \"\"\"{question}\"\"\"

    Réponse du candidat :
    \"\"\"{answer}\"\"\"

    Ta tâche :
    Évaluer cette réponse selon les critères suivants :

    - score : note globale sur 10 (entier)
    - clarity : clarté de la réponse (1 à 5)
    - relevance : pertinence par rapport à la question (1 à 5)
    - alignment : adéquation avec le poste / l'offre (1 à 5)
    - depth : profondeur de la réponse (1 à 5) : exemples concrets, détails techniques, etc.
    - strengths : liste de 2 à 4 points forts (chaque élément = une phrase courte)
    - weaknesses : liste de 2 à 4 points faibles ou manques (chaque élément = une phrase courte)
    - improvements : liste de 2 à 5 conseils concrets pour améliorer la réponse
      (par ex : "donner un exemple chiffré", "structurer la réponse avec contexte/action/résultat", etc.)

    Réponds STRICTEMENT avec un JSON du type :

    {{
      "score": 0-10 (entier),
      "clarity": 1-5,
      "relevance": 1-5,
      "alignment": 1-5,
      "depth": 1-5,
      "strengths": [...],
      "weaknesses": [...],
      "improvements": [...]
    }}
    """

    data = generate_json(prompt)

    # Sécurisation minimale des champs attendus
    score = int(data.get("score", 0))
    clarity = int(data.get("clarity", 0))
    relevance = int(data.get("relevance", 0))
    alignment = int(data.get("alignment", 0))
    depth = int(data.get("depth", 0))

    strengths = data.get("strengths", [])
    weaknesses = data.get("weaknesses", [])
    improvements = data.get("improvements", [])

    # Forcer types simples
    if not isinstance(strengths, list):
        strengths = [str(strengths)]
    if not isinstance(weaknesses, list):
        weaknesses = [str(weaknesses)]
    if not isinstance(improvements, list):
        improvements = [str(improvements)]

    result: Dict[str, Any] = {
        "score": score,
        "clarity": clarity,
        "relevance": relevance,
        "alignment": alignment,
        "depth": depth,
        "strengths": [str(s).strip() for s in strengths if s],
        "weaknesses": [str(w).strip() for w in weaknesses if w],
        "improvements": [str(i).strip() for i in improvements if i],
    }

    return result
