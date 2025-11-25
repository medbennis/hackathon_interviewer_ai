from typing import Any, Dict, List, Set

from src.llm_client import generate_json, generate_text


def _normalize_skills(skills: List[str]) -> Set[str]:
    """
    Normalise une liste de compétences en minuscules, sans doublons.
    """
    return {s.strip().lower() for s in skills if s and isinstance(s, str)}


def extract_cv_info(cv_text: str) -> Dict[str, Any]:
    """
    Utilise le LLM pour extraire les informations importantes du CV.

    Retourne un dict du type :
    {
        "hard_skills": [...],
        "soft_skills": [...],
        "languages": [...],
        "projects": [
            {"title": "...", "description": "..."},
            ...
        ],
        "summary": "Résumé en 3-4 phrases du profil"
    }
    """
    prompt = f"""
    Tu es un assistant RH spécialisé en profils Data/Tech.
    Analyse le CV ci-dessous et renvoie STRICTEMENT un JSON avec les clés :

    - hard_skills : liste de chaînes (ex: ["python", "sql", "machine learning"])
    - soft_skills : liste de chaînes (ex: ["communication", "travail en équipe"])
    - languages   : liste de langues parlées (ex: ["français", "anglais B2"])
    - projects    : liste d'objets avec les clés "title" et "description"
    - summary     : une courte description (3-4 phrases) du profil du candidat

    CV :
    \"\"\"{cv_text}\"\"\"
    """

    data = generate_json(prompt)

    # Sécurisation minimale des champs attendus
    data.setdefault("hard_skills", [])
    data.setdefault("soft_skills", [])
    data.setdefault("languages", [])
    data.setdefault("projects", [])
    data.setdefault("summary", "")

    return data


def extract_job_info(job_text: str) -> Dict[str, Any]:
    """
    Utilise le LLM pour extraire les infos importantes de l'offre.

    Retourne un dict du type :
    {
        "title": "...",
        "company": "...",
        "location": "...",
        "hard_skills_required": [...],
        "soft_skills_required": [...],
        "missions": [...],
        "summary": "Résumé de l'offre en 3-4 phrases"
    }
    """
    prompt = f"""
    Tu es un assistant RH.
    Analyse l'offre de stage/emploi suivante et renvoie STRICTEMENT un JSON avec les clés :

    - title                 : titre du poste
    - company               : nom de l'entreprise si identifiable (sinon null ou "")
    - location              : localisation principale si identifiable (sinon null ou "")
    - hard_skills_required  : liste de compétences techniques attendues
    - soft_skills_required  : liste de compétences non techniques attendues
    - missions              : liste de 3 à 7 phrases décrivant les missions principales
    - summary               : résumé en 3-4 phrases de l'offre

    Offre :
    \"\"\"{job_text}\"\"\"
    """

    data = generate_json(prompt)

    data.setdefault("title", "")
    data.setdefault("company", "")
    data.setdefault("location", "")
    data.setdefault("hard_skills_required", [])
    data.setdefault("soft_skills_required", [])
    data.setdefault("missions", [])
    data.setdefault("summary", "")

    return data


def build_profile(cv_text: str, job_text: str) -> Dict[str, Any]:
    """
    Construit un profil combiné à partir du CV et de l'offre.

    Retourne un dict du type :
    {
        "cv": { ... infos CV ... },
        "job": { ... infos offre ... },
        "overlap_hard_skills": [...],
        "missing_hard_skills": [...],
        "overlap_soft_skills": [...],
        "missing_soft_skills": [...],
        "fit_summary": "Texte expliquant le matching global"
    }
    """
    cv_info = extract_cv_info(cv_text)
    job_info = extract_job_info(job_text)

    cv_hard = _normalize_skills(cv_info.get("hard_skills", []))
    job_hard = _normalize_skills(job_info.get("hard_skills_required", []))

    cv_soft = _normalize_skills(cv_info.get("soft_skills", []))
    job_soft = _normalize_skills(job_info.get("soft_skills_required", []))

    overlap_hard = sorted(cv_hard & job_hard)
    missing_hard = sorted(job_hard - cv_hard)

    overlap_soft = sorted(cv_soft & job_soft)
    missing_soft = sorted(job_soft - cv_soft)

    # Résumé global du "fit" pour alimenter les autres modules
    fit_prompt = f"""
    Tu es un recruteur data.
    Voici un résumé du CV et de l'offre, ainsi que les compétences communes et manquantes.

    Résumé du CV :
    {cv_info.get("summary", "")}

    Résumé de l'offre :
    {job_info.get("summary", "")}

    Compétences techniques en commun :
    {overlap_hard}

    Compétences techniques manquantes :
    {missing_hard}

    Compétences soft en commun :
    {overlap_soft}

    Compétences soft manquantes :
    {missing_soft}

    Écris un court paragraphe (5-7 phrases) qui évalue :
    - l'adéquation globale du profil au poste,
    - les points forts majeurs,
    - les principaux manques,
    - et ce sur quoi le candidat devrait insister pendant l'entretien.
    """

    fit_summary = generate_text(fit_prompt, max_tokens=400)

    profile = {
        "cv": cv_info,
        "job": job_info,
        "overlap_hard_skills": overlap_hard,
        "missing_hard_skills": missing_hard,
        "overlap_soft_skills": overlap_soft,
        "missing_soft_skills": missing_soft,
        "fit_summary": fit_summary,
    }

    return profile
