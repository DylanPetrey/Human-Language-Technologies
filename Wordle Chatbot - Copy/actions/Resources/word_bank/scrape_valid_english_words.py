import requests
import time
from bs4 import BeautifulSoup
import enchant
import re
from urllib import request
from profanity import profanity
from nltk.corpus import wordnet as wn


links_list = set()
words = set()
d = enchant.Dict("en_US")
base_url = 'https://en.wikipedia.org'

# gets all valid english words
def process_link(target):
    try:
        response = request.urlopen(target)
        raw = response.read().decode('utf8')
    except:
        return
    tokens = re.findall(r'\b[a-zA-Z]{5}\b', raw)
    tokens = [w.lower() for w in tokens if d.check(w)]
    words.update(tokens)

# Recursive web crawler that goes over wikipedia articles for 3 minuets
def crawl(url):
    depth = 3  # 3 levels
    url_list_depth = [[] for i in range(0, depth + 1)]
    url_list_depth[0].append(url)
    for depth_i in range(0, depth):
        for links in url_list_depth[depth_i]:
            try:
                response = requests.get(links)
                soup = BeautifulSoup(response.text, 'html.parser')
                tags = soup.find_all('a', href=True)
                for link in tags:
                    if link['href'] != '#' and link['href'].strip() != '':
                        if link['href'] in links_list:
                            continue
                        url_new = base_url + link['href']
                        flag = False
                        for item in url_list_depth:
                            for l in item:
                                if url_new == l:
                                    flag = True

                        if url_new is not None and "https://en" in url_new and flag is False and '/wiki/' in url_new:
                            links_list.update(url_new)
                            url_list_depth[depth_i + 1].append(url_new)
                            process_link(url_new)
                            end = int(time.time() - start)
                            print(str(len(words)) + ' ' + str(end))
                            print(links, "->", url_new)
                            if time.time() - start > 20 * 60:
                                return
            except:
                break


def timer():
    now = time.localtime(time.time())
    return now[5]


def write_to_file(data):
    with open('actions/Resources/word_bank/word_bank.txt', 'w') as f:
        for w in data:
            f.write(w + '\n')


def build_knowledge_base():
    yaml = list()
    yaml.append('version: "3.1"\n')
    yaml.append('nlu:\n')
    yaml.append('  - lookup: valid_guess\n')
    yaml.append('    examples: |\n')

    with open('actions/Resources/word_bank/word_bank.txt', 'r') as word_bank_file:
        for word in word_bank_file:
            yaml.append('      - {}'.format(word))

    with open('data/lookups/valid_guess.yml', 'w') as yfile:
        yfile.write("".join(yaml))


def checkIfRomanNumeral(numeral):
    numeral = numeral.upper()
    validRomanNumerals = ["M", "D", "C", "L", "X", "V", "I", "(", ")"]
    valid = True
    for letters in numeral:
        if letters not in validRomanNumerals:
            return False
    for ss in wn.synsets(numeral):
        lem = ss.lemmas()[0].name()
        if '-' in lem or 'teen' in lem or lem.isdigit():
            valid = True
        else:
            valid = False
            break
        print(str(valid) + ' ' + numeral)
    return valid


def clean_words(w):
    tokens = [w.lower() for w in list(words) if d.check(w) and not profanity.contains_profanity(w) or not checkIfRomanNumeral(w)]
    tokens.sort() 
    print(len(tokens))
    return tokens


if __name__ == '__main__':
    starter_url = "https://en.wikipedia.org/wiki/Wordle"
    start = time.time()
    crawl(starter_url)
    write_to_file(clean_words(words))
    build_knowledge_base()
