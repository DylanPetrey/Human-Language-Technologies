# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.events import AllSlotsReset

import fileinput
import sys
import os
import random
import time
import re
import datetime
from pathlib import Path

class Backgrounds:
      ok = '\33[42m'
      maybe = '\33[43m'
      wrong = '\33[41m'
      reset = '\033[0m'

def initilize_user_information(user_filename: str):
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
   user_file = open(user_filename)
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
         initilize_user_information(user_file)
         user_file = user_file + '/data.txt'
         dispatcher.utter_message(text="Welcome to wordle!")
      else:
         user_file = user_file + '/data.txt'
         date_time = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M")
         user_file_update_value(user_file, 'most_recent_login', date_time)
         dispatcher.utter_message(text="Welcome back! Lets play some wordle!")

      return [SlotSet("user_file", user_file)]


def getWordBank():
      word_bank = list()
      with open('actions/Resources/word_bank.txt') as topo_file:
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
      dispatcher.utter_message(text="I picked the word {}".format(target_word))
      
      user_file_increment_value(user_file, "total_num_games")
      add_to_history_file(user_file_get_value(user_file, "answer_history_file"), target_word)

      return [SlotSet("target", target_word)]


def evaluate_guess(guess, target_word) -> str:
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


def print_board(dispatcher: CollectingDispatcher, guess_list, target):
   for word in guess_list:
      dispatcher.utter_message(text=evaluate_guess(word, target))


class ActionMakeGuess(Action):
   def name(self) -> Text:
      return "action_make_guess"
      

   def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:      
      current_guess = tracker.get_slot("guess")
      current_board = tracker.get_slot("guess_list")
      target_word = tracker.get_slot("target")
      guess_num = tracker.get_slot("guess_num")
      user_file = tracker.get_slot("user_file")

      if current_guess == None:
         return []
      
      if len(current_board) != 0 and current_guess == current_board[len(current_board)-1]:
         dispatcher.utter_message(text='Im sorry, but that word is not in my word bank.')
         return []

      current_board += [current_guess]
      guess_num = len(current_board)
      print(guess_num)

      print_board(dispatcher, current_board, target_word)
      
      add_to_history_file(user_file_get_value(user_file, "guess_history_file"), current_guess)
      
      if current_guess == target_word and not guess_num > 6:
         user_file_increment_value(user_file, 'correct_guess_' + str(guess_num))
         user_file_increment_value(user_file, 'total_num_wins')
         dispatcher.utter_message(text='Congrats! You found the word! Would you like to play again?')
         return[SlotSet("game_end", True)]
      elif guess_num > 6:
         dispatcher.utter_message(text='You lost! Would you like to play again?')
         return [SlotSet("guess_list", current_board), SlotSet("game_end", True)]


      return [SlotSet("guess_list", current_board)]

class ActionMakeGuess(Action):
   def name(self) -> Text:
      return "action_reset_wordle"
      
   def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
      user_file = tracker.get_slot("user_file")

      dispatcher.utter_message(text='Resetting wordle')
      return [SlotSet("guess", None), SlotSet("target", None), SlotSet("guess_list", []), SlotSet("guess_num", 0)]

class ActionMakeGuess(Action):
   def name(self) -> Text:
      return "action_reset_game_end"
      
   def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
      return [SlotSet("game_end", None)]