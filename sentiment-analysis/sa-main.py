import nltk

# nltk.download(["stopwords", "names", "state_union"])

stopwords = nltk.corpus.stopwords.words("english")

# w.isalpha() pour inclure seulement les "mots" composés de lettre. Sinon inclus la ponctuation
words = [w for w in nltk.corpus.state_union.words() if w.isalpha()]
words = [w for w in words if w.lower() not in stopwords]
# Pour transformer un texte en liste de mots avec nltk: nltk.word_tokenize(text)

print(words)
