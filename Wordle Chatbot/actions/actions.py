# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, AllSlotsReset, FollowupAction, ConversationPaused

import fileinput
import sys
import os
import random
import re
import time
import datetime
import traceback
import nltk
from nltk.corpus import wordnet as wn
from nltk import FreqDist


class Backgrounds:
      ok = '\33[42m'
      maybe = '\33[43m'
      wrong = '\33[41m'
      reset = '\033[0m'

def initialize_user_information(user_filename: str):
   name = os.getlogin()

   guess_history_filename = user_filename + '/guess_history.txt'.format(name)
   answer_history_filename = user_filename + '/answer_history.txt'.format(name)

   date_time = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M")

   with open(user_filename + '/data.txt', 'w') as data_file:
      data_file.write(user_filename + '\n')
      data_file.write('$guess_history_file=' + guess_history_filename + '\n')
      data_file.write('$answer_history_file=' + answer_history_filename + '\n')
      data_file.write('$system_user_name=' + name + '\n')
      data_file.write('$initial_login=' + date_time + '\n')
      data_file.write('$most_recent_login=' + date_time + '\n')
      data_file.write('$total_num_games=0\n')
      data_file.write('$total_num_wins=0\n')
      data_file.write('$correct_guess_1=0\n')
      data_file.write('$correct_guess_2=0\n')
      data_file.write('$correct_guess_3=0\n')
      data_file.write('$correct_guess_4=0\n')
      data_file.write('$correct_guess_5=0\n')
      data_file.write('$correct_guess_6=0\n')

   with open(guess_history_filename, 'w') as guess_file:
      guess_file.write('')
   with open(answer_history_filename, 'w') as answer_file:
      answer_file.write('')

def user_file_update_value(user_filename: str, target_variable:str, new_value:str):
   for line in fileinput.input(user_filename, inplace=1):
      if target_variable in line:
         pattern = line[line.index('=') + 1:]
         line = line.replace(pattern, new_value + '\n')
      sys.stdout.write(line)

def user_file_get_value(user_filename: str, target_variable:str):
   user_file = open(user_filename, 'r')
   for line in user_file.readlines():
      if target_variable in line:
         return line[line.index('=') + 1:].strip()
   user_file.close()
   return

def user_file_increment_value(user_filename: str, target_variable:str):
   for line in fileinput.input(user_filename, inplace=1):
      if target_variable in line:
         pattern = line[line.index('=') + 1:]
         new_value = str(int(pattern) + 1) + '\n'
         line = line.replace(pattern, new_value)
      sys.stdout.write(line)

def add_to_history_file(user_filename: str, new_word:str):
   with open(user_filename, 'a') as history_file:
      history_file.write(new_word + '\n')

class ActionGetUserName(Action):
   def name(self) -> Text:
      return "action_get_user_name"

   def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
      name = os.getlogin()
      user_file = "actions/Resources/Users/{}".format(name)
      if not os.path.exists(user_file):
         os.makedirs(user_file)
         initialize_user_information(user_file)
         user_file = user_file + '/data.txt'
         dispatcher.utter_message(text="Welcome to wordle!")
      else:
         user_file = user_file + '/data.txt'
         date_time = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M")
         user_file_update_value(user_file, 'most_recent_login', date_time)
         dispatcher.utter_message(text="Welcome back!")

      return [SlotSet("user_file", user_file)]


class ActionGetUserStats(Action):
   def name(self) -> Text:
      return "action_get_user_stats"
   
   def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
      user_file = tracker.get_slot("user_file")
      game_end = tracker.get_slot("game_end")
      if user_file == None:
         ActionGetUserName.run(self, dispatcher, tracker, domain)
         user_file = tracker.get_slot("user_file")
         name = os.getlogin()
         user_file = "actions/Resources/Users/{}/data.txt".format(name)

      dispatcher.utter_message(text="Fetching your stats...")

      try:
         total_games = int(user_file_get_value(user_file, "total_num_games"))
         if not game_end:
            total_games -= 1
         total_wins = int(user_file_get_value(user_file, "total_num_wins"))

         win_percentage = 0
         if not total_games == 0:
            win_percentage = int((total_wins/total_games)*100)

         correct_guesses = []
         for index in range(1, 7):
            value = user_file_get_value(user_file, "correct_guess_{}".format(index))
            if not value.isnumeric():
               continue
            for i in range(int(value)):
               correct_guesses.append(index)

         average_guess = 0
         if not total_wins == 0:
            average_guess = sum(correct_guesses)/total_wins
         most_common_words = self.getMostFrequentGuesses(user_file_get_value(user_file, "guess_history_file"))

         dispatcher.utter_message(text="Total number of games: {}".format(total_games))
         dispatcher.utter_message(text="Total number of wins: {}".format(total_wins))
         dispatcher.utter_message(text="You have a win percentage of: {}%".format(win_percentage))
         dispatcher.utter_message(text="Average number of guesses to win: {}".format(average_guess))
         dispatcher.utter_message(text="Your favorite words are: {}".format(' '.join(most_common_words)))
      
      except:
         traceback.print_exc()
         dispatcher.utter_message(text="Error reading user file")
      
      return [SlotSet("user_file", user_file)]

   def getMostFrequentGuesses(self, guess_filename: str) -> list:
      tokens = nltk.word_tokenize(open(guess_filename).read())
      fdist = FreqDist(tokens)
      return [word[0] for word in fdist.most_common(3)]
