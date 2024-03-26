import nltk

nltk.download(["movie_reviews", "averaged_perceptron_tagger"])

unwanted = nltk.corpus.stopwords.words("english")
unwanted.extend([w.lower() for w in nltk.corpus.names.words()])


def skip_unwanted(pos_tuple):
    word, tag = pos_tuple

    if not word.isalpha() or word in unwanted:
        return False

    # NN: Noun, singular or mass
    if tag.startswith("NN"):
        return False

    return True


# Récupère les mots à connotation neg/pos en enlevant les mots inutiles grâce aux tags "Part Of Speech"
positive_words = [word for word, tag in filter(
    skip_unwanted,
    nltk.pos_tag(nltk.corpus.movie_reviews.words(categories=["pos"]))
)]
negative_words = [word for word, tag in filter(
    skip_unwanted,
    nltk.pos_tag(nltk.corpus.movie_reviews.words(categories=["neg"]))
)]

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

print("top_100_positive: ", top_100_positive)
print("top_100_negative: ", top_100_negative)
