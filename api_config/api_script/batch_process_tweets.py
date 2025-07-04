# api_config/api_script/batch_process_tweets.py

import sys
import os
from sqlalchemy.orm import joinedload

# --- Configuration du chemin pour les imports ---
# Ajoute le dossier racine du projet au path Python pour que les imports fonctionnent
# C'est nécessaire car ce script sera exécuté de manière autonome.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(PROJECT_ROOT)
# --- Fin de la configuration du chemin ---

# Imports depuis votre projet
from api_config.api_script.models import SessionLocal, Tweet, Detection
from api_config.api_script.post_from_url import predict_text_veracity, MODEL_NAME

def process_unclassified_tweets():
    """
    Script principal pour trouver les tweets non analysés,
    appliquer le modèle de détection et sauvegarder les résultats.
    """
    print("--- Lancement du traitement par lot des tweets non classifiés ---")
    db_session = SessionLocal()

    try:
        # 1. Requête pour trouver les tweets qui n'ont pas de détection associée.
        # On utilise un LEFT JOIN (outerjoin) entre Tweet et Detection.
        # Si la détection est NULL (Detection.id == None), cela signifie que le tweet
        # n'a pas encore été analysé.
        tweets_to_process = db_session.query(Tweet).outerjoin(Tweet.detections).filter(Detection.id == None).all()

        if not tweets_to_process:
            print("Aucun tweet à traiter. Tous les tweets ont déjà une détection.")
            return

        print(f"Trouvé {len(tweets_to_process)} tweet(s) à analyser.")
        
        detections_created = 0
        for i, tweet in enumerate(tweets_to_process):
            # On vérifie que le tweet a bien du contenu textuel
            if not tweet.content or not tweet.content.strip():
                print(f"  ({i+1}/{len(tweets_to_process)}) Tweet ID {tweet.id} ignoré (contenu vide).")
                continue

            print(f"  ({i+1}/{len(tweets_to_process)}) Analyse du Tweet ID: {tweet.id}...")

            # 2. On appelle la fonction de prédiction (réutilisée depuis post_from_url.py)
            label, probability, threshold = predict_text_veracity(tweet.content)
            print(f"    -> Résultat : {label} (Prob: {probability:.4f})")

            # 3. On crée le nouvel objet Detection
            new_detection = Detection(
                tweet_id=tweet.id,
                label=label,
                probability=probability,
                model_used=MODEL_NAME,
                threshold=threshold,
                verified=False,
            )
            
            # 4. On l'ajoute à la session de la base de données
            db_session.add(new_detection)
            detections_created += 1

        # 5. Si des détections ont été créées, on sauvegarde tout en une seule fois.
        if detections_created > 0:
            print(f"\nSauvegarde de {detections_created} nouvelle(s) détection(s) dans la base de données...")
            db_session.commit()
            print("Sauvegarde terminée.")
        else:
            print("\nAucune nouvelle détection n'a été créée (tous les tweets ciblés étaient vides).")

    except Exception as e:
        print(f"\nUne erreur est survenue durant le traitement : {e}")
        db_session.rollback() # On annule les changements en cas de problème
    finally:
        db_session.close() # On ferme toujours la connexion

    print("--- Traitement par lot terminé ---")

if __name__ == "__main__":
    # Ce bloc est exécuté lorsque vous lancez le script directement
    process_unclassified_tweets()