def getWordBank():
      word_bank = list()
      with open('actions/Resources/word_bank/word_bank.txt') as topo_file:
         for line in topo_file:
            line = line.replace('\n', '')
            word_bank.append(line)
      return word_bank

class ActionPickRandomWord(Action):
   def name(self) -> Text:
      return "action_pick_random_word"

   def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:      
      user_file = tracker.get_slot("user_file")
      word_bank = getWordBank()

      random.seed(time.time())
      target_word = word_bank[random.randint(0, len(word_bank))]      
      user_file_increment_value(user_file, "total_num_games")
      add_to_history_file(user_file_get_value(user_file, "answer_history_file"), target_word)

      return [SlotSet("target", target_word)]


class ActionMakeGuess(Action):
   def name(self) -> Text:
      return "action_make_guess"
   
   def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:      
      current_guess = tracker.get_slot("guess")
      current_board = tracker.get_slot("guess_list")
      target_word = tracker.get_slot("target")
      guess_num = tracker.get_slot("guess_num")
      user_file = tracker.get_slot("user_file")
      game_end = tracker.get_slot("game_end")

      if current_guess == None or target_word == None:
         return []
      
      if game_end:
         dispatcher.utter_message(text='You have already finished the current game.')
         dispatcher.utter_message(text='Would you like to play again?')
         return []

      if len(current_board) != 0 and current_guess == current_board[len(current_board)-1]:
         dispatcher.utter_message(text="I'm sorry, but that word is not in my word bank.")
         return []

      current_board += [current_guess]
      guess_num = len(current_board)

      self.print_board(dispatcher, current_board, target_word)
      
      add_to_history_file(user_file_get_value(user_file, "guess_history_file"), current_guess)
      
      if current_guess == target_word and not guess_num > 7:
         user_file_increment_value(user_file, 'correct_guess_' + str(guess_num))
         user_file_increment_value(user_file, 'total_num_wins')
         dispatcher.utter_message(text='Congrats! You found the word! Would you like to play again?')
         return[SlotSet("game_end", True), SlotSet("guess", None)]
      elif guess_num > 6:
         dispatcher.utter_message(text='You lost! The correct word was {}. Would you like to play again?'.format(target_word))
         return [SlotSet("guess_list", current_board), SlotSet("game_end", True), SlotSet("guess", None)]

      return [SlotSet("guess_list", current_board), SlotSet("guess", None), SlotSet("guess", None), SlotSet("has_target", True)]

   def print_board(self, dispatcher: CollectingDispatcher, guess_list, target):
      for word in guess_list:
         dispatcher.utter_message(text=self.evaluate_guess(word, target))
   
   def evaluate_guess(self, guess, target_word) -> str:
      currentLine = ""
      for index, letter in enumerate(guess):
         curr = ' ' + letter + ' '
         if letter == target_word[index]:
            currentLine += Backgrounds.ok + curr
         elif letter in target_word:
            currentLine += Backgrounds.maybe + curr
         else:
            currentLine += Backgrounds.wrong + curr
      return currentLine + Backgrounds.reset


class ActionCustomHello(Action):
   def name(self) -> Text:
      return "action_custom_hello"
   
   def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
      current_guess = tracker.get_slot("guess")
      
      if current_guess != None:
         match = re.search(r'^\w{5}$', current_guess)
         if match:
            return [FollowupAction('action_make_guess')]

      dispatcher.utter_message(response = "utter_greet")
      return []

class ActionCustomsStart(Action):
   def name(self) -> Text:
      return "action_custom_start"
   
   def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
      return [SlotSet("is_start", False), SlotSet("guess", None), SlotSet("has_target", True)]


class ActionResetWordle(Action):
   def name(self) -> Text:
      return "action_reset_wordle"
   
   def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
      user_file = tracker.get_slot("user_file")

      dispatcher.utter_message(text='I am resetting the wordle for you.')
      return [AllSlotsReset(), SlotSet("user_file", user_file), SlotSet("is_start", False), SlotSet("game_end", True)]

class ActionGameEnd(Action):
   def name(self) -> Text:
      return "action_custom_end"

   def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
      dispatcher.utter_message(text='Thank you for playing! Please come again soon.')
      return [ConversationPaused()]


class ActionResetGameStatus(Action):
   def name(self) -> Text:
      return "action_reset_game_end"
   
   def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
      return [SlotSet("game_end", None)]
      dispatcher.utter_message(text='Game has been reset. You are ready to begin guessing.')
      return [AllSlotsReset(), SlotSet("user_file", user_file), SlotSet("is_start", False), SlotSet("target_word", target_word), SlotSet("has_target", True)]

