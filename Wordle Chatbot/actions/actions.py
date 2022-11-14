# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

import os
from pathlib import Path

import random
import time


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
   with open('actions\\Resources\\word_bank.txt') as topo_file:
      for line in topo_file:
         line = line.replace('\n', '')
         word_bank.append(line)
   return word_bank

class ActionPickRandomWord(Action):
       
   def name(self) -> Text:
      return "action_pick_random_word"

   def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:      
      word_bank = getWordBank()
      SlotSet("word_bank", word_bank)

      random.seed(time.time())
      target_word = word_bank[random.randint(0, len(word_bank))]
      dispatcher.utter_message(text="I picked the word {}".format(target_word))
      return [SlotSet("word_bank", word_bank), SlotSet("target", target_word)]

