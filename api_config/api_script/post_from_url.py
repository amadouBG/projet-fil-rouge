# api_config/api_script/post_from_url.py

import re
from urllib.parse import urlparse
from datetime import datetime
import os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from atproto import Client, models
from sqlalchemy.orm import Session, joinedload

# Importations depuis votre projet
from .config import BLUESKY_HANDLE, APP_PASSWORD
from .models import SessionLocal, Author, Tweet, Detection, Base, engine

# ==============================================================================
# SECTION POUR LE MODÈLE DE PRÉDICTION (INCHANGÉE)
# ==============================================================================
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
MODEL_PATH = os.path.join(PROJECT_ROOT, 'models', 'final_model_bert')
if not os.path.isdir(MODEL_PATH):
    raise FileNotFoundError(f"Le dossier du modèle est introuvable: {MODEL_PATH}")
MODEL_NAME = os.path.basename(MODEL_PATH)
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Utilisation du périphérique : {DEVICE}")
print(f"Chargement du modèle depuis : {MODEL_PATH}")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH, local_files_only=True).to(DEVICE)
model.eval()
print("Modèle prêt.")

def clean_text_for_prediction(text):
    text = re.sub(r"http\S+|www\S+", "<URL>", text)
    text = re.sub(r"@\w+", "<USER>", text)
    text = re.sub(r"#(\w+)", r"<HASHTAG> \1", text)
    return text.strip()

def predict_text_veracity(text):
    cleaned = clean_text_for_prediction(text)
    enc = tokenizer(
        cleaned, add_special_tokens=True, max_length=128,
        padding='max_length', truncation=True, return_tensors='pt'
    )
    input_ids = enc['input_ids'].to(DEVICE)
    attention_mask = enc['attention_mask'].to(DEVICE)
    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        probs = torch.softmax(outputs.logits, dim=1)[0].cpu().numpy()
    diff = abs(probs[0] - probs[1])
    threshold = 0.15
    if diff < threshold:
        label = "Opinion personnelle"
    else:
        label = "Vrai" if probs[1] > probs[0] else "Faux"
    highest_probability = float(max(probs))
    return label, highest_probability, threshold

# ==============================================================================
# SECTION POUR LA LOGIQUE MÉTIER (MODIFIÉE)
# ==============================================================================

def parse_bluesky_url(url: str) -> tuple[str | None, str | None]:
    BLUESKY_URL_PATTERN = re.compile(r"https?://bsky\.app/profile/([^/]+)/post/([^/]+)")
    match = BLUESKY_URL_PATTERN.match(url)
    if match: return match.group(1), match.group(2)
    parsed = urlparse(url)
    if parsed.scheme == 'at':
        parts = parsed.path.split('/')
        if len(parts) == 4 and parts[2] == 'app.bsky.feed.post': return parts[1], parts[3]
    return None, None

def get_bluesky_client() -> Client:
    client = Client()
    try:
        client.login(BLUESKY_HANDLE, APP_PASSWORD)
        print("Connexion à Bluesky réussie.")
        return client
    except Exception as e:
        print(f"Erreur de connexion à Bluesky: {e}")
        raise

def get_or_create_author(db: Session, author_profile: models.AppBskyActorDefs.ProfileViewDetailed) -> Author:
    author = db.query(Author).filter(Author.bluesky_id == author_profile.did).first()
    if not author:
        print(f"Création de l'auteur: {author_profile.handle}")
        author = Author(handle=author_profile.handle, display_name=author_profile.display_name, bluesky_id=author_profile.did)
        db.add(author)
        db.commit()
        db.refresh(author)
    return author

def fetch_and_store_post(url: str, user_id: int | None = None) -> tuple[Tweet | None, Detection | None, str]:
    identifier, rkey = parse_bluesky_url(url)
    if not identifier or not rkey:
        return None, None, 'error'

    db = SessionLocal()
    try:
        client = get_bluesky_client()
        repo_did = identifier
        if not identifier.startswith('did:'):
            resolved_did = client.com.atproto.identity.resolve_handle(models.ComAtprotoIdentityResolveHandle.Params(handle=identifier))
            repo_did = resolved_did.did
        at_uri = f"at://{repo_did}/app.bsky.feed.post/{rkey}"

        existing_tweet = db.query(Tweet).options(joinedload(Tweet.author), joinedload(Tweet.detections)).filter(Tweet.bluesky_id == at_uri).first()
        if existing_tweet:
            print(f"Le tweet {at_uri} existe déjà. Chargement depuis la BDD.")
            detection = existing_tweet.detections[0] if existing_tweet.detections else None
            return existing_tweet, detection, 'existing'

        response = client.app.bsky.feed.get_post_thread(models.AppBskyFeedGetPostThread.Params(uri=at_uri, depth=0))
        if not isinstance(response.thread, models.AppBskyFeedDefs.ThreadViewPost):
            return None, None, 'error'

        post_view = response.thread.post
        author_profile = client.app.bsky.actor.get_profile(models.AppBskyActorGetProfile.Params(actor=post_view.author.did))
        author_db = get_or_create_author(db, author_profile)

        record = post_view.record
        content = getattr(record, 'text', '')
        language = getattr(record, 'langs', [None])[0] if getattr(record, 'langs', None) else None
        posted_at_str = getattr(record, 'created_at', None)
        posted_at_dt = datetime.fromisoformat(posted_at_str.replace('Z', '+00:00')) if posted_at_str else None

        new_tweet = Tweet(bluesky_id=post_view.uri, author_id=author_db.id, user_id=user_id, content=content, language=language, posted_at=posted_at_dt)
        db.add(new_tweet)
        db.commit()
        db.refresh(new_tweet)
        print(f"Tweet {new_tweet.bluesky_id} ajouté à la BDD (ID: {new_tweet.id}).")

        new_detection = None
        if content:
            print("Lancement de la prédiction sur le contenu...")
            label, probability, threshold = predict_text_veracity(content)
            print(f"-> Résultat : {label} (Prob: {probability:.4f})")
            new_detection = Detection(tweet_id=new_tweet.id, label=label, probability=probability, model_used=MODEL_NAME, threshold=threshold, verified=False)
            db.add(new_detection)
            db.commit()
            db.refresh(new_detection)
            print(f"Détection (ID: {new_detection.id}) ajoutée pour le tweet {new_tweet.id}.")
        else:
            print("Contenu vide, pas de détection.")

        # --- CORRECTION APPLIQUÉE ICI ---
        # On re-cherche le tweet fraîchement créé en s'assurant de charger
        # ses relations. Cela "attache" les objets `author` et `detections`
        # à l'objet `tweet` avant que la session ne soit fermée.
        final_tweet_to_return = db.query(Tweet).options(
            joinedload(Tweet.author),
            joinedload(Tweet.detections)
        ).filter(Tweet.id == new_tweet.id).one()
        final_detection_to_return = final_tweet_to_return.detections[0] if final_tweet_to_return.detections else None
        # --- FIN DE LA CORRECTION ---

        return final_tweet_to_return, final_detection_to_return, 'new'

    except Exception as e:
        print(f"Une erreur est survenue lors du traitement de {url}: {e}")
        if db: db.rollback()
        return None, None, 'error'
    finally:
        if db: db.close()

