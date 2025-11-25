# 🎧 Interview-AI  
### Simulateur d’entretien intelligent (Hackathon 2025)

Interview-AI est une application interactive permettant aux étudiants de s’entraîner à passer des entretiens de stage grâce à l’intelligence artificielle.  
Le système analyse le CV, l’offre de stage et le profil du recruteur pour générer une simulation personnalisée, réaliste et interactive.

---

## 🚀 Fonctionnalités principales

### 🔍 Analyse
- Extraction automatique du texte des PDF/TXT (CV + offre).
- Détection des compétences requises / compétences présentes.
- Génération d’un résumé d’adéquation CV ↔ Offre.

### 🤖 Simulation d’entretien
- Génération d’un **plan d’entretien personnalisé** (8 questions).
- Questions adaptées au poste et au profil du recruteur.
- Deux modes :
  - **Mode texte**
  - **Mode audio (avancé)**  
    - TTS : lecture des questions  
    - STT : transcription des réponses orales avec Whisper  

### 📝 Évaluation intelligente
- Analyse de la réponse du candidat via LLM.
- Scoring : clarté, alignement, pertinence, profondeur.
- Points forts, points faibles et pistes d’amélioration.

### 📄 Rapport final
- Génération d’un compte-rendu complet après l'entretien.
- Export textuel via l’application.