"""
Module d'intégration avec Grist pour Démarches Simplifiées.
Ce module gère la communication avec l'API Grist pour récupérer
les données des tables Grist.
"""

import os
import requests
import pandas as pd
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration API Grist
GRIST_API_KEY = os.getenv("GRIST_API_KEY")
GRIST_DOC_ID = os.getenv("GRIST_DOC_ID")
GRIST_BASE_URL = os.getenv("GRIST_BASE_URL", "https://grist.numerique.gouv.fr/api")
GRIST_PROJETS_TABLE = os.getenv("GRIST_PROJETS_TABLE", "Demarche_87698_dossiers")
GRIST_ANNOTATIONS_TABLE = os.getenv("GRIST_ANNOTATIONS_TABLE", "Demarche_87698_annotations")

# Noms des colonnes adaptés à la structure de données Grist
# Ces noms devront être adaptés selon la structure réelle de vos tables
COL_NOM = "A_nom"
COL_EMAIL = "usager_email"
COL_TITRE_PROJET = "A_titre_du_projet"
COL_NUMERO_DOSSIER = "number"
COL_MONTANT_DRAC = "montant_drac"
COL_MONTANT_DRAAF = "montant_draaf"


class GristClient:
    def __init__(self, base_url, api_key, doc_id=None):
        """
        Initialise un client pour l'API Grist.
        
        Args:
            base_url: URL de base de l'API Grist (ex: https://grist.numerique.gouv.fr/api)
            api_key: Clé API pour l'authentification
            doc_id: ID du document Grist (optionnel)
        """
        self.base_url = base_url.rstrip('/')  # Enlever le / final s'il y en a un
        self.api_key = api_key
        self.doc_id = doc_id
        self.headers = {
            "Authorization": f"Bearer {api_key}"
        }

    def set_doc_id(self, doc_id):
        """
        Définit l'ID du document Grist pour les opérations futures.
        """
        self.doc_id = doc_id

    def list_documents(self):
        """
        Liste tous les documents accessibles.
        
        Returns:
            list: Liste des documents
        """
        url = f"{self.base_url}/docs"
        try:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                raise Exception(f"Erreur {response.status_code}: {response.text}")
            
            # Vérification du format de la réponse
            data = response.json()
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'docs' in data:
                return data['docs']
            else:
                return [data]  # Cas où un seul document est retourné
                
        except Exception as e:
            print(f"Erreur lors de la récupération des documents: {str(e)}")
            return []

    def get_document_info(self):
        """
        Récupère les informations sur le document courant.
        
        Returns:
            dict: Informations sur le document
        """
        if not self.doc_id:
            raise ValueError("L'ID du document est requis")
        
        url = f"{self.base_url}/docs/{self.doc_id}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            raise Exception(f"Erreur {response.status_code}: {response.text}")
        
        return response.json()
    
    def list_tables(self):
        """
        Liste toutes les tables du document courant.
        
        Returns:
            list: Liste des tables
        """
        if not self.doc_id:
            raise ValueError("L'ID du document est requis")

        url = f"{self.base_url}/docs/{self.doc_id}/tables"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            raise Exception(f"Erreur {response.status_code}: {response.text}")
        
        data = response.json()
        
        # Normalisation des données retournées
        if isinstance(data, dict) and 'tables' in data:
            return data['tables']
        elif isinstance(data, list):
            return data
        else:
            raise Exception(f"Format de données inattendu: {data}")

    def get_table_data(self, table_id):
        """
        Récupère toutes les données d'une table.
        
        Args:
            table_id: ID de la table Grist
            
        Returns:
            DataFrame: Données de la table sous forme de DataFrame pandas
        """
        if not self.doc_id:
            raise ValueError("L'ID du document est requis")

        url = f"{self.base_url}/docs/{self.doc_id}/tables/{table_id}/records"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            raise Exception(f"Erreur {response.status_code}: {response.text}")
        
        data = response.json()
        
        if 'records' not in data:
            raise Exception(f"Format de données inattendu: {data}")
        
        # Extraire les champs et l'ID de chaque enregistrement
        rows = []
        for record in data['records']:
            if 'fields' in record:
                # Copier les champs et ajouter l'ID
                row_data = record['fields'].copy()
                row_data['id'] = record.get('id')
                rows.append(row_data)
        
        # Créer un DataFrame pandas
        df = pd.DataFrame(rows)
        
        return df

    def get_table_columns(self, table_id):
        """
        Récupère les informations sur les colonnes d'une table.
        
        Args:
            table_id: ID de la table Grist
            
        Returns:
            list: Informations sur les colonnes
        """
        if not self.doc_id:
            raise ValueError("L'ID du document est requis")

        url = f"{self.base_url}/docs/{self.doc_id}/tables/{table_id}/columns"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            raise Exception(f"Erreur {response.status_code}: {response.text}")
        
        data = response.json()
        
        if 'columns' not in data:
            raise Exception(f"Format de données inattendu: {data}")
        
        return data['columns']


