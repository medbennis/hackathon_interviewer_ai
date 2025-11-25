from typing import Any, Dict, List

from src.llm_client import generate_json


def generate_interview_plan(
    profile: Dict[str, Any],
    interviewer_profile: str,
    n_questions: int = 8,
) -> List[Dict[str, Any]]:
    """
    Génère un plan d'entretien (liste de questions) à partir :
    - du profil combiné (CV + offre) construit par analyze_inputs.build_profile
    - d'une description textuelle de l'intervieweur
    - d'un nombre cible de questions.

    Le plan retourné est une liste de dictionnaires de la forme :
    {
        "type": "intro" | "motivation" | "technique" | "projet" | "soft_skill" | "conclusion",
        "topic": "thème de la question",
        "question": "texte de la question que posera l'intervieweur"
    }

    Args:
        profile: dict contenant les infos CV/Job + overlaps, tel que retourné par build_profile().
        interviewer_profile: courte description de l'intervieweur
            (ex: "manager technique backend exigeant, ton direct").
        n_questions: nombre de questions dans l'entretien (recommandé: 6–10).

    Returns:
        Liste de questions structurées.
    """

    cv_info = profile.get("cv", {})
    job_info = profile.get("job", {})

    overlap_hard = profile.get("overlap_hard_skills", [])
    overlap_soft = profile.get("overlap_soft_skills", [])
    missing_hard = profile.get("missing_hard_skills", [])
    missing_soft = profile.get("missing_soft_skills", [])

    cv_summary = cv_info.get("summary", "")
    job_summary = job_info.get("summary", "")
    job_title = job_info.get("title", "")
    company = job_info.get("company", "")

    prompt = f"""
    Tu es un recruteur qui prépare un entretien d'embauche.

    Tu disposes des informations suivantes :

    1) Résumé du CV du candidat :
    {cv_summary}

    2) Résumé de l'offre :
    {job_summary}

    3) Titre du poste : {job_title}
       Entreprise : {company}

    4) Compétences techniques en commun (CV ∩ offre) :
    {overlap_hard}

    5) Compétences techniques manquantes côté candidat (attendues par l'offre) :
    {missing_hard}

    6) Compétences soft en commun :
    {overlap_soft}

    7) Compétences soft manquantes :
    {missing_soft}

    8) Profil de l'intervieweur :
    {interviewer_profile}

    Ta tâche :
    Proposer un plan d'entretien structuré avec exactement {n_questions} questions,
    adaptées à ce candidat et à ce poste.

    Le plan doit couvrir au minimum :
    - 1 question d'introduction / présentation
    - 1 à 2 questions de motivation (poste + entreprise)
    - 2 à 3 questions techniques (en priorité sur les compétences en commun)
    - 1 question sur un ou plusieurs projets du CV
    - 1 à 2 questions soft skills / comportementales
    - 1 question de conclusion (ex: "avez-vous des questions ?")

    Pour chaque question, renvoie un objet JSON avec les clés :
    - "type" : un mot clé parmi
        ["intro", "motivation", "technique", "projet", "soft_skill", "conclusion"]
    - "topic" : une courte phrase décrivant le thème (ex: "motivation pour le poste",
        "compétences Python", "projet de classification d'images", "travail en équipe")
    - "question" : la question exacte que l'intervieweur posera au candidat,
        en français, dans un ton cohérent avec le profil de l'intervieweur.

    IMPORTANT :
    - Réponds STRICTEMENT avec un JSON au format suivant :
      [
        {{
          "type": "...",
          "topic": "...",
          "question": "..."
        }},
        ...
      ]
    - Pas de texte en dehors du JSON.
    """

    plan = generate_json(prompt)
    # On s'assure que c'est bien une liste, sinon on encapsule
    if isinstance(plan, dict):
        plan = [plan]

    # Filtrage léger de sécurité : on ne garde que les éléments bien formés
    cleaned_plan: List[Dict[str, Any]] = []
    for item in plan:
        if not isinstance(item, dict):
            continue
        q_type = item.get("type")
        topic = item.get("topic")
        question = item.get("question")
        if not question:
            continue
        cleaned_plan.append(
            {
                "type": q_type or "autre",
                "topic": topic or "",
                "question": question.strip(),
            }
        )

    return cleaned_plan


def pretty_print_plan(plan: List[Dict[str, Any]]) -> None:
    """
    Affiche le plan d'entretien de manière lisible dans le terminal.
    Utile pour la démo ou le debug.
    """
    for i, q in enumerate(plan, start=1):
        q_type = q.get("type", "inconnu")
        topic = q.get("topic", "")
        question = q.get("question", "")

        print(f"\n--- Question {i} ---")
        print(f"Type   : {q_type}")
        if topic:
            print(f"Thème  : {topic}")
        print(f"Texte  : {question}")
