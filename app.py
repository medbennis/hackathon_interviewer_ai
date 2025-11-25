import os
import fitz
import streamlit as st

from src.analyze_inputs import build_profile
from src.plan_interview import generate_interview_plan
from src.evaluator import evaluate_answer
from src.final_report import generate_final_report
from src.tts import question_to_audio
from src.stt import transcribe_audio


# ---------- Configuration de la page ----------

st.set_page_config(
    page_title="Simulateur d'Entretien RH",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- CSS Personnalisé ----------

st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Variables CSS */
    :root {
        --primary-color: #2E86DE;
        --secondary-color: #54A0FF;
        --success-color: #10AC84;
        --warning-color: #F39C12;
        --danger-color: #EE5A6F;
        --dark-bg: #1E1E2E;
        --light-bg: #F8F9FA;
        --card-bg: #FFFFFF;
        --text-primary: #2C3E50;
        --text-secondary: #7F8C8D;
        --border-color: #E1E8ED;
        --shadow: 0 2px 8px rgba(0,0,0,0.08);
        --shadow-hover: 0 4px 16px rgba(0,0,0,0.12);
    }
    
    /* Style général */
    .main {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
    }
    
    /* Container principal */
    .main > div {
        background: var(--light-bg);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
    }
    
    /* Titre principal */
    h1 {
        color: var(--text-primary);
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Sous-titres */
    h2 {
        color: var(--text-primary);
        font-weight: 600;
        font-size: 1.75rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-left: 4px solid var(--primary-color);
        padding-left: 1rem;
    }
    
    h3 {
        color: var(--text-primary);
        font-weight: 600;
        font-size: 1.25rem;
        margin-top: 1.5rem;
    }
    
    /* Cards personnalisées */
    .card {
        background: var(--card-bg);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: var(--shadow);
        transition: all 0.3s ease;
        border: 1px solid var(--border-color);
    }
    
    .card:hover {
        box-shadow: var(--shadow-hover);
        transform: translateY(-2px);
    }
    
    /* Badges de statut */
    .status-badge {
        display: inline-block;
        padding: 0.35rem 0.85rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    
    .badge-success {
        background: #D4EDDA;
        color: #155724;
    }
    
    .badge-warning {
        background: #FFF3CD;
        color: #856404;
    }
    
    .badge-info {
        background: #D1ECF1;
        color: #0C5460;
    }
    
    /* Boutons stylisés */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* File uploader */
    .stFileUploader {
        background: var(--card-bg);
        border-radius: 10px;
        padding: 1rem;
        border: 2px dashed var(--border-color);
        transition: all 0.3s ease;
    }
    
    .stFileUploader:hover {
        border-color: var(--primary-color);
        background: #F0F4FF;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: var(--card-bg);
        border-radius: 10px;
        border: 1px solid var(--border-color);
        font-weight: 600;
        color: var(--text-primary);
    }
    
    .streamlit-expanderHeader:hover {
        background: #F8F9FA;
        border-color: var(--primary-color);
    }
    
    /* Text area */
    .stTextArea textarea {
        border-radius: 10px;
        border: 2px solid var(--border-color);
        font-family: 'Inter', sans-serif;
    }
    
    .stTextArea textarea:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Alerts */
    .stAlert {
        border-radius: 10px;
        border: none;
        padding: 1rem 1.5rem;
    }
    
    /* Score display */
    .score-container {
        display: flex;
        justify-content: space-around;
        flex-wrap: wrap;
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .score-item {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        text-align: center;
        flex: 1;
        min-width: 120px;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .score-label {
        font-size: 0.85rem;
        opacity: 0.9;
        margin-bottom: 0.5rem;
    }
    
    .score-value {
        font-size: 2rem;
        font-weight: 700;
    }
    
    /* Question counter */
    .question-counter {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1.5rem;
        border-radius: 20px;
        display: inline-block;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--primary-color), transparent);
        margin: 2rem 0;
    }
    
    /* Audio player */
    audio {
        width: 100%;
        border-radius: 10px;
    }
    
    /* Lists */
    ul {
        list-style: none;
        padding-left: 0;
    }
    
    li {
        padding: 0.5rem 0;
        padding-left: 1.5rem;
        position: relative;
    }
    
    li:before {
        content: "▸";
        color: var(--primary-color);
        font-weight: bold;
        position: absolute;
        left: 0;
    }
    
    /* Columns spacing */
    .row-widget.stHorizontal > div {
        padding: 0 0.5rem;
    }
    
    /* Info box */
    .info-box {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
        border-left: 4px solid #2196F3;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .success-box {
        background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
        border-left: 4px solid #4CAF50;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%);
        border-left: 4px solid #FF9800;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)


# ---------- Helpers ----------

def read_uploaded_file(file) -> str:
    """
    Lit un fichier uploadé (PDF ou texte) et renvoie son contenu texte.
    """
    if file is None:
        return ""

    filename = file.name.lower()

    # PDF
    if filename.endswith(".pdf"):
        file_bytes = file.read()
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text.strip()

    # Texte brut
    else:
        try:
            return file.read().decode("utf-8").strip()
        except Exception:
            return file.read().decode(errors="ignore").strip()


# ---------- Initialisation de l'état de session ----------

if "profile" not in st.session_state:
    st.session_state.profile = None

if "plan" not in st.session_state:
    st.session_state.plan = []

if "current_question_index" not in st.session_state:
    st.session_state.current_question_index = 0

if "history" not in st.session_state:
    st.session_state.history = []

if "job_text" not in st.session_state:
    st.session_state.job_text = ""

if "cv_text" not in st.session_state:
    st.session_state.cv_text = ""

if "transcriptions" not in st.session_state:
    st.session_state.transcriptions = {}


# ---------- Interface Streamlit ----------

# Header avec logo et titre
col_header1, col_header2 = st.columns([3, 1])
with col_header1:
    st.title("🎯 Simulateur d'Entretien RH")
    st.markdown("""
        <div class="info-box">
            <strong>Préparez-vous efficacement à votre entretien d'embauche</strong><br>
            Une solution intelligente utilisant l'IA pour analyser votre profil et simuler un entretien professionnel
        </div>
    """, unsafe_allow_html=True)

# Vérification clé Groq
if not os.getenv("GROQ_API_KEY"):
    st.markdown("""
        <div class="warning-box">
            ⚠️ <strong>Configuration requise</strong><br>
            La variable d'environnement <code>GROQ_API_KEY</code> n'est pas définie.<br>
            Dans CMD : <code>setx GROQ_API_KEY "ta_cle_ici"</code> puis redémarrez votre terminal/VS Code.
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# ---------- Section 1 : Upload des documents ----------

st.markdown("## 📄 Étape 1 : Chargement des documents")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 👤 Votre CV")
    cv_file = st.file_uploader(
        "Uploadez votre CV",
        type=["pdf", "txt"],
        key="cv_uploader_app1",
        help="Format accepté : PDF ou TXT"
    )
    if cv_file:
        st.markdown('<span class="status-badge badge-success">✓ CV chargé</span>', unsafe_allow_html=True)

with col2:
    st.markdown("### 💼 Description du poste")
    job_file = st.file_uploader(
        "Uploadez la description du poste",
        type=["pdf", "txt"],
        key="job_uploader_app1",
        help="Format accepté : PDF ou TXT"
    )
    if job_file:
        st.markdown('<span class="status-badge badge-success">✓ Offre chargée</span>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    if st.button("🚀 Lancer l'analyse et générer le plan d'entretien", type="primary", use_container_width=True):
        if not cv_file or not job_file:
            st.warning("⚠️ Merci de fournir **un CV** ET **une description de poste**.")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("📖 Lecture des fichiers...")
            progress_bar.progress(20)
            cv_text = read_uploaded_file(cv_file)
            job_text = read_uploaded_file(job_file)
            
            st.session_state.cv_text = cv_text
            st.session_state.job_text = job_text
            
            status_text.text("🔍 Analyse du profil en cours...")
            progress_bar.progress(40)
            
            try:
                profile = build_profile(cv_text, job_text)
            except Exception as e:
                st.error(f"❌ Erreur lors de l'analyse CV/Offre : {e}")
                st.stop()
            
            st.session_state.profile = profile
            
            status_text.text("📋 Génération du plan d'entretien...")
            progress_bar.progress(70)
            
            interviewer_profile = (
                "Manager technique backend, ton direct mais bienveillant, "
                "s'intéresse aux projets concrets et aux résultats chiffrés."
            )
            
            try:
                plan = generate_interview_plan(
                    profile,
                    interviewer_profile=interviewer_profile,
                    n_questions=8,
                )
            except Exception as e:
                st.error(f"❌ Erreur lors de la génération du plan d'entretien : {e}")
                st.stop()
            
            st.session_state.plan = plan
            st.session_state.current_question_index = 0
            st.session_state.history = []
            st.session_state.transcriptions = {}
            
            progress_bar.progress(100)
            status_text.empty()
            progress_bar.empty()
            
            st.markdown("""
                <div class="success-box">
                    ✅ <strong>Analyse terminée avec succès !</strong><br>
                    Votre profil a été analysé et le plan d'entretien est prêt.
                </div>
            """, unsafe_allow_html=True)

# ---------- Section 2 : Résumé du matching ----------

if st.session_state.profile:
    st.markdown("---")
    st.markdown("## 📊 Étape 2 : Analyse de l'adéquation profil-poste")
    
    profile = st.session_state.profile
    
    # Résumé dans une card
    st.markdown(f"""
        <div class="card">
            <h3 style="margin-top: 0;">💡 Résumé de l'analyse</h3>
            <p style="color: var(--text-secondary); line-height: 1.6;">{profile.get("fit_summary", "Aucun résumé disponible.")}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Compétences en colonnes
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class="card">
                <h3 style="margin-top: 0; color: var(--success-color);">✅ Compétences correspondantes</h3>
        """, unsafe_allow_html=True)
        
        overlap_skills = profile.get("overlap_hard_skills", [])
        if overlap_skills:
            for skill in overlap_skills:
                st.markdown(f'<span class="status-badge badge-success">{skill}</span>', unsafe_allow_html=True)
        else:
            st.markdown("*Aucune compétence commune identifiée*")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="card">
                <h3 style="margin-top: 0; color: var(--warning-color);">📚 Compétences à développer</h3>
        """, unsafe_allow_html=True)
        
        missing_skills = profile.get("missing_hard_skills", [])
        if missing_skills:
            for skill in missing_skills:
                st.markdown(f'<span class="status-badge badge-warning">{skill}</span>', unsafe_allow_html=True)
        else:
            st.markdown("*Aucune compétence manquante identifiée*")
        
        st.markdown("</div>", unsafe_allow_html=True)

# ---------- Section 3 : Simulation d'entretien ----------

if st.session_state.plan:
    st.markdown("---")
    st.markdown("## 🎙️ Étape 3 : Simulation d'entretien")
    
    plan = st.session_state.plan
    idx = st.session_state.current_question_index
    
    # Progress indicator
    progress_percentage = (idx / len(plan)) * 100
    st.progress(progress_percentage / 100)
    st.markdown(f'<div class="question-counter">Question {idx + 1} sur {len(plan)}</div>', unsafe_allow_html=True)
    
    if idx < len(plan):
        current_q = plan[idx]
        
        # Question card
        st.markdown(f"""
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <span class="status-badge badge-info">{current_q.get('type', 'inconnu')}</span>
                    {f'<span class="status-badge badge-info">{current_q.get("topic", "")}</span>' if current_q.get("topic", "") else ''}
                </div>
                <h3 style="margin-top: 0; color: var(--text-primary); font-size: 1.35rem;">
                    {current_q.get("question", "")}
                </h3>
            </div>
        """, unsafe_allow_html=True)
        
        question_text = current_q.get("question", "")
        
        # TTS Button
        col_tts1, col_tts2, col_tts3 = st.columns([1, 2, 1])
        with col_tts2:
            if st.button("🔊 Écouter la question", key=f"tts_{idx}", use_container_width=True):
                try:
                    with st.spinner("Génération audio..."):
                        audio_bytes = question_to_audio(question_text)
                        st.audio(audio_bytes, format="audio/mp3")
                except Exception as e:
                    st.error(f"❌ Erreur TTS : {e}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Zone de réponse audio
        st.markdown("### 🎤 Votre réponse")
        
        col_audio1, col_audio2 = st.columns([2, 1])
        
        with col_audio1:
            audio_file = st.file_uploader(
                "Uploadez votre réponse audio",
                type=["wav", "mp3"],
                key=f"audio_{idx}",
                help="Formats acceptés : WAV, MP3"
            )
        
        with col_audio2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📝 Transcrire", key=f"transcribe_{idx}", disabled=not audio_file, use_container_width=True):
                with st.spinner("Transcription en cours..."):
                    audio_bytes = audio_file.read()
                    ext = "wav"
                    if audio_file.name.lower().endswith(".mp3"):
                        ext = "mp3"
                    try:
                        text = transcribe_audio(audio_bytes, file_ext=ext)
                        st.session_state.transcriptions[idx] = text
                        st.markdown("""
                            <div class="success-box">
                                ✅ Transcription terminée avec succès
                            </div>
                        """, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"❌ Erreur lors de la transcription : {e}")
        
        # Zone de texte pour la réponse
        initial_answer = st.session_state.transcriptions.get(idx, "")
        answer_text = st.text_area(
            "✍️ Votre réponse (éditez si nécessaire)",
            value=initial_answer,
            key=f"answer_text_{idx}",
            height=200,
            help="Vous pouvez corriger ou compléter la transcription automatique"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Boutons d'action
        col_a, col_b, col_c = st.columns([1, 2, 1])
        
        with col_a:
            if st.button("⏭️ Passer", key=f"skip_{idx}", use_container_width=True):
                st.session_state.current_question_index += 1
                st.rerun()
        
        with col_b:
            if st.button("✅ Soumettre ma réponse", key=f"eval_{idx}", type="primary", use_container_width=True):
                if not answer_text.strip():
                    st.warning("⚠️ Merci de saisir une réponse avant de soumettre.")
                else:
                    with st.spinner("Évaluation de votre réponse..."):
                        try:
                            evaluation = evaluate_answer(
                                question=question_text,
                                answer=answer_text,
                                job_text=st.session_state.job_text,
                            )
                        except Exception as e:
                            st.error(f"❌ Erreur lors de l'évaluation : {e}")
                            st.stop()
                        
                        record = {
                            "question": question_text,
                            "type": current_q.get("type", ""),
                            "topic": current_q.get("topic", ""),
                            "answer": answer_text,
                            "evaluation": evaluation,
                        }
                        st.session_state.history.append(record)
                        st.session_state.current_question_index += 1
                        st.rerun()
    
    else:
        st.markdown("""
            <div class="success-box">
                🎉 <strong>Félicitations !</strong><br>
                Vous avez répondu à toutes les questions de l'entretien.
            </div>
        """, unsafe_allow_html=True)

# ---------- Section 4 : Feedback en temps réel ----------

if st.session_state.history:
    st.markdown("---")
    st.markdown("## 📈 Étape 4 : Feedback détaillé sur vos réponses")
    
    for i, record in enumerate(st.session_state.history, start=1):
        with st.expander(f"**Question {i}** : {record['question'][:100]}{'...' if len(record['question']) > 100 else ''}"):
            
            # Réponse
            st.markdown("#### 💬 Votre réponse")
            st.markdown(f"<div class='card'>{record['answer']}</div>", unsafe_allow_html=True)
            
            eval_ = record["evaluation"]
            
            # Scores
            st.markdown("#### 📊 Évaluation")
            
            st.markdown(f"""
                <div class="score-container">
                    <div class="score-item">
                        <div class="score-label">Score global</div>
                        <div class="score-value">{eval_.get('score', '?')}<span style="font-size: 1rem;">/10</span></div>
                    </div>
                    <div class="score-item">
                        <div class="score-label">Clarté</div>
                        <div class="score-value">{eval_.get('clarity', '?')}<span style="font-size: 1rem;">/5</span></div>
                    </div>
                    <div class="score-item">
                        <div class="score-label">Pertinence</div>
                        <div class="score-value">{eval_.get('relevance', '?')}<span style="font-size: 1rem;">/5</span></div>
                    </div>
                    <div class="score-item">
                        <div class="score-label">Alignement</div>
                        <div class="score-value">{eval_.get('alignment', '?')}<span style="font-size: 1rem;">/5</span></div>
                    </div>
                    <div class="score-item">
                        <div class="score-label">Profondeur</div>
                        <div class="score-value">{eval_.get('depth', '?')}<span style="font-size: 1rem;">/5</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Points forts, faibles, améliorations
            col1, col2, col3 = st.columns(3)
            
            with col1:
                strengths = eval_.get("strengths", [])
                if strengths:
                    st.markdown("**✅ Points forts**")
                    for s in strengths:
                        st.markdown(f"- {s}")
            
            with col2:
                weaknesses = eval_.get("weaknesses", [])
                if weaknesses:
                    st.markdown("**⚠️ Points à améliorer**")
                    for w in weaknesses:
                        st.markdown(f"- {w}")
            
            with col3:
                improvements = eval_.get("improvements", [])
                if improvements:
                    st.markdown("**💡 Recommandations**")
                    for imp in improvements:
                        st.markdown(f"- {imp}")

# ---------- Section 5 : Rapport final ----------

if st.session_state.history:
    st.markdown("---")
    st.markdown("## 📋 Étape 5 : Rapport final d'entretien")
    
    col_report1, col_report2, col_report3 = st.columns([1, 2, 1])
    with col_report2:
        if st.button("📄 Générer le rapport complet", type="primary", use_container_width=True):
            with st.spinner("Génération du rapport final en cours..."):
                try:
                    report = generate_final_report(st.session_state.history)
                except Exception as e:
                    st.error(f"❌ Erreur lors de la génération du rapport final : {e}")
                else:
                    st.markdown("""
                        <div class="success-box">
                            ✅ Rapport généré avec succès
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    st.markdown(report)
                    st.markdown("</div>", unsafe_allow_html=True)

# ---------- Footer ----------

st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: var(--text-secondary); padding: 2rem 0;">
        <p>Simulateur d'Entretien RH - Propulsé par l'Intelligence Artificielle</p>
        <p style="font-size: 0.85rem;">Pour toute question ou assistance, contactez votre service RH</p>
    </div>
""", unsafe_allow_html=True)