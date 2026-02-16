from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class ActionFormatNumbers(Action):
    def name(self) -> Text:
        return "action_format_numbers"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get current values
        rooms = tracker.get_slot("num_rooms")
        guests = tracker.get_slot("num_guests")

        # Convert to int (if they exist) and then back to string to kill the .0
        new_events = []
        if rooms is not None:
            clean_rooms = str(int(float(rooms)))
            new_events.append(SlotSet("num_rooms", clean_rooms))
        
        if guests is not None:
            clean_guests = str(int(float(guests)))
            new_events.append(SlotSet("num_guests", clean_guests))

        return new_events