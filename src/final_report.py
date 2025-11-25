from typing import Any, Dict, List

from src.llm_client import generate_text


def _compute_score_stats(history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calcule quelques statistiques simples à partir de l'historique :
    - moyenne des scores
    - moyenne des critères (clarity, relevance, alignment, depth)
    - nombre de questions traitées
    """
    if not history:
        return {
            "n_questions": 0,
            "avg_score": 0.0,
            "avg_clarity": 0.0,
            "avg_relevance": 0.0,
            "avg_alignment": 0.0,
            "avg_depth": 0.0,
        }

    n = 0
    total_score = 0
    total_clarity = 0
    total_relevance = 0
    total_alignment = 0
    total_depth = 0

    for record in history:
        eval_ = record.get("evaluation", {})
        total_score += int(eval_.get("score", 0))
        total_clarity += int(eval_.get("clarity", 0))
        total_relevance += int(eval_.get("relevance", 0))
        total_alignment += int(eval_.get("alignment", 0))
        total_depth += int(eval_.get("depth", 0))
        n += 1

    if n == 0:
        n = 1  # éviter division par 0, même si déjà checké

    return {
        "n_questions": n,
        "avg_score": total_score / n,
        "avg_clarity": total_clarity / n,
        "avg_relevance": total_relevance / n,
        "avg_alignment": total_alignment / n,
        "avg_depth": total_depth / n,
    }


def _build_text_summary_for_llm(history: List[Dict[str, Any]], stats: Dict[str, Any]) -> str:
    """
    Construit un résumé textuel brut de l'historique et des stats,
    pour le donner au LLM dans le prompt.
    """
    lines = []

    lines.append(f"Nombre de questions posées : {stats['n_questions']}")
    lines.append(
        "Moyennes des scores : "
        f"score global = {stats['avg_score']:.2f} / 10, "
        f"clarté = {stats['avg_clarity']:.2f} / 5, "
        f"pertinence = {stats['avg_relevance']:.2f} / 5, "
        f"alignement = {stats['avg_alignment']:.2f} / 5, "
        f"profondeur = {stats['avg_depth']:.2f} / 5."
    )
    lines.append("\nDétail question par question :")

    for i, record in enumerate(history, start=1):
        q = record.get("question", "")
        a = record.get("answer", "")
        eval_ = record.get("evaluation", {})

        score = eval_.get("score", "?")
        clarity = eval_.get("clarity", "?")
        relevance = eval_.get("relevance", "?")
        alignment = eval_.get("alignment", "?")
        depth = eval_.get("depth", "?")

        lines.append(f"\nQuestion {i} : {q}")
        lines.append(f"Réponse du candidat : {a}")
        lines.append(
            f"Scores -> global: {score}/10, clarté: {clarity}/5, "
            f"pertinence: {relevance}/5, alignement: {alignment}/5, profondeur: {depth}/5"
        )

    return "\n".join(lines)


def generate_final_report(history: List[Dict[str, Any]]) -> str:
    """
    Génère un rapport final d'entretien à partir de l'historique complet.

    Le rapport contient typiquement :
    - un résumé global du candidat
    - les forces principales
    - les faiblesses principales
    - une interprétation des scores
    - des conseils concrets pour progresser
    """
    if not history:
        return (
            "Aucun historique d'entretien fourni. "
            "Le rapport final ne peut pas être généré."
        )

    stats = _compute_score_stats(history)
    raw_summary = _build_text_summary_for_llm(history, stats)

    prompt = f"""
    Tu es un coach d'entretien professionnel.

    On te donne ci-dessous :
    - un résumé chiffré des performances du candidat
    - le détail de chaque question, de la réponse et des scores associés.

    Données :

    {raw_summary}

    Ta tâche :
    Rédiger un RAPPORT FINAL structuré pour le candidat, en français, comprenant :

    1. Une introduction : ton impression générale sur le candidat (5-7 phrases).
    2. Un paragraphe "Synthèse des performances chiffrées" :
       - interprète les moyennes des scores (score global, clarté, pertinence, alignement, profondeur).
    3. Une section "Points forts" :
       - liste à puces de 4 à 6 forces clés observées.
    4. Une section "Points à améliorer" :
       - liste à puces de 4 à 6 faiblesses ou axes d'amélioration.
    5. Une section "Conseils concrets pour progresser" :
       - 5 à 8 actions concrètes que le candidat peut mettre en place
         dans les 2 à 3 semaines avant un vrai entretien (exemples précis).
    6. Une courte conclusion motivante (2-3 phrases).

    Format attendu :
    - Utilise des titres clairs (par ex : 'Introduction', 'Points forts', etc.).
    - Utilise des listes à puces là où c'est pertinent.
    - Adopte un ton bienveillant mais honnête.
    """

    report = generate_text(prompt, max_tokens=900)

    return report
