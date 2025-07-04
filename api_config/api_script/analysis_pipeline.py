# api_config/api_script/analysis_pipeline.py

from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

# --- MODÈLE 1: DÉTECTION FAKE NEWS (BINAIRE) ---
MODEL_NAME_FAKE_NEWS = "mohammadjavadpirhadi/roberta-base-fake-news-detection"

try:
    fake_news_classifier = pipeline(
        "text-classification",
        model=MODEL_NAME_FAKE_NEWS
    )
    print(f"INFO: Modèle de détection Fake News ('{MODEL_NAME_FAKE_NEWS}') chargé.")
except Exception as e:
    print(f"ERREUR: Impossible de charger le modèle Fake News ('{MODEL_NAME_FAKE_NEWS}'): {e}")
    fake_news_classifier = None

def classify_content_v1(text: str) -> str | None:
    """
    Classifie le texte en "Fake News" ou "Non Fake News" avec le modèle RoBERTa,
    en affichant le score de confiance et en filtrant par un seuil.
    """
    if not fake_news_classifier:
        print("ERREUR: Modèle Fake News non disponible.")
        return "Erreur Modèle"

    if not text or not isinstance(text, str) or len(text.strip()) == 0:
        print("WARN: Texte d'entrée vide ou invalide pour classify_content_v1.")
        return "Texte Invalide"

    try:
        print(f"INFO: Classification du contenu (Modèle 1 - RoBERTa): \"{text[:100]}...\"")
        results = fake_news_classifier(text)

        predicted_label_from_model = results[0]['label'].lower() # Convertir en minuscules pour la comparaison
        score = results[0]['score']
        print(f"INFO: Prédiction brute Modèle 1 ('{MODEL_NAME_FAKE_NEWS}'): Label='{predicted_label_from_model}', Score={score:.4f}")

        seuil_confiance = 0.60

        if score < seuil_confiance:
            print(f"WARN: Score ({score:.2f}) inférieur au seuil de confiance ({seuil_confiance})")
            return f"Indéterminé (Score: {score:.2f})"

        # -------- VEUILLEZ ADAPTER CETTE PARTIE SELON LA MODEL CARD ! --------
        # Supposons que la model card dise que le modèle retourne "fake" ou "real"
        # (Vérifiez si c'est le cas, ou si c'est LABEL_0 / LABEL_1, etc.)
        if predicted_label_from_model == "fake": # Exemple: si le label FAKE est "fake"
            return f"Fake News (Score: {score:.2f})"
        elif predicted_label_from_model == "real": # Exemple: si le label REAL est "real"
            return f"Non Fake News (Score: {score:.2f})"
        # --- Exemple si les labels sont LABEL_0 et LABEL_1 ---
        # --- (Décommentez et adaptez si c'est le cas pour votre modèle) ---
        # elif predicted_label_from_model == "label_1": # Supposons LABEL_1 = FAKE
        #     return f"Fake News (Score: {score:.2f})"
        # elif predicted_label_from_model == "label_0": # Supposons LABEL_0 = REAL
        #     return f"Non Fake News (Score: {score:.2f})"
        else:
            print(f"WARN: Label inattendu ('{predicted_label_from_model}') du modèle Fake News.")
            return f"Indéterminé (Label inconnu, Score: {score:.2f})"
        # -------- FIN DE LA PARTIE À ADAPTER --------

    except Exception as e:
        print(f"ERREUR: Échec de la classification du contenu (Modèle 1): {e}")
        return "Erreur Classification"

# --- MODÈLE 2: ANALYSE DE SENTIMENTS (sera ajouté plus tard) ---
# def analyze_sentiment_v1(text: str) -> str | None:
#     pass

# --- FONCTION PRINCIPALE DE LA PIPELINE ---
def run_analysis_pipeline(text: str) -> dict:
    result_model1 = classify_content_v1(text)
    result_model2 = None

    # --- MODIFICATION DE LA CONDITION ICI ---
    if result_model1 and result_model1.startswith("Non Fake News"):
    # --- FIN MODIFICATION ---
        result_model2 = "Bientôt disponible (Sentiments)" # On l'activera plus tard

    return {
        "classification_contenu": result_model1,
        "analyse_sentiment": result_model2
    }

if __name__ == '__main__':
    # Tests
    sample_text_fake = "BREAKING NEWS: Moon landing was faked, says anonymous source with blurry photo."
    sample_text_real = "The United Nations headquarters is located in New York City."
    another_text = "This is a general statement that isn't news."
    ambiguous_text = "Maybe this is true, or maybe not, who knows these days?" # Pour tester le seuil

    print("\n--- Test avec texte potentiellement FAKE ---")
    analysis_fake = run_analysis_pipeline(sample_text_fake)
    print(f"Résultat final: {analysis_fake}")

    print("\n--- Test avec texte potentiellement REAL ---")
    analysis_real = run_analysis_pipeline(sample_text_real)
    print(f"Résultat final: {analysis_real}")

    print("\n--- Test avec un autre texte ---")
    analysis_other = run_analysis_pipeline(another_text)
    print(f"Résultat final: {analysis_other}")

    print("\n--- Test avec un texte ambigu (pour seuil) ---")
    analysis_ambiguous = run_analysis_pipeline(ambiguous_text)
    print(f"Résultat final: {analysis_ambiguous}")