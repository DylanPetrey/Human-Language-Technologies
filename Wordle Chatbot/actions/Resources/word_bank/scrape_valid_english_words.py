from nltk import word_tokenize
from urllib import request
from nltk.corpus import stopwords
import enchant


web_url = 'https://raw.githubusercontent.com/dwyl/english-words/master/words.txt'

def convert_txt_to_yaml():
    yaml = list()

    yaml.append('version: "3.1"\n')
    yaml.append('nlu:\n')
    yaml.append('  - lookup: valid_guess\n')
    yaml.append('    examples: |\n')

    with open('actions/Resources/word_bank/word_bank.txt') as word_bank_file:
        for word in word_bank_file:
            yaml.append('      - {}'.format(word))

    with open('data/lookups/valid_guess.yml', 'w') as yfile:
        yfile.write("".join(yaml))


if __name__ == '__main__':
    # Read all english words from url
    response = request.urlopen(web_url)
    raw = response.read().decode('utf8')

    # Tokenize
    tokens = word_tokenize(raw)

    # Filter out unneeded words
    stopwords = stopwords.words('english')
    tokens = [w.lower() for w in tokens if w.isalpha() and w not in stopwords and len(w) == 5]
    # get words with definitions in the nltk wordnet
    d = enchant.Dict("en_US")
    tokens = [t for t in tokens if d.check(t)]

    with open('actions/Resources/word_bank/word_bank.txt', 'w') as f:
        for token in tokens:
            f.write("{}\n".format(token))

    convert_txt_to_yaml()
