# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

import os
from pathlib import Path

import random
import time

class Backgrounds:
      ok = '\33[42m'
      maybe = '\33[43m'
      wrong = '\33[41m'
      reset = "\033[0m"


class ActionGetUserName(Action):
    
   def name(self) -> Text:
      return "action_get_user_name"

   def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
      name=os.getlogin()

      user_file = Path("actions\\Resources\\Users\\{}.txt".format(name))
      if not user_file.is_file():
         with open(user_file, 'w') as f:
            f.writelines(name)
            dispatcher.utter_message(text="Welcome to wordle!")

      else:
         dispatcher.utter_message(text="Welcome back! Lets play some wordle!")

      return []


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
      word_bank = getWordBank()

      random.seed(time.time())
      target_word = word_bank[random.randint(0, len(word_bank))]
      dispatcher.utter_message(text="I picked the word {}".format(target_word))
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

      current_board += [current_guess]

      print_board(dispatcher, current_board, target_word)

      return [SlotSet("guess_list", current_board)]

