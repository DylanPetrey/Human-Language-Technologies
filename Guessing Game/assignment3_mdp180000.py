import nltk
import sys
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from random import seed
from random import randint


def preprocess_raw_text(text):
    # Lowercase the raw text
    text = text.lower()

    # tokenize the lowercase text
    tokens = word_tokenize(text)

    # Reduce tokens to those that are alpha, not in stopwords, and have length > 5
    tokens = [t.lower() for t in tokens if t.isalpha() and
               t not in stopwords.words('english') and len(t) > 5]

    # Lemmatize the tokens and make a list of unique lemmas
    wnl = WordNetLemmatizer()
    lemmas = [wnl.lemmatize(t) for t in tokens]
    lemmas_unique = list(set(lemmas))

    # POS tagging on the unique lemmas
    tags = nltk.pos_tag(lemmas_unique)

    # Print the first 20 tags
    print()
    print(tags[:20])

    # Create a list of the nouns
    noun_tokens = [t for t in tags if t[1][0] == 'N']

    # Print the  number of tokens and the number of nouns
    print('\nTokens:  ' + str(len(tokens)) + '\nNouns:  ' + str(len(noun_tokens)))

    # Return the tokens and the nouns
    return tokens, noun_tokens


def guessing_game(word_list):
    # Initialize game
    score = 5
    current_progress = ''
    print('\nLets play a guessing game!')

    target = word_list[randint(0, 49)]

    # Continuous loop for the game
    while score >= 0:
        # Print the current guessing progress
        for letter in target:
            if letter in current_progress:
                print(letter, end=' ')
                continue
            print('_', end=' ')
        print("\nCurrent Score:  " + str(score))

        # Check for game end or continue to next guess
        if len(set(target)) == len(current_progress):
            print('Congrats! You found the word!')
            print('Lets play a new game.\n')
            # Reset variables
            target = word_list[randint(0, 49)]
            current_progress = ''
            continue

        # Guess the next letter
        print('Guess a letter:  ', end=' ')
        guess = input()

        # guess validation
        while len(guess) != 1 or not (guess.isalpha() or guess == '!'):
            print('Please enter one letter A-Z.')
            print('Guess a letter:  ', end=' ')
            guess = input()

        # Check for forced game end
        if guess == '!':
            print('Ending game')
            break

        guess = guess.lower()

        # Process current guess
        if guess in target and guess not in current_progress:
            score += 1
            current_progress += guess
            print("Right!\n")
        else:
            score -= 1
            if score >= 0:
                print("Sorry, guess again!\n")
            else:
                print('Game Over!')
                print('The final word was: ' + target)


if __name__ == '__main__':
    if not len(sys.argv) > 1:
        print("There is no file location in the argument")
    else:
        # Preprocessing the text
        with open(str(sys.argv[1])) as input_file:
            # Read the input file and store into text
            raw_text = input_file.read()

            # Calculate the lexical diversity and output it
            raw_tokens = word_tokenize(raw_text)
            raw_token_set = set(raw_tokens)
            print("\nLexical diversity: %.2f" % (len(raw_token_set) / len(raw_tokens)))

            # Preprocess the text and get the tokens and the unique nouns
            tokens, nouns = preprocess_raw_text(raw_text)

            # Create a dictionary of the nouns and the number of nouns in tokens
            counts = {t[0]:tokens.count(t[0]) for t in nouns}

            # Get the 50 most common words and save them to a list for the guessing game
            sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
            word_game_list = [t[0] for t in sorted_counts][:50]
            print("\n50 most common words:")
            for i in range(50):
                print(sorted_counts[i])

            # Play the game
            guessing_game(word_game_list)
