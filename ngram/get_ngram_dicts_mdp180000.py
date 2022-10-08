import nltk
import pickle
import time
from nltk import ngrams


def get_ngram_dict(filename):
    # open the file
    f = open(filename, 'r', encoding="utf8")

    # Read the input file and store into text
    raw_text = f.read()

    # Remove newlines
    raw_text = ''.join(raw_text.splitlines())

    # Tokenize the text using nltk
    tokens = raw_text.split()

    # Uniform the text and remove punctuation
    tokens = [token.lower() for token in tokens if token.isalpha()]

    # Create bigrams and unigrams using nltk
    bigrams = list(ngrams(tokens, 2))
    unigrams = tokens

    # Create a dictionary of bigrams and unigrams
    bigram_dict = {b: bigrams.count(b) for b in set(bigrams)}
    unigram_dict = {t: unigrams.count(t) for t in set(unigrams)}

    return bigram_dict, unigram_dict


if __name__ == '__main__':
    start = time.process_time()
    # Get the english dictionaries
    bigram_eng, unigram_eng = get_ngram_dict('ngram_files/LangId.train.English')
    with open('pickle_files/bigram_eng.pickle', 'wb') as handle:
        pickle.dump(bigram_eng, handle)
    with open('pickle_files/unigram_eng.pickle', 'wb') as handle:
        pickle.dump(unigram_eng, handle)

    # Get the french dictionaries
    bigram_fr, unigram_fr = get_ngram_dict('ngram_files/LangId.train.French')
    with open('pickle_files/bigram_fr.pickle', 'wb') as handle:
        pickle.dump(bigram_fr, handle)
    with open('pickle_files/unigram_fr.pickle', 'wb') as handle:
        pickle.dump(unigram_fr, handle)

    # Get the italian dictionaries
    bigram_it, unigram_it = get_ngram_dict('ngram_files/LangId.train.Italian')
    with open('pickle_files/bigram_it.pickle', 'wb') as handle:
        pickle.dump(bigram_it, handle)
    with open('pickle_files/unigram_it.pickle', 'wb') as handle:
        pickle.dump(unigram_it, handle)
