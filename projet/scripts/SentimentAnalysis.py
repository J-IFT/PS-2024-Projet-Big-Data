import pickle
import pandas as pd
from random import shuffle
from statistics import mean

import nltk
from nltk.sentiment import SentimentIntensityAnalyzer


# region==== ENTRAINEMENT DU MODELE ====
# Le but est de récolter les mots présents dans les reviews de films déjà catégoriés.
# En comparant les deux listes de mots on peux supprimer les mots en communs pour
# obtenir une liste de mots à forte connotation positive ou négative.
def skip_unwanted(pos_tuple):
    # Liste de mots inutiles, qui ne serviront pas à déterminer le sentiment
    unwanted_words = nltk.corpus.stopwords.words("english")
    unwanted_words.extend([w.lower() for w in nltk.corpus.names.words()])

    word, tag = pos_tuple
    if not word.isalpha() or word in unwanted_words:
        return False
    if tag.startswith("NN"):
        return False
    return True


def get_top_100_words():
    print("Get the top neg/pos words...")
    positive_words = [word for word, tag in filter(
        skip_unwanted,
        nltk.pos_tag(nltk.corpus.movie_reviews.words(categories=["pos"]))
    )]
    negative_words = [word for word, tag in filter(
        skip_unwanted,
        nltk.pos_tag(nltk.corpus.movie_reviews.words(categories=["neg"]))
    )]

    # Récupères tout les mots des reviews
    positive_fd = nltk.FreqDist(positive_words)
    negative_fd = nltk.FreqDist(negative_words)

    # Crée une liste des mots en communs entre les reviews positives et négatives.
    common_set = set(positive_fd).intersection(negative_fd)

    # Supprime les mots en commun pour ne que ceux ayant une forte connotation positive ou négative.
    for word in common_set:
        del positive_fd[word]
        del negative_fd[word]

    top_100_positive = {word for word, count in positive_fd.most_common(100)}
    top_100_negative = {word for word, count in negative_fd.most_common(100)}

    return top_100_positive, top_100_negative


# Crée des features pour représenter les reviews en se concentrant sur le positif.
def extract_features(text, model):
    print("Extract features")
    top_100_positive, top_100_negative = get_top_100_words()

    features = dict()
    wordcount = 0
    compound_scores = list()
    positive_scores = list()

    for sentence in nltk.sent_tokenize(text):
        for word in nltk.word_tokenize(sentence):
            if word.lower() in top_100_positive:
                wordcount += 1
        compound_scores.append(model.polarity_scores(sentence)["compound"])
        positive_scores.append(model.polarity_scores(sentence)["pos"])

    features["mean_compound"] = mean(compound_scores) + 1  # moyenne du sentiment général des phrases de la review
    features["mean_positive"] = mean(positive_scores)  # moyenne des scores de positivités des phrases
    features["wordcount"] = wordcount  # Nombres de mots du top 100 positif apparaissant dans la review

    return features


def create_nb_classifier():
    # Téléchargements des corpus pour entrainer notre modèle
    nltk.download([
        "names",
        "stopwords",
        "movie_reviews",
        "averaged_perceptron_tagger",
        "vader_lexicon",
        "punkt",
    ])

    # Modèle préentrainé de NLTK
    vader = SentimentIntensityAnalyzer()

    features = [
        (extract_features(nltk.corpus.movie_reviews.raw(review), vader), "pos")
        for review in nltk.corpus.movie_reviews.fileids(categories=["pos"])
    ]
    features.extend([
        (extract_features(nltk.corpus.movie_reviews.raw(review), vader), "neg")
        for review in nltk.corpus.movie_reviews.fileids(categories=["neg"])
    ])

    # Entrainement du modèle Vader à partir de nos nouvelles données
    train_count = len(features) // 4
    shuffle(features)
    classifier = nltk.NaiveBayesClassifier.train(features[:train_count])

    # Précision du nouveau modèle
    print(nltk.classify.accuracy(classifier, features[train_count:]))

    # Sauvegarde le classifier
    with (open("./projet/scripts/nb_classifier.pickle", "wb") as new_classifier_file):
        pickle.dump(classifier, new_classifier_file)

    return classifier
# endregion


try:
    print("Opening the pickle jar...")
    with open("./projet/scripts/nb_classifier.pickle", "rb") as f:
        nb_classifier = pickle.load(f)
except FileNotFoundError:
    print("Pickle Jar doesn't exist, creating a new one...")
    nb_classifier = create_nb_classifier()


# Charger le fichier livre nettoyé
book_nb = 4
book_path = f"./projet/output/bigdataprocessing/book_{book_nb}_clean.txt"
with open(book_path) as f:
    book = f.read().replace("\n", "")

# Occurrence
print("Starting counting occurrences...")
book_fd = nltk.FreqDist(nltk.word_tokenize(book))
most_commons = {word: count for word, count in book_fd.most_common(50)}
print("Most common words: ", most_commons)

df_most_commons = pd.DataFrame(list(most_commons.items()), columns=["Word", "Frequency"])
df_most_commons.to_csv(f"./projet/output/sentimentanalysis/book_{book_nb}-occurrence.csv", index=False)

# Juger de la positivité du texte
print("Starting sentiment analysis...")
vader = SentimentIntensityAnalyzer()
book_polarity = vader.polarity_scores(book)
print("Book polarity: ", book_polarity)

df_book_polarity = pd.DataFrame(list(book_polarity.items()), columns=["Sentiment", "Value"])
df_book_polarity.to_csv(f"./projet/output/sentimentanalysis/book_{book_nb}-sentimentanalysis.csv", index=False)

print("All done.")
