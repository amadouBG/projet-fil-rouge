# ✅ PIPELINE COMPLETE POUR LA CLASSIFICATION DE TWEETS ET VÉRIFICATION DE FAITS
# ---
# Catégories : Opinion personnelle, Information factuelle, Humour noir/satire
# Données : LIAR/Politifact, COVID-19 Fake News, TweetEval
# Objectif : Classifier les tweets puis vérifier la véracité si "information" > seuil

#############################################
# 📅 1. PRÉREQUIS ET INSTALLATION
#############################################

# 📌 Prérequis Python (minimum)
# !pip install torch transformers datasets scikit-learn pandas gradio

# 🔹 Bibliothèques
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import load_dataset, concatenate_datasets, DatasetDict
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np
import gradio as gr


#############################################
# 🔹 2. CHARGEMENT & PRÉTRAITEMENT DES DONNÉES
#############################################

# • LIAR (Politifact) : class label = [pants-fire, false, barely-true, half-true, mostly-true, true] (regroupables en vrai/faux)
# • COVID-19 : textes annotés comme fake/news
# • TweetEval (subtask sentiment/fakenews)

liar = load_dataset("liar", split="train")  # Split en 'train' par défaut
covid = load_dataset("csv", data_files="covid_fake_news.csv")  # Doit être préparé au format texte+label

# Dataset TweetEval (fakenews)
tweeteval = load_dataset("tweet_eval", "fakenews")

# Nettoyage et uniformisation des labels
def preprocess_liar(example):
    label_map = {
        "true": 1, "mostly-true": 1, "half-true": 1,
        "barely-true": 0, "false": 0, "pants-fire": 0
    }
    return {"text": example["statement"], "label": label_map.get(example["label"], 0)}

liar_proc = liar.map(preprocess_liar)
covid_proc = covid["train"].rename_column("text_column", "text").rename_column("label_column", "label")
tweeteval_proc = tweeteval["train"].rename_column("text", "text").rename_column("label", "label")

# Quantification
print("\n[INFO] Taille LIAR:", len(liar_proc))
print("[INFO] Taille COVID:", len(covid_proc))
print("[INFO] Taille TweetEval:", len(tweeteval_proc))

# Fusion de tout en un seul dataset d'entraînement
dataset_total = concatenate_datasets([liar_proc, covid_proc, tweeteval_proc])

# Train/test split
train_data, test_data = dataset_total.train_test_split(test_size=0.2).values()


#############################################
# 🎓 3. FINE-TUNING DU MODÈLE BERTWEET
#############################################

model_ckpt = "vinai/bertweet-base"
tokenizer = AutoTokenizer.from_pretrained(model_ckpt)

# Tokenisation
def tokenize_function(example):
    return tokenizer(example["text"], truncation=True, padding="max_length", max_length=128)

train_enc = train_data.map(tokenize_function, batched=True)
test_enc = test_data.map(tokenize_function, batched=True)

model = AutoModelForSequenceClassification.from_pretrained(model_ckpt, num_labels=3)

args = TrainingArguments(
    output_dir="bertweet-fake-news-classifier",
    evaluation_strategy="epoch",
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=3,
    save_strategy="epoch",
    load_best_model_at_end=True,
    logging_dir="logs"
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=train_enc,
    eval_dataset=test_enc
)

# Décommenter pour lancer l'entraînement
# trainer.train()


#############################################
# 💡 4. PRÉDICTION AVEC SEUIL DE FACT-CHECKING
#############################################

FACT_CHECK_THRESHOLD = 0.75  # Seuil de détection de "vraie" information
label_map = {0: "Opinion", 1: "Information", 2: "Humour/Satire"}

def classify_and_check(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    with torch.no_grad():
        logits = model(**inputs).logits
    probs = torch.nn.functional.softmax(logits, dim=-1)[0]

    prob_dict = {label_map[i]: float(p) for i, p in enumerate(probs)}
    predicted = max(prob_dict, key=prob_dict.get)
    trigger_check = prob_dict["Information"] >= FACT_CHECK_THRESHOLD

    return {
        "Classe prédite": predicted,
        **{k: f"{v*100:.2f}%" for k, v in prob_dict.items()},
        "Fact-check nécessaire": "Oui" if trigger_check else "Non"
    }


#############################################
# 📈 5. INTERFACE GRADIO
#############################################

demo = gr.Interface(
    fn=classify_and_check,
    inputs=gr.Textbox(label="Entrez un tweet"),
    outputs=[
        gr.Label(label="Classe prédite"),
        gr.Label(label="Probabilités (Opinion)"),
        gr.Label(label="Probabilités (Information)"),
        gr.Label(label="Probabilités (Humour/Satire)"),
        gr.Label(label="Fact-check nécessaire")
    ],
    title="Détection de Fake News & Typologie Tweet",
    description="Classifie les tweets et vérifie si nécessaire."
)

# Lancer l'UI
# demo.launch()
