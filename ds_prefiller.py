"""
Module de pré-remplissage pour Démarches Simplifiées.
Ce module gère la communication avec l'API Démarches Simplifiées
pour générer des URLs vers des dossiers pré-remplis.
"""

import requests
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration API Démarches Simplifiées
DEFAULT_DEMARCHE_ID = '111570'  # ID de démarche par défaut
API_TOKEN = os.getenv("API_TOKEN_BILAN_DRAC_DRAAF")  # Token API

# Mapper les champs du formulaire aux IDs DS
FIELD_MAPPING = {
    "Titre_du_projet": "Q2hhbXAtNjIyMzQw",
    "Numero_dossier": "Q2hhbXAtNjA3OTQ3",
    "Montant_DRAC": "Q2hhbXAtNDA3NDExMQ",
    "Montant_DRAAF": "Q2hhbXAtNDA3NDExMg",
    "Nom": "Q2hhbXAtNjA3OTcy",
    "Email": "Q2hhbXAtNjA3OTc1"
}

def map_data(data_dict):
    """
    Mappe les données du dictionnaire d'entrée aux IDs DS.
    
    Args:
        data_dict (dict): Dictionnaire des données à mapper
        
    Returns:
        dict: Dictionnaire mappé pour l'API DS
    """
    mapped_data = {}
    
    for key, value in data_dict.items():
        if key in FIELD_MAPPING:
            mapped_data[f"champ_{FIELD_MAPPING[key]}"] = str(value)
    
    return mapped_data

def generate_prefilled_url(data_dict, demarche_id=DEFAULT_DEMARCHE_ID):
    """
    Génère une URL vers un dossier pré-rempli sur Démarches Simplifiées.
    
    Args:
        data_dict (dict): Dictionnaire des données du formulaire
        demarche_id (str): ID de la démarche DS (optionnel)
        
    Returns:
        tuple: (success, result) où result est l'URL ou un message d'erreur
    """
    # Vérifier la présence du token API
    if not API_TOKEN:
        return False, "Token API non trouvé. Vérifiez votre fichier .env"
    
    # Préparer les données
    api_url = f'https://www.demarches-simplifiees.fr/api/public/v1/demarches/{demarche_id}/dossiers'
    headers = {
        "Content-Type": "application/json", 
        "Authorization": f"Bearer {API_TOKEN}"
    }
    
    # Mapper les données
    mapped_data = map_data(data_dict)
    
    try:
        # Envoyer la requête à l'API
        response = requests.post(api_url, headers=headers, json=mapped_data)
        
        if response.status_code == 201:
            return True, response.json().get("dossier_url", "")
        else:
            return False, f"Erreur API DS: {response.text}"
    except Exception as e:
        return False, f"Exception: {str(e)}"

def test_api_connection(demarche_id=DEFAULT_DEMARCHE_ID):
    """
    Teste la connexion à l'API avec des données factices.
    
    Args:
        demarche_id (str): ID de la démarche DS (optionnel)
    
    Returns:
        tuple: (success, result) où result est l'URL ou un message d'erreur
    """
    # Données de test
    test_data = {
        "Nom": "Test Utilisateur",
        "Email": "test@example.com",
        "Titre_du_projet": "Projet Test API",
        "Numero_dossier": "TEST123",
        "Montant_DRAC": "1000",
        "Montant_DRAAF": "500"
    }
    
    return generate_prefilled_url(test_data, demarche_id)

# Code pour tester le module si exécuté directement
if __name__ == "__main__":
    success, result = test_api_connection()
    
    if success:
        print(f"Test réussi ! URL générée : {result}")
    else:
        print(f"Échec du test : {result}")