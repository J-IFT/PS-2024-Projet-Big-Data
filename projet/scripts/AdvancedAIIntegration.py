from transformers import BertTokenizer, BertForSequenceClassification
from torch.utils.data import DataLoader
import torch

# Charger le tokenizer et le modèle BERT pré-entraîné
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForSequenceClassification.from_pretrained('bert-base-uncased')

# Charger les données depuis un fichier texte
with open("C:/Users/julie/OneDrive - Ifag Paris/Documents/Atelier Big Data/PS-2024-Projet-Big-Data/projet/output/petitbook4traitéparunehumaine.txt", "r", encoding="utf-8") as file:
    text = file.read()

# Tokenization
inputs = tokenizer(text, return_tensors='pt')

# Analyse de sentiment avec BERT
outputs = model(**inputs)

# Prédiction de la classe de sentiment
predicted_class = torch.argmax(outputs.logits)

# Affichage du résultat
print("Sentiment class:", predicted_class.item())
