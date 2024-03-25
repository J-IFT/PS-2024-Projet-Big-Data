import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize


def get_sentences_avg_compound(sentences):
    compound = 0
    for sentence in sentences:
        compound += vader.polarity_scores(sentence)['compound']

    # Arrondit à 4 chiffres pour correspondre au compound de vader
    return round(compound / len(sentences), 4)


# Décommenter la ligne ci dessous pour télécharger les données pour le modèle
# nltk.download(["stopwords", "names", "state_union", "punkt"])

if __name__ == "__main__":
    # Récupère le fichier en texte brut
    # TODO: Remplacer avec les fichiers livres
    stateUnionRaw = nltk.corpus.state_union.raw('1945-Truman.txt')

    # Modèle prè-entrainé de NLTK
    vader = SentimentIntensityAnalyzer()

    print("Total: ", vader.polarity_scores(stateUnionRaw)["compound"])
    print("Moyenne: ", get_sentences_avg_compound(sent_tokenize(stateUnionRaw)))