# Fonctions d'interface pour notre application
def get_grist_client():
    """
    Crée et configure un client Grist avec les paramètres de l'environnement.
    
    Returns:
        GristClient: Client Grist configuré
    """
    return GristClient(GRIST_BASE_URL, GRIST_API_KEY, GRIST_DOC_ID)


def get_table_structure(table_id):
    """
    Affiche la structure d'une table pour faciliter le débogage.
    
    Args:
        table_id: ID de la table à analyser
    """
    try:
        client = get_grist_client()
        df = client.get_table_data(table_id)
        
        if df.empty:
            print(f"La table {table_id} est vide")
            return
        
        print(f"\nStructure de la table {table_id}:")
        print(f"Nombre d'enregistrements: {len(df)}")
        print(f"Colonnes: {df.columns.tolist()}")
        
        # Afficher un exemple de données
        if len(df) > 0:
            print("\nExemple de données (premier enregistrement):")
            for col in df.columns:
                value = df.iloc[0][col]
                print(f"  {col}: {value}")
    
    except Exception as e:
        print(f"Erreur lors de l'analyse de la table {table_id}: {str(e)}")


def rechercher_dossier_par_email(email):
    """
    Recherche un dossier dans la table des dossiers qui correspond à l'email.
    
    Args:
        email (str): Adresse email du dossier
    
    Returns:
        tuple: (success, result) où result est les données du dossier ou un message d'erreur
    """
    try:
        print(f"Recherche de dossier avec email: {email}")
        client = get_grist_client()
        
        # Récupérer les données de la table des dossiers
        df_dossiers = client.get_table_data(GRIST_PROJETS_TABLE)
        
        # Vérifier les colonnes disponibles pour le débogage
        print(f"Colonnes disponibles: {df_dossiers.columns.tolist()}")
        
        # Vérifier que la colonne email existe
        if COL_EMAIL not in df_dossiers.columns:
            print(f"⚠️ La colonne {COL_EMAIL} n'existe pas dans la table des dossiers")
            return False, f"La colonne {COL_EMAIL} n'existe pas dans la table des dossiers"
        
        # Filtrer par email
        dossiers_filtres = df_dossiers[df_dossiers[COL_EMAIL] == email]
        
        if len(dossiers_filtres) == 0:
            print("Aucun dossier trouvé avec cet email.")
            return False, "Aucun dossier trouvé avec cet email."
        
        # Prendre le premier dossier correspondant
        dossier = dossiers_filtres.iloc[0].to_dict()
        
        # Formater le résultat
        result = {
            "id": dossier.get("id"),
            "fields": {k: v for k, v in dossier.items() if k != "id"}
        }
        
        print(f"Dossier trouvé avec ID: {result['id']}")
        return True, result
    
    except Exception as e:
        print(f"Exception lors de la recherche du dossier: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, f"Exception: {str(e)}"


def rechercher_annotations_par_id_dossier(dossier_id):
    """
    Recherche les annotations associées à un dossier dans la table des annotations.
    
    Args:
        dossier_id (int): ID du dossier
    
    Returns:
        tuple: (success, result) où result est les données des annotations ou un message d'erreur
    """
    try:
        print(f"Recherche d'annotations pour le dossier ID: {dossier_id}")
        client = get_grist_client()
        
        # Récupérer les données de la table annotations
        df_annotations = client.get_table_data(GRIST_ANNOTATIONS_TABLE)
        
        # Vérifier qu'il y a des données
        if df_annotations.empty:
            print("Table des annotations vide")
            return False, "Aucune donnée dans la table des annotations"
        
        # Vérifier les colonnes de la table
        print(f"Colonnes dans la table des annotations: {df_annotations.columns.tolist()}")
        
        # Rechercher la colonne qui pourrait contenir la référence au dossier
        # Essayer plusieurs noms possibles
        dossier_id_columns = ["dossier_id", "projet_id", "id_dossier", "parentId"]
        
        found_column = None
        for col in dossier_id_columns:
            if col in df_annotations.columns:
                found_column = col
                print(f"Utilisation de la colonne {col} pour lier aux dossiers")
                break
        
        if not found_column:
            print("⚠️ Impossible de trouver la colonne de liaison au dossier")
            possible_columns = [col for col in df_annotations.columns if "id" in col.lower()]
            print(f"Colonnes potentielles: {possible_columns}")
            
            # Si aucune colonne évidente n'est trouvée, essayer de deviner basé sur les valeurs
            if len(df_annotations) > 0 and dossier_id is not None:
                for col in df_annotations.columns:
                    if df_annotations[col].eq(dossier_id).any():
                        found_column = col
                        print(f"Trouvé correspondance potentielle dans la colonne {col}")
                        break
            
            if not found_column:
                return False, "Impossible de déterminer la colonne de référence au dossier"
        
        # Filtrer les annotations par ID de dossier
        annotations = df_annotations[df_annotations[found_column] == dossier_id]
        
        if len(annotations) == 0:
            print(f"Aucune annotation trouvée pour le dossier ID {dossier_id}")
            return False, "Aucune annotation trouvée pour ce dossier"
        
        # Convertir la première ligne en dictionnaire
        annotation_dict = annotations.iloc[0].to_dict()
        
        # Vérifier si les colonnes des montants existent
        has_montant_drac = COL_MONTANT_DRAC in annotation_dict
        has_montant_draaf = COL_MONTANT_DRAAF in annotation_dict
        
        if not has_montant_drac:
            print(f"⚠️ Colonne {COL_MONTANT_DRAC} non trouvée dans les annotations")
        if not has_montant_draaf:
            print(f"⚠️ Colonne {COL_MONTANT_DRAAF} non trouvée dans les annotations")
        
        # Formater le résultat
        result = {
            "id": annotation_dict.get("id"),
            "fields": {k: v for k, v in annotation_dict.items() if k != "id"}
        }
        
        print(f"Annotation trouvée avec ID: {result['id']}")
        return True, result
    
    except Exception as e:
        print(f"Exception lors de la recherche des annotations: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, f"Exception: {str(e)}"


def valider_email_et_recuperer_donnees(email):
    """
    Vérifie si l'email existe dans les tables Grist
    et récupère les données associées, y compris le N_dossier.
    
    Args:
        email (str): Adresse email associée au dossier
    
    Returns:
        tuple: (success, result) où result est un dictionnaire de données combinées ou un message d'erreur
    """
    print(f"Validation de l'email: {email}")
    
    # Rechercher le dossier
    success_dossier, result_dossier = rechercher_dossier_par_email(email)
    if not success_dossier:
        return False, result_dossier
    
    # Récupérer l'ID du dossier
    dossier_id = result_dossier.get("id")
    
    # Par défaut, définir des montants à 0
    montant_drac = "0"
    montant_draaf = "0"
    
    # Rechercher les annotations associées au dossier
    success_annotations, result_annotations = rechercher_annotations_par_id_dossier(dossier_id)
    
    # Si des annotations sont trouvées, récupérer les montants
    if success_annotations:
        montant_drac = str(result_annotations.get("fields", {}).get(COL_MONTANT_DRAC, "0"))
        montant_draaf = str(result_annotations.get("fields", {}).get(COL_MONTANT_DRAAF, "0"))
        print(f"Montants trouvés - DRAC: {montant_drac}, DRAAF: {montant_draaf}")
    else:
        print("Aucune annotation trouvée avec les montants")
    
    # Extraire les champs du dossier
    dossier_fields = result_dossier.get("fields", {})

    # Récupérer le numéro de dossier depuis N_dossier (ou number si N_dossier n'existe pas)
    numero_dossier = dossier_fields.get("N_dossier", dossier_fields.get(COL_NUMERO_DOSSIER, ""))
    
    # Combiner les données
    combined_data = {
        "Nom": dossier_fields.get(COL_NOM, ""),
        "Email": email,
        "Titre_du_projet": dossier_fields.get(COL_TITRE_PROJET, ""),
        "Numero_dossier": numero_dossier,
        "Montant_DRAC": montant_drac,
        "Montant_DRAAF": montant_draaf
    }
    
    print(f"Données combinées prêtes: {combined_data}")
    
    return True, combined_data


def test_grist_connection():
    """
    Teste la connexion à l'API Grist et affiche la structure des tables.
    
    Returns:
        tuple: (success, result) où result est un message de succès ou d'erreur
    """
    try:
        client = get_grist_client()
        
        # Afficher les informations de connexion
        print(f"URL de base: {client.base_url}")
        print(f"ID du document: {client.doc_id}")
        
        # Tester la liste des tables
        tables = client.list_tables()
        table_names = [table.get('id') for table in tables]
        
        return True, f"Connexion réussie à Grist. Tables disponibles: {', '.join(table_names)}"
    
    except Exception as e:
        return False, f"Exception: {str(e)}"


# Code pour tester le module si exécuté directement
if __name__ == "__main__":
    # Tester la connexion à l'API Grist
    print("\n=== Test de connexion à Grist ===")
    success, result = test_grist_connection()
    print(f"Résultat: {'Succès' if success else 'Échec'} - {result}")
    
    if success:
        # Analyser la structure des tables
        print("\n=== Analyse de la structure des tables ===")
        get_table_structure(GRIST_PROJETS_TABLE)
        get_table_structure(GRIST_ANNOTATIONS_TABLE)
        
        