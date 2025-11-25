import os
import fitz  # PyMuPDF

def pdf_to_text(path: str) -> str:
    """
    Convertit un fichier PDF en texte brut.
    
    Args:
        path (str): Chemin du fichier PDF.
    
    Returns:
        str: Texte extrait du PDF.
    """
    try:
        doc = fitz.open(path)
        text = ""
        for page in doc:
            text += page.get_text()

        return text.strip()

    except Exception as e:
        raise RuntimeError(f"Erreur lors de la lecture du PDF '{path}': {e}")


def txt_to_text(path: str) -> str:
    """
    Lit un fichier .txt et renvoie son contenu sous forme de texte brut.
    
    Args:
        path (str): Chemin du fichier texte.
    
    Returns:
        str: Contenu du fichier.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        raise RuntimeError(f"Erreur lors de la lecture du fichier texte '{path}': {e}")


def load_file(path: str) -> str:
    """
    Charge un fichier CV ou offre (PDF ou TXT) et retourne son texte.
    
    Args:
        path (str): Chemin du fichier.
    
    Returns:
        str: Texte brut du CV / Job Description.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Le fichier '{path}' n'existe pas.")

    ext = os.path.splitext(path)[1].lower()

    if ext == ".pdf":
        return pdf_to_text(path)
    elif ext == ".txt":
        return txt_to_text(path)
    else:
        raise ValueError("Format non supporté. Utiliser uniquement .pdf ou .txt")


# Fonctions conviviales pour CV et offres
def load_cv(path: str) -> str:
    return load_file(path)


def load_job_description(path: str) -> str:
    return load_file(path)
