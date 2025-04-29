"""
Simulateur Démarches Simplifiées avec Streamlit.
Cette application permet de générer des liens vers des dossiers pré-remplis
sur Démarches Simplifiées à partir de données Grist.
"""

import streamlit as st
import os
from dotenv import load_dotenv
import ds_prefiller
import grist_connector
import re

# Charger les variables d'environnement
load_dotenv()

# Configuration
demarche_id = os.getenv("DEMARCHE_ID", "111570")

# CSS pour le style conforme au design système de l'État
def load_css():
    st.markdown("""
    <style>
    /* Style général conforme au DSFR */
    .main {
        background-color: #ffffff;
        color: #1e1e1e;
        font-family: Marianne, arial, sans-serif;
    }
    h1, h2, h3 {
        color: #000091;
    }
    .stButton button {
        background-color: #000091;
        color: white;
        border-radius: 4px;
        border: none;
        padding: 8px 16px;
    }
    .stButton button:hover {
        background-color: #1212ff;
    }
    
    /* Style pour les messages de succès */
    .success-message {
        background-color: #e8f5e9;
        color: #1b5e20;
        padding: 15px;
        border-radius: 4px;
        margin: 15px 0;
        text-align: center;
    }
    
    /* Style pour la sidebar */
    section[data-testid="stSidebar"] {
        background-color: #f2f2ff;
    }
    
    /* Style pour l'alerte */
    .custom-alert {
        background-color: #fff4e5;
        color: #b95000;
        padding: 15px;
        border-radius: 4px;
        margin: 15px 0;
        border-left: 4px solid #b95000;
    }
    
    /* Style pour l'info */
    .info-box {
        background-color: #e3f2fd;
        color: #0d47a1;
        padding: 15px;
        border-radius: 4px;
        margin: 15px 0;
        border-left: 4px solid #0d47a1;
    }
    
    /* Style pour le bouton de lien */
    .link-button {
        background-color: #000091;
        color: white !important;
        text-decoration: none;
        padding: 10px 24px;
        border-radius: 4px;
        font-size: 16px;
        display: inline-block;
        border: none;
        cursor: pointer;
        text-align: center;
        margin-bottom: 16px; 
    }
    
    .link-button:hover {
        background-color: #1212ff;
    }
    
    /* Style pour le conteneur de résultat */
    .result-container {
        background-color: #f7f7f7;
        padding: 15px;
        border-radius: 4px;
        margin-top: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# Validation de l'email
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def main():
    # Configuration de la page
    st.set_page_config(
        page_title="Création dossier bilan Drac Draaf",
        page_icon="🦥",  # Icône de la page 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Appliquer le style
    load_css()
    
    # Initialisation des variables de session
    if 'generate_success' not in st.session_state:
        st.session_state.generate_success = False
    if 'dossier_url' not in st.session_state:
        st.session_state.dossier_url = ""
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {}
    if 'grist_data_loaded' not in st.session_state:
        st.session_state.grist_data_loaded = False
    
    # Sidebar (bandeau latéral)
    st.sidebar.title("Statut du dossier")
    
    # Section principale
    st.title("🦥 Création dossier bilan Drac Draaf")
    st.subheader("Recherche par email")
    

    # Formulaire de recherche - uniquement l'email maintenant
    email_recherche = st.text_input("Email", help="Adresse email associée au dossier", key="email_recherche")
    
    # Bouton de recherche
    if st.button("Récupérer les données vous concernant", key="btn_recherche"):
        if not email_recherche:
            st.markdown("""
            <div class="custom-alert">
                <strong>⚠️ Veuillez saisir une adresse email pour effectuer la recherche</strong>
            </div>
            """, unsafe_allow_html=True)
        elif not is_valid_email(email_recherche):
            st.markdown("""
            <div class="custom-alert">
                <strong>⚠️ Format d'email invalide</strong>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Effectuer la recherche
            with st.spinner("Recherche en cours..."):
                success, result = grist_connector.valider_email_et_recuperer_donnees(email_recherche)
            
            if success:
                # Stocker les données récupérées
                st.session_state.form_data = result
                st.session_state.grist_data_loaded = True
                
                # Afficher un message de succès
                st.markdown("""
                <div class="success-message">
                    <span>✓ Données récupérées avec succès!</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Afficher les données trouvées
                st.markdown("""
                <div class="info-box">
                    <strong>Données récupérées</strong><br/>
                    Les champs du formulaire ont été remplis automatiquement.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="custom-alert">
                    <strong>⚠️ Erreur lors de la recherche: {result}</strong>
                </div>
                """, unsafe_allow_html=True)
    
    # Si des données ont été chargées, afficher un récapitulatif
    if st.session_state.grist_data_loaded:
        st.markdown("### Récapitulatif des données")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Nom:** {st.session_state.form_data.get('Nom', '')}")
            st.markdown(f"**Email:** {st.session_state.form_data.get('Email', '')}")
            st.markdown(f"**Numéro de dossier:** {st.session_state.form_data.get('Numero_dossier', '')}")
        
        with col2:
            st.markdown(f"**Titre du projet:** {st.session_state.form_data.get('Titre_du_projet', '')}")
            st.markdown(f"**Montant DRAC:** {st.session_state.form_data.get('Montant_DRAC', '0')} €")
            st.markdown(f"**Montant DRAAF:** {st.session_state.form_data.get('Montant_DRAAF', '0')} €")
    
    # Zone de résultat
    st.subheader("Résultat")
    afficher_resultat()
    
    # Mise à jour des informations dans la sidebar
    update_sidebar()

def afficher_resultat():
    # Vérifier les champs obligatoires
    champs_manquants = verifier_champs_obligatoires()
    bouton_disabled = len(champs_manquants) > 0 and not st.session_state.generate_success
    
    # Interface de résultat améliorée
    if st.session_state.generate_success:
        # Afficher le message de succès
        st.markdown("""
        <div class="success-message">
            <span>✓ Traitement terminé avec succès!</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Bouton d'accès au dossier - lien direct
        st.markdown(f"""
        <a href="{st.session_state.dossier_url}" target="_blank" class="link-button">
            Accéder au dossier pré-rempli
        </a>
        """, unsafe_allow_html=True)
        
        # Message informatif juste après le premier bouton
        st.markdown("""
        <div class="result-container">
            <p>Votre dossier a été pré-rempli. Cliquez sur le bouton pour y accéder.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Bouton pour générer un nouveau lien - séparé et placé en dernier
        if st.button("Générer un nouveau lien", key="new_link"):
            st.session_state.generate_success = False
            st.session_state.dossier_url = ""
            st.rerun()
        
    else:
        # Afficher l'alerte si des champs sont manquants
        if champs_manquants:
            champs_texte = ", ".join(champs_manquants)
            st.markdown(f"""
            <div class="custom-alert">
                    <strong>⚠️ Veuillez renseigner votre email de connexion à Démarches Simplifiées. </strong><br/>
                
            </div>
            """, unsafe_allow_html=True)
        
        # Bouton pour générer le lien
        if st.button("Générer le dossier bilan Drac Draaf", disabled=bouton_disabled):
            # Préparer les données du formulaire
            form_data = st.session_state.form_data
            
            # Appeler le module de pré-remplissage
            with st.spinner("Génération du lien en cours..."):
                success, result = ds_prefiller.generate_prefilled_url(
                    form_data, 
                    demarche_id=demarche_id
                )
            
            # Enregistrer le résultat dans les variables de session
            if success:
                st.session_state.generate_success = True
                st.session_state.dossier_url = result
                st.rerun()
            else:
                st.error(f"❌ Erreur: {result}")

def verifier_champs_obligatoires():
    form_data = st.session_state.form_data
    champs_manquants = []
    
    # Le champ Nom n'est pas obligatoire
    
    email = form_data.get("Email", "")
    if not email:
        champs_manquants.append("Email")
    elif not is_valid_email(email):
        champs_manquants.append("Email (format invalide)")
    
    if not form_data.get("Titre_du_projet", ""):
        champs_manquants.append("Titre du projet")
    
    if not form_data.get("Numero_dossier", ""):
        champs_manquants.append("Numéro de dossier")
    
    montant_drac = int(form_data.get("Montant_DRAC", 0))
    if montant_drac <= 0:
        champs_manquants.append("Montant DRAC")
    
    montant_draaf = int(form_data.get("Montant_DRAAF", 0))
    if montant_draaf <= 0:
        champs_manquants.append("Montant DRAAF")
    
    return champs_manquants

def update_sidebar():
    form_data = st.session_state.form_data

    # Afficher le numéro de dossier en premier et en évidence
    numero_dossier = form_data.get("Numero_dossier", "")
    if numero_dossier:
        st.sidebar.markdown(f"""
        <div style="margin-bottom:20px; padding:15px; background-color:#f5f5fe; border-left:4px solid #000091; border-radius:4px;">
            <strong style="font-size:18px;">Numéro de dossier</strong><br/>
            <span style="font-size:24px; color:#000091; font-weight:bold;">{numero_dossier}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown("""
        <div style="margin-bottom:20px; padding:15px; background-color:#f5f5fe; border-left:4px solid #e0e0e0; border-radius:4px;">
            <strong style="font-size:18px;">Numéro de dossier</strong><br/>
            <span style="font-size:18px; color:#666;">Non disponible</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Vérification du nom (affiché mais pas obligatoire)
    if form_data.get("Nom", ""):
        st.sidebar.markdown("""
        <div style="margin-bottom:15px;">
            <span style="display:inline-block; width:20px; height:20px; background-color:#18753c; color:white; border-radius:50%; text-align:center; line-height:20px; margin-right:10px;">✓</span>
            <strong>Nom</strong><br/>
            <span style="margin-left:30px;">Renseigné</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown("""
        <div style="margin-bottom:15px;">
            <span style="display:inline-block; width:20px; height:20px; background-color:#e0e0e0; color:#666; border-radius:50%; text-align:center; line-height:20px; margin-right:10px;">○</span>
            <strong>Nom</strong><br/>
            <span style="margin-left:30px;">Non renseigné</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Vérification de l'email
    email = form_data.get("Email", "")
    if email:
        if is_valid_email(email):
            st.sidebar.markdown("""
            <div style="margin-bottom:15px;">
                <span style="display:inline-block; width:20px; height:20px; background-color:#18753c; color:white; border-radius:50%; text-align:center; line-height:20px; margin-right:10px;">✓</span>
                <strong>Email</strong><br/>
                <span style="margin-left:30px;">Valide</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.sidebar.markdown("""
            <div style="margin-bottom:15px;">
                <span style="display:inline-block; width:20px; height:20px; background-color:#e1000f; color:white; border-radius:50%; text-align:center; line-height:20px; margin-right:10px;">✗</span>
                <strong>Email</strong><br/>
                <span style="margin-left:30px;">Format invalide</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown("""
        <div style="margin-bottom:15px;">
            <span style="display:inline-block; width:20px; height:20px; background-color:#e0e0e0; color:#666; border-radius:50%; text-align:center; line-height:20px; margin-right:10px;">○</span>
            <strong>Email</strong><br/>
            <span style="margin-left:30px;">Non renseigné</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Vérification du titre du projet
    if form_data.get("Titre_du_projet", ""):
        st.sidebar.markdown("""
        <div style="margin-bottom:15px;">
            <span style="display:inline-block; width:20px; height:20px; background-color:#18753c; color:white; border-radius:50%; text-align:center; line-height:20px; margin-right:10px;">✓</span>
            <strong>Titre du projet</strong><br/>
            <span style="margin-left:30px;">Renseigné</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown("""
        <div style="margin-bottom:15px;">
            <span style="display:inline-block; width:20px; height:20px; background-color:#e0e0e0; color:#666; border-radius:50%; text-align:center; line-height:20px; margin-right:10px;">○</span>
            <strong>Titre du projet</strong><br/>
            <span style="margin-left:30px;">Non renseigné</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Vérification du montant DRAC
    montant_drac = int(form_data.get("Montant_DRAC", 0))
    if montant_drac > 0:
        st.sidebar.markdown(f"""
        <div style="margin-bottom:15px;">
            <span style="display:inline-block; width:20px; height:20px; background-color:#18753c; color:white; border-radius:50%; text-align:center; line-height:20px; margin-right:10px;">✓</span>
            <strong>Montant DRAC</strong><br/>
            <span style="margin-left:30px;">{montant_drac} €</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown("""
        <div style="margin-bottom:15px;">
            <span style="display:inline-block; width:20px; height:20px; background-color:#e0e0e0; color:#666; border-radius:50%; text-align:center; line-height:20px; margin-right:10px;">○</span>
            <strong>Montant DRAC</strong><br/>
            <span style="margin-left:30px;">Non renseigné</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Vérification du montant DRAAF
    montant_draaf = int(form_data.get("Montant_DRAAF", 0))
    if montant_draaf > 0:
        st.sidebar.markdown(f"""
        <div style="margin-bottom:15px;">
            <span style="display:inline-block; width:20px; height:20px; background-color:#18753c; color:white; border-radius:50%; text-align:center; line-height:20px; margin-right:10px;">✓</span>
            <strong>Montant DRAAF</strong><br/>
            <span style="margin-left:30px;">{montant_draaf} €</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown("""
        <div style="margin-bottom:15px;">
            <span style="display:inline-block; width:20px; height:20px; background-color:#e0e0e0; color:#666; border-radius:50%; text-align:center; line-height:20px; margin-right:10px;">○</span>
            <strong>Montant DRAAF</strong><br/>
            <span style="margin-left:30px;">Non renseigné</span>
        </div>
        """, unsafe_allow_html=True)
        
    # Vérification du numéro de dossier
    if form_data.get("Numero_dossier", ""):
        st.sidebar.markdown(f"""
        <div style="margin-bottom:15px;">
            <span style="display:inline-block; width:20px; height:20px; background-color:#18753c; color:white; border-radius:50%; text-align:center; line-height:20px; margin-right:10px;">✓</span>
            <strong>Numéro de dossier</strong><br/>
            <span style="margin-left:30px;">Renseigné</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown("""
        <div style="margin-bottom:15px;">
            <span style="display:inline-block; width:20px; height:20px; background-color:#e0e0e0; color:#666; border-radius:50%; text-align:center; line-height:20px; margin-right:10px;">○</span>
            <strong>Numéro de dossier</strong><br/>
            <span style="margin-left:30px;">Non renseigné</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Afficher source des données si chargées depuis Grist
    if st.session_state.grist_data_loaded:
        st.sidebar.markdown("""
        <div style="margin-top:30px; background-color:#e3f2fd; padding:10px; border-radius:4px;">
            <strong>🔄 Données chargées</strong>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
