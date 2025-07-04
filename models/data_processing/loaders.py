# data_processing/loaders.py

import pandas as pd
from datasets import load_dataset
import config # Importer notre fichier de configuration

# Dans data_processing/loaders.py

def _preparer_bsard() -> pd.DataFrame:
    """Charge et formate le dataset BSARD (Français)."""
    print("Chargement et préparation de BSARD...")
    
    # Ancien nom incorrect :
    # dataset = load_dataset("bsard", "french", split='train')
    
    # ✅ Nom correct :
    dataset = load_dataset("bsard-dataset/bsard", "french", split='train')
    
    df = pd.DataFrame(dataset)
    # On renomme 'title' en 'texte' et on garde la colonne 'label' qui est déjà correcte (0/1).
    return df[['title', 'label']].rename(columns={'title': 'texte'})

def _preparer_liar() -> pd.DataFrame:
    """Charge et formate le dataset LIAR (Anglais)."""
    print("Chargement et préparation de LIAR...")
    dataset = load_dataset("liar", split='train')
    df = pd.DataFrame(dataset)
    # On transforme les 6 labels textuels en 2 labels numériques (0 pour VRAI, 1 pour FAUX).
    label_map = {
        'pants-fire': 1, 'false': 1, 'barely-true': 1, # Classes considérées comme "Fake"
        'half-true': 0, 'mostly-true': 0, 'true': 0     # Classes considérées comme "Real"
    }
    df['label'] = df['label'].map(label_map)
    df_final = df[['statement', 'label']].rename(columns={'statement': 'texte'})
    # On supprime les lignes où la conversion de label a échoué.
    return df_final.dropna()

def _preparer_fever() -> pd.DataFrame:
    """Charge et formate le dataset FEVER (Anglais)."""
    print("Chargement et préparation de FEVER...")
    dataset = load_dataset("fever", "v1.0", split='train')
    df = pd.DataFrame(dataset)
    # On ne garde que les affirmations clairement supportées ou contredites.
    df_filtered = df[df['label'].isin(['SUPPORTS', 'REFUTES'])]
    label_map = {'SUPPORTS': 0, 'REFUTES': 1} # Supports = REAL, Refutes = FAKE
    df_filtered['label'] = df_filtered['label'].map(label_map)
    return df_filtered[['claim', 'label']].rename(columns={'claim': 'texte'})

def _preparer_fake_news_english() -> pd.DataFrame:
    """Charge et formate le dataset george-mcintire/fake-news (Anglais)."""
    print("Chargement et préparation de 'george-mcintire/fake-news'...")
    dataset = load_dataset("george-mcintire/fake-news", split='train')
    df = pd.DataFrame(dataset)
    # Les labels (0/1) et la colonne 'text' sont déjà bien formatés.
    return df[['text', 'label']].rename(columns={'text': 'texte'})


def get_unified_dataset() -> pd.DataFrame:
    """
    Fonction principale qui orchestre le chargement de tous les datasets,
    les combine et retourne un DataFrame final mélangé.
    """
    print("--- Démarrage de l'unification des datasets ---")
    
    # Appel de chaque fonction de préparation
    df_bsard = _preparer_bsard()
    df_liar = _preparer_liar()
    df_fever = _preparer_fever()
    df_fake_news_english = _preparer_fake_news_english()

    # Concaténation de tous les DataFrames en un seul
    df_complet = pd.concat([df_bsard, df_liar, df_fever, df_fake_news_english], ignore_index=True)
    
    # Mélanger le dataset final pour assurer une distribution homogène des données.
    # C'est crucial pour que le modèle ne voie pas les datasets les uns après les autres.
    df_complet = df_complet.sample(frac=1, random_state=config.RANDOM_STATE).reset_index(drop=True)
    
    print(f"\n--- Dataset unifié final créé avec {len(df_complet)} exemples ---")
    return df_complet