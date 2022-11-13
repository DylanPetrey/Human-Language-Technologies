# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import csv
from csv import writer 

class ActionGetUserName(Action):
   
   def name(self) -> Text:
      return "action_get_user_name"

   def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
      name= tracker.get_slot("name")
      
      msg = ""
      with open('data\\Resources\\user_info.csv', 'rt') as f:
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
      with open('data\\Resources\\user_info.csv', 'a', newline ='') as f_object:
         csv_writer  = writer(f_object)
         csv_writer.writerow(data)
         f_object.close()