class ActionMakeGetPos(Action):
   def name(self) -> Text:
      return "action_get_POS"
   
   def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
      target_word = tracker.get_slot("target")
      pos = self.get_most_common_pos(target_word)

      if pos != '':
         dispatcher.utter_message(text='The most common part of speech of the target word is a(n) {}.'.format(pos))
      else:
         dispatcher.utter_message(text="I'm sorry, I can't seem to find the part of speech for this word.")

      return []

   def get_most_common_pos(self, word: str) -> str:
      pos_dict = {}
      for ss in wn.synsets(word):
         pos = ss.pos()
         if pos not in pos_dict:
            pos_dict[pos] = 1
         else:
            pos_dict[pos] += 1

      pos_list = sorted(pos_dict, key=pos_dict.get, reverse=True)
      if len(pos_list) != 0:
         pos = pos_list[0]
         if pos == 'n':
            pos = 'noun'
         elif pos == 'v':
            pos = 'verb'
         elif pos == 'a' or pos == 's':
            pos = 'adjective'
         elif pos == 'r':
            pos = 'adverb'
         else:
            pos = ''
      else:
         pos = ''

      return pos


class ActionSuggestWords(Action):
   correct_letters = [[], [".", ".", ".", ".", "."]]
   maybe_letters = []
   invalid_letters = [[], {0: [], 1: [], 2: [], 3: [], 4: []}]

   def name(self) -> Text:
      return "action_suggest_words"
   
   def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
      guess_list = tracker.get_slot("guess_list")
      target = tracker.get_slot("target")
      word_list = getWordBank()

      self.correct_letters = [[], [".", ".", ".", ".", "."]]
      self.maybe_letters = []
      self.invalid_letters = [[], {0: [], 1: [], 2: [], 3: [], 4: []}]

      suggested_words = self.get_current_wordle_answers(guess_list, target, word_list)

      dispatcher.utter_message(text='I suggest trying ' + suggested_words)
      return []

   def get_current_wordle_answers(self, list_of_guesses, target_word, current_word_list):
      self.assign_letters(list_of_guesses, target_word)

      validated_words = self.remove_invalid_words(current_word_list, self.correct_letters, self.maybe_letters, self.invalid_letters)

      if len(validated_words) > 5:
         validated_words = self.rank_words(validated_words)
         sugg = self.list_to_string(validated_words[:5])
      else:
         validated_words = self.rank_words(validated_words)
         sugg = self.list_to_string(validated_words)
      return(sugg)

   def assign_letters(self, input_guesses, current_target):
      for input_guess in input_guesses:
         for index, current_character in enumerate(input_guess):
            if current_character == current_target[index]:
                if current_character not in self.correct_letters[0]:
                    self.correct_letters[0] += current_character
                self.correct_letters[1][index] = current_character
                if current_character in self.maybe_letters:
                    self.maybe_letters.remove(current_character)
                if current_character in self.invalid_letters[0]:
                    self.invalid_letters[0].remove(current_character)
            elif current_character in current_target:
                if current_character not in self.maybe_letters:
                    self.maybe_letters += current_character
                self.invalid_letters[1][index] += current_character
                if current_character in self.invalid_letters[0]:
                    self.invalid_letters[0].remove(current_character)
            else:
                if current_character in self.invalid_letters[1][index]:
                    continue
                elif current_character in self.correct_letters[0]:
                    self.invalid_letters[1][index] += current_character
                elif current_character not in self.invalid_letters[0] and current_character not in self.maybe_letters:
                    self.invalid_letters[0] += current_character
                    self.invalid_letters[1][index] += current_character

   def remove_invalid_words(self, current_word_list, correct_letters, maybe_letters, invalid_letters) -> list:
      new_list = []
      for word in current_word_list:
         valid = True
         for index, letter in enumerate(word):
            if letter != correct_letters[1][index] and correct_letters[1][index] != ".":
               valid = False
               break
            elif letter in invalid_letters[0] or letter in invalid_letters[1][index]:
               valid = False
               break
         if not all(letter in word for letter in maybe_letters):
            valid = False
         if valid:
            new_list.append(word)
      return new_list

   def rank_words(self, validated_words) -> list:
      # Get letter frequency
      char_freq_list = list()
      for i in range(5):
         char_freq_list.append(FreqDist([letter for letter in ''.join([word[i] for word in validated_words])]))
      
      # Score the word  
      new_list = [[]]
      for w_index, w in enumerate(validated_words):
         score = 0
         used_characters = ''
         for index, ch in enumerate(w):
            score_modifier = 1 if ch not in used_characters and validated_words else 0.75
            used_characters += ch
            score = score + (char_freq_list[index].get(ch) / len(validated_words) * score_modifier)
         new_list.insert(w_index, [w, score])
      new_list.pop()

      # Return 5 most common
      return [word[0] for word in sorted(new_list, key=lambda x: x[1], reverse=True)[:5]]

   def list_to_string(self, words: list):
      res = ''
      num_words = min(len(words), 5)
      for word in words:
         res += word
         if num_words > 1:
            res += ', '
            num_words -= 1
            if num_words == 1:
               res += 'and '
      
      return res

