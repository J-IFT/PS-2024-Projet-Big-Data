import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from random import shuffle
from statistics import mean

# Téléchargements des corpus pour entrainer notre modèle
nltk.download([
    "names",
    "stopwords",
    "movie_reviews",
    "averaged_perceptron_tagger",
    "vader_lexicon",
    "punkt",
])

# region==== ENTRAINEMENT DU MODELE ====
# Le but est de récolter les mots présents dans les reviews de films déjà catégoriés.
# En comparant les deux listes de mots on peux supprimer les mots en communs pour
# obtenir une liste de mots à forte connotation positive ou négative.
positive_review_ids = nltk.corpus.movie_reviews.fileids(categories=["pos"])
negative_review_ids = nltk.corpus.movie_reviews.fileids(categories=["neg"])
all_review_ids = positive_review_ids + negative_review_ids

# Liste de mots inutiles, qui ne serviront pas à déterminer le sentiment
unwanted_words = nltk.corpus.stopwords.words("english")
unwanted_words.extend([w.lower() for w in nltk.corpus.names.words()])


def skip_unwanted(pos_tuple):
    word, tag = pos_tuple
    if not word.isalpha() or word in unwanted_words:
        return False
    if tag.startswith("NN"):
        return False
    return True


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

# Modèle préentrainé de NLTK
vader = SentimentIntensityAnalyzer()


# Crée des features pour représenter les reviews en se concentrant sur le positif.
def extract_features(text):
    features = dict()
    wordcount = 0
    compound_scores = list()
    positive_scores = list()

    for sentence in nltk.sent_tokenize(text):
        for word in nltk.word_tokenize(sentence):
            if word.lower() in top_100_positive:
                wordcount += 1
        compound_scores.append(vader.polarity_scores(sentence)["compound"])
        positive_scores.append(vader.polarity_scores(sentence)["pos"])

    features["mean_compound"] = mean(compound_scores) + 1   # moyenne du sentiment général des phrases de la review
    features["mean_positive"] = mean(positive_scores)   # moyenne des scores de positivités des phrases
    features["wordcount"] = wordcount   # Nombres de mots du top 100 positif apparaissant dans la review

    return features


features = [
    (extract_features(nltk.corpus.movie_reviews.raw(review)), "pos")
    for review in nltk.corpus.movie_reviews.fileids(categories=["pos"])
]
features.extend([
    (extract_features(nltk.corpus.movie_reviews.raw(review)), "neg")
    for review in nltk.corpus.movie_reviews.fileids(categories=["neg"])
])

# Entrainement du modèle Vader à partir de nos nouvelles données
train_count = len(features) // 4
shuffle(features)
classifier = nltk.NaiveBayesClassifier.train(features[:train_count])

# Précision du nouveau modèle
print(nltk.classify.accuracy(classifier, features[train_count:]))
# endregion
