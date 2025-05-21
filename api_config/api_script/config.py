# api/config.py
import os
from dotenv import load_dotenv

load_dotenv()

BLUESKY_HANDLE = os.getenv("BLUESKY_HANDLE")
APP_PASSWORD = os.getenv("APP_PASSWORD")
DATABASE_URL = os.getenv("DATABASE_URL")

if not all([BLUESKY_HANDLE, APP_PASSWORD, DATABASE_URL]):
    raise ValueError("Veuillez vérifier que toutes les variables d'environnement sont définies.")


"""import os
from atproto import Client
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Récupérer les identifiants depuis les variables d'environnement
BLUESKY_HANDLE = os.getenv("BLUESKY_HANDLE")
APP_PASSWORD = os.getenv("APP_PASSWORD")

def get_authenticated_client():
    #Authentifie l'utilisateur auprès de l'API de Bluesky et retourne un client authentifié.
    if not BLUESKY_HANDLE or not APP_PASSWORD:
        raise ValueError("Les variables d'environnement BLUESKY_HANDLE et APP_PASSWORD doivent être définies.")

    client = Client()
    client.login(BLUESKY_HANDLE, APP_PASSWORD)
    return client

if __name__ == "__main__":
    try:
        client = get_authenticated_client()
       # print("✅ Connexion réussie à l'API de Bluesky.")
        # Exemple : récupérer et afficher les 5 derniers posts du fil d'actualité
        timeline = client.get_timeline(limit=5)
        for idx, post in enumerate(timeline.feed, start=1):
            print(f"\nPost {idx}:")
            print(f"Auteur : {post.post.author.handle}")
            print(f"Contenu : {post.post.record.text}")
    except Exception as e:
        print("❌ Échec de la connexion à l'API de Bluesky.")
        print(f"Erreur : {e}")"""

##### last version en bas ####
# api/config.py

"""import os
from atproto import Client
from dotenv import load_dotenv

load_dotenv()

BLUESKY_HANDLE = os.getenv("BLUESKY_HANDLE")
APP_PASSWORD = os.getenv("APP_PASSWORD")

def get_authenticated_client():
    if not BLUESKY_HANDLE or not APP_PASSWORD:
        raise ValueError("Les variables d'environnement BLUESKY_HANDLE et APP_PASSWORD doivent être définies.")

    client = Client()
    client.login(BLUESKY_HANDLE, APP_PASSWORD)
    return client"""
    

