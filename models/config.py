# config.py

# ----------------------------------------------------
# CONFIGURATION DU MODÈLE
# ----------------------------------------------------
# Nom du modèle multilingue pré-entraîné sur le Hugging Face Hub.
MODEL_NAME: str = 'xlm-roberta-base'

# Dossier où le modèle final sera sauvegardé après l'entraînement.
MODEL_OUTPUT_DIR: str = "./xlm_roberta_finetuned_multilingual"


# ----------------------------------------------------
# CONFIGURATION DE L'ENTRAÎNEMENT
# ----------------------------------------------------
# Nombre de fois que le modèle verra l'ensemble du dataset. 2 ou 3 est un bon début.
NUM_TRAIN_EPOCHS: int = 2

# Taille des lots pour l'entraînement. À réduire si vous manquez de mémoire GPU.
TRAIN_BATCH_SIZE: int = 16

# Taille des lots pour l'évaluation. Peut être plus grande car moins gourmande en mémoire.
EVAL_BATCH_SIZE: int = 32

# Vitesse d'apprentissage du modèle.
LEARNING_RATE: float = 2e-5

# Activer l'entraînement en précision mixte (fp16) pour accélérer le processus sur les GPU
# compatibles (NVIDIA Volta, Turing, Ampere et plus récents). Mettre à False sinon.
FP16: bool = True


# ----------------------------------------------------
# CONFIGURATION DES DONNÉES
# ----------------------------------------------------
# Longueur maximale des séquences. Les textes plus longs seront tronqués.
MAX_LENGTH: int = 160

# Pourcentage du dataset à utiliser pour la validation (ex: 0.15 = 15%).
TEST_SIZE: float = 0.15

# Graine pour la reproductibilité des divisions de données et du mélange.
RANDOM_STATE: int = 42