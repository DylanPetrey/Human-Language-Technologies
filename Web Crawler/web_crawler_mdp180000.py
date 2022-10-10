import os
import pickle
import re
import string
import requests

from bs4 import BeautifulSoup
from nltk import word_tokenize, sent_tokenize
from nltk import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk import ngrams
from nltk import FreqDist


# This function opens a url and stores the first 50 URLs to a list
def extract_urls(link) -> list:
    r = requests.get(starter_url)
    data = r.text
    soup = BeautifulSoup(data, features="html.parser")

    scraped_urls = []
    counter = 0

    # Filters out invalid urls
    for link in soup.find_all('a'):
        link_str = str(link.get('href'))
        if 'formula' in link_str or 'Formula' in link_str:
            if link_str.startswith('/url?q='):
                link_str = link_str[7:]
                print('MOD:', link_str)
            if '&' in link_str:
                i = link_str.find('&')
                link_str = link_str[:i]
            if link_str.startswith('http') and 'google' not in link_str:
                if counter < 50 and link_str not in scraped_urls:
                    counter += 1
                    scraped_urls.append(link_str)
    # Returns list
    return scraped_urls


# This function stores the first 20 good urls of the input list
def scrape_text(list_of_urls):
    counter = 0

    for url in list_of_urls:
        if counter > 19:
            break

        # Some older websites don't like when you ping them too much
        try:
            r = requests.get(url, timeout=20)
        except requests.exceptions.RequestException as e:
            continue

        soup = BeautifulSoup(r.text, 'html.parser')

        with open('data/raw_url_' + str(counter) + '.txt', 'w', encoding="utf-8") as f:
            # kill all script and style elements
            text = []
            for data in soup.find_all("p"):
                if text == [] and data.get_text() == '00':
                    break
                # write text to file
                text.append(data.get_text())

            # protects from blank websites
            if len(text) > 5:
                print(url)
                counter += 1
                f.write("".join(text))

            f.close()


# This function cleans up the raw text into something that is easier for the
# rest of the program to read
def clean_files():
    directory = os.fsencode('data')

    for index_file, file in enumerate(os.listdir(directory)):
        filename = os.fsdecode(file)

        if filename.startswith('raw_url') and filename.endswith(".txt"):
            with open('data/' + filename, 'r', encoding="utf-8") as f:
                raw_text = f.read()

                raw_text = raw_text.replace('\n', '')
                raw_text = raw_text.replace('\t', '')

                # some periods don't have spaces afterwards
                raw_text = re.sub(r'(?<=[.,])(?=[^\s])', r' ', raw_text)

                sent_tokens = sent_tokenize(raw_text)
                sent_tokens = [" ".join(token.split()) for token in sent_tokens]

                f.close()
            with open('data/url_tokenized_' + str(index_file) + '.txt', 'w', encoding="utf-8") as f:
                f.write('\n'.join(sent_tokens))
                f.close()
            continue
        else:
            continue


# This function returns the 40 most common terms in all of the websites
def get_most_common_terms():
    directory = os.fsencode('data')
    full_text = ''

    # Take all the text on all of the sites and store it to a string
    for index_file, file in enumerate(os.listdir(directory)):
        filename = os.fsdecode(file)

        if filename.startswith('url_tokenized') and filename.endswith(".txt"):
            with open('data/' + filename, 'r', encoding="utf-8") as f:
                full_text += f.read()

    # tokenize and some formatting
    tokens = word_tokenize(full_text)
    token_lemma = [WordNetLemmatizer().lemmatize(token) for token in tokens]
    token_lemma = [t.lower() for t in token_lemma if t not in stopwords.words('english')
                   and t not in string.punctuation and (t.isalpha() or t.isdigit()) and len(t) >= 3]

    # Create the dict
    all_counts = FreqDist(ngrams(token_lemma, 1))
    return all_counts.most_common(40)


# This function finds sentences that contain the 10 keywords that I picked from the
# previous function
def build_knowledge_base() -> dict:
    selected_words = ['car', 'formula', 'team', 'race', 'driver',
                      'season', 'lap', 'point', 'championship', 'safety']

    base = {key: [] for key in selected_words}

    directory = os.fsencode('data')
    for index_file, file in enumerate(os.listdir(directory)):
        filename = os.fsdecode(file)

        if filename.startswith('url_tokenized') and filename.endswith(".txt"):
            with open('data/' + filename, 'r', encoding="utf-8") as f:
                current_line = f.readlines()
                for line in current_line:
                    for current_term in selected_words:
                        if current_term in line:
                            base[current_term].append(line)
    return base


if __name__ == '__main__':
    starter_url = "https://en.wikipedia.org/wiki/Formula_One"

    urls = extract_urls(starter_url)

    scrape_text(urls)

    clean_files()

    freq_terms = get_most_common_terms()

    for term in freq_terms:
        print(term[0][0])

    knowledge_base = build_knowledge_base()

    with open('pickle_files/knowledge.pickle', 'wb') as handle:
        pickle.dump(knowledge_base, handle)
