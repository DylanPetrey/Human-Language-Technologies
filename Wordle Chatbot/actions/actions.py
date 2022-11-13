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

import csv
from csv import writer 
import random
import time


class ActionGetUserName(Action):
    
   def name(self) -> Text:
      return "action_get_user_name"

   def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
      name= tracker.get_slot("name")
      
      msg = ""
      with open('actions\\Resources\\user_info.csv', 'rt') as f:
         reader = csv.reader(f, delimiter=',')
         for row in reader:
            if name == row[0]:
               msg= "Welcome back {}! Are you ready to play wordle?".format(name)
               dispatcher.utter_message(text=msg)
               return []

      self.initilize_user(name)
      msg="Hello {}! Would you like to play wordle?".format(name)
      dispatcher.utter_message(text=msg)

      return []

   def initilize_user(self, name: str):
      data = [name, '0', '0', '0', '0', '0', '0', '0']
      with open('actions\\Resources\\user_info.csv', 'a', newline ='') as f_object:
         csv_writer  = writer(f_object)
         csv_writer.writerow(data)
         f_object.close()


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
      SlotSet("target", target_word)
      dispatcher.utter_message(text="I picked the word {}".format(tracker.get_slot("target_word")))
      return []

