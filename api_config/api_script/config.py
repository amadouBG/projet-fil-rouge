# api_config/api_script/config.py
import os
from dotenv import load_dotenv

# --- MODIFICATION ---
# Chercher le fichier .env à la racine du projet (deux niveaux au-dessus)
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env') # <--- CORRIGÉ ICI ('..' ajouté)
loaded = load_dotenv(dotenv_path=dotenv_path)

# Optionnel: Afficher pour vérifier que le .env est bien trouvé
print(f"--- [DEBUG] config.py: Chemin .env = {dotenv_path}, Chargé = {loaded}")
# --- FIN MODIFICATION ---

BLUESKY_HANDLE = os.getenv("BLUESKY_HANDLE")
APP_PASSWORD = os.getenv("APP_PASSWORD")
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")

# Optionnel: Afficher pour vérifier que les variables sont lues
print(f"--- [DEBUG] config.py: DATABASE_URL = {DATABASE_URL}")

# Vérification
if not all([BLUESKY_HANDLE, APP_PASSWORD, DATABASE_URL, SECRET_KEY]):
    # Note: Ajout de SECRET_KEY à la vérification car Flask en a besoin.
    raise ValueError("Veuillez vérifier que BLUESKY_HANDLE, APP_PASSWORD, DATABASE_URL et SECRET_KEY sont définis dans .env.")

# --- SUPPRIMEZ TOUT LE CODE COMMENTÉ QUI SUIVAIT ---
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
    

