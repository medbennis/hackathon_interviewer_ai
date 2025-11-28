# 🎧 Simulateur d’Entretien Intelligent – app.py  

## 🎯 Objectif du projet

L’objectif est de permettre à un étudiant de :

- Charger son **CV** (PDF/TXT)
- Importer la **description du poste**
- Lancer une **simulation d’entretien personnalisée**
- Répondre aux questions en **texte**
- Obtenir un **feedback instantané** :  
  score, pertinence, alignement avec l’offre, points forts, axes d’amélioration
- Recevoir un **rapport final** complet

Cette version reste volontairement simplifiée (sans audio) pour faciliter l’évaluation.

---

## 🚀 Fonctionnalités (version app.py)

### 🔍 Analyse CV / Offre
- Extraction automatique du texte des documents PDF ou TXT
- Identification des compétences pertinentes
- Synthèse de l’adéquation CV ↔ Offre

### 🤖 Génération d’entretien
- Production d’un plan d’entretien intelligent (8 questions)
- Adaptation selon le **profil supposé du recruteur**

### 📝 Évaluation LLM
Pour chaque réponse étudiante :

- Score global /10
- Clarté /5
- Alignement avec l’offre /5
- Pertinence /5
- Profondeur /5
- Points forts
- Points faibles
- Conseils d’amélioration

### 📄 Rapport final généré automatiquement
- Résumé complet des questions
- Réponses du candidat
- Évaluations détaillées
- Recommandations globales

---

## ⚙️ Technologies utilisées

- **Streamlit** : interface utilisateur
- **Python 3.10+** : traitement et logique
- **Fitz/PyMuPDF** : extraction du texte des PDF
- **Groq API** :  
  - LLM pour génération du plan d’entretien  
  - LLM pour évaluer les réponses  
- **Aucune dépendance audio** dans cette version (pas de TTS / STT)

---

