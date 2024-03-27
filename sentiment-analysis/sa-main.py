import math
from random import shuffle
from statistics import mean

import nltk
from nltk.sentiment import SentimentIntensityAnalyzer


def get_sentences_avg_compound(sentences):
    compound = 0
    for sentence in sentences:
        compound += vader.polarity_scores(sentence)['compound']

    # Arrondit à 4 chiffres pour correspondre au compound de vader
    return round(compound / len(sentences), 4)


def skip_unwanted(pos_tuple):
    word, tag = pos_tuple

    if not word.isalpha() or word in unwanted_words:
        return False

    # NN: Noun, singular or mass
    # Retire tout ce qui s'apparente à un nom commun ou propre
    if tag.startswith("NN"):
        return False

    return True


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

    # Adding 1 to the final compound score to always have positive numbers
    # since some classifiers you'll use later don't work with negative numbers.
    features["mean_compound"] = mean(compound_scores) + 1
    features["mean_positive"] = mean(positive_scores)
    features["wordcount"] = wordcount

    return features


def process_tokens(tokens):
    return [word for word, tag in filter(
        skip_unwanted,
        nltk.pos_tag(tokens)
    )]


nltk.download(["stopwords", "names", "state_union", "punkt", "movie_reviews", "averaged_perceptron_tagger"])

if __name__ == "__main__":
    # Récupère le fichier en texte brut
    # TODO: Remplacer avec les fichiers livres
    stateUnionRaw = nltk.corpus.state_union.raw('1945-Truman.txt')

    # Modèle prè-entrainé de NLTK
    vader = SentimentIntensityAnalyzer()

    unwanted_words = nltk.corpus.stopwords.words("english")
    unwanted_words.extend([w.lower() for w in nltk.corpus.names.words()])

    # Récupère les mots à connotation neg/pos en enlevant les mots inutiles grâce aux tags "Part Of Speech"
    positive_words = process_tokens(nltk.corpus.movie_reviews.words(categories=["pos"]))
    negative_words = process_tokens(nltk.corpus.movie_reviews.words(categories=["neg"]))

    # Frequency distribution
    # Récupères les mots à connotation les plus présents
    positive_fd = nltk.FreqDist(positive_words)
    negative_fd = nltk.FreqDist(negative_words)

    common_set = set(positive_fd).intersection(negative_fd)

    for word in common_set:
        del positive_fd[word]
        del negative_fd[word]

    # Les 100 mots apparaissant les plus souvent, uniquement dans des reviews positives ou négatives
    # On est donc censé obtenir des mots à forte valeur positive/negative
    top_100_positive = {word for word, count in positive_fd.most_common(100)}
    top_100_negative = {word for word, count in negative_fd.most_common(100)}

features = [
    (extract_features(nltk.corpus.movie_reviews.raw(review)), "pos")
    for review in nltk.corpus.movie_reviews.fileids(categories=["pos"])
]
features.extend([
    (extract_features(nltk.corpus.movie_reviews.raw(review)), "neg")
    for review in nltk.corpus.movie_reviews.fileids(categories=["neg"])
])

# Entrainer le classificateur
train_count = math.floor(len(features) * 0.8)
shuffle(features)
classifier = nltk.NaiveBayesClassifier.train(features[:train_count])
print("Précision du modèle: ", nltk.classify.accuracy(classifier, features[train_count:]))

print(classifier.classify(extract_features(stateUnionRaw)))
print(extract_features(stateUnionRaw))
