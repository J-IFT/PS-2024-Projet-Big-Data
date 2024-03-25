import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize

# Décommenter la ligne ci dessous pour télécharger les données pour le modèle
# nltk.download(["stopwords", "names", "state_union", "punkt"])

# Récupère le fichier en texte brut
# TODO: Remplacer avec les fichiers livres
stateUnionRaw = nltk.corpus.state_union.raw('1945-Truman.txt')

stateUnionSentences = sent_tokenize(stateUnionRaw)

# Modèle prè-entrainé de NLTK
vader = SentimentIntensityAnalyzer()

# Moyenne des compound des phrases
compound = 0
for sentence in stateUnionSentences:
    compound += vader.polarity_scores(sentence)['compound']
compound /= len(stateUnionSentences)

print("Total")
print(vader.polarity_scores(stateUnionRaw))

print("Moyenne")
print(compound)
