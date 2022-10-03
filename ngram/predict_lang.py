import pickle
from nltk import word_tokenize
from nltk import ngrams


# This function computes the probability that the line is in the specified language
# by using laplace smoothing
def compute_prob(text, unigram_dict, bigram_dict, vocab_size):
    # get unigrams and bigrams of the input text
    unigrams_test = word_tokenize(text)

    # Uniform the text and remove punctuation
    unigrams_test = [token.lower() for token in unigrams_test if token.isalpha()]

    bigrams_test = list(ngrams(unigrams_test, 2))

    # calculates the probability for each bigram
    lang_prob = 1
    for bigram in bigrams_test:
        uni = bigram[0]

        b = bigram_dict[bigram] if bigram in bigram_dict else 0
        u = unigram_dict[uni] if uni in unigram_dict else 0

        # Laplace formula
        lang_prob *= (b+1)/(u+vocab_size)

    return lang_prob


# def verify_ans(ans):


if __name__ == '__main__':
    # unpickle the dictionaries from previous program
    with open('pickle_files/bigram_eng.pickle', 'rb') as handle:
        bigram_eng = pickle.load(handle)
    with open('pickle_files/unigram_eng.pickle', 'rb') as handle:
        unigram_eng = pickle.load(handle)
    with open('pickle_files/bigram_fr.pickle', 'rb') as handle:
        bigram_fr = pickle.load(handle)
    with open('pickle_files/unigram_fr.pickle', 'rb') as handle:
        unigram_fr = pickle.load(handle)
    with open('pickle_files/bigram_it.pickle', 'rb') as handle:
        bigram_it = pickle.load(handle)
    with open('pickle_files/unigram_it.pickle', 'rb') as handle:
        unigram_it = pickle.load(handle)

    # Calculate the total vocab size
    total_vocab_size = len(unigram_eng) + len(unigram_fr) + len(unigram_it)

    # Open the test Wfile
    test_file = open('ngram_files/LangId.test', 'r')
    test_text = test_file.read()
    test_text = test_text.splitlines()

    output_file = open("ngram_files/LangId.out", "w")

    # Calculate the probabilities for each line of test_text
    for line_number, line in enumerate(test_text):
        if line_number == 23:
            print('stop')

        # Get probabilities
        eng_prob = compute_prob(line, unigram_eng, bigram_eng, total_vocab_size)
        fr_prob = compute_prob(line, unigram_fr, bigram_fr, total_vocab_size)
        it_prob = compute_prob(line, unigram_it, bigram_it, total_vocab_size)

        # Output highest probability to the file
        if eng_prob > fr_prob and eng_prob > it_prob:
            output_file.write(f'{line_number + 1} English\n')
        elif fr_prob > eng_prob and fr_prob > it_prob:
            output_file.write(f'{line_number + 1} French\n')
        elif it_prob > eng_prob and it_prob > fr_prob:
            output_file.write(f'{line_number + 1} Italian\n')
        else:
            output_file.write(f'{line_number + 1} Undefined\n')

    output_file.close()
