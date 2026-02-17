from typing import Any, Text, Dict, List, Optional
import re
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


def parse_number(value: Any) -> Optional[int]:
    """
    Converts any value the LLM might return into a clean integer.
    Returns None if unparseable.
    """
    if value is None:
        return None

    word_map = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
        'eleven': 11, 'twelve': 12, 'just me': 1, 'myself': 1,
        'alone': 1, 'solo': 1,
    }

    str_val = str(value).strip().lower()

    if str_val in word_map:
        return word_map[str_val]

    match = re.search(r'\d+', str_val)
    if match:
        return int(match.group())

    try:
        return int(float(str_val))
    except (ValueError, TypeError):
        return None


class ValidateNumGuests(Action):

    def name(self) -> Text:
        return "validate_num_guests"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        raw = tracker.get_slot("num_guests")

        # Slot not yet filled — do nothing, let Rasa ask the question
        if raw is None:
            return []

        guests = parse_number(raw)

        if guests is None:
            dispatcher.utter_message(
                text="I didn't catch the number of guests. Please enter a number, for example: 2"
            )
            return [SlotSet("num_guests", None)]

        if guests > 24:
            dispatcher.utter_message(
                text="We can only accommodate up to 24 guests. Please enter a smaller number."
            )
            return [SlotSet("num_guests", None)]

        return [SlotSet("num_guests", str(guests))]


class ValidateNumRooms(Action):

    def name(self) -> Text:
        return "validate_num_rooms"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        raw = tracker.get_slot("num_rooms")

        # Slot not yet filled — do nothing, let Rasa ask the question
        if raw is None:
            return []

        rooms = parse_number(raw)

        if rooms is None:
            dispatcher.utter_message(
                text="I didn't catch the number of rooms. Please enter a number, for example: 1"
            )
            return [SlotSet("num_rooms", None)]

        if rooms > 10:
            dispatcher.utter_message(
                text="We have a maximum of 10 rooms per booking. Please enter a number between 1 and 10."
            )
            return [SlotSet("num_rooms", None)]

        return [SlotSet("num_rooms", str(rooms))]


class ValidateConfirmBooking(Action):
    """
    Suppresses Rasa's built-in bool slot validation error for confirm_booking.
    When the slot is null (not yet answered), return silently.
    """

    def name(self) -> Text:
        return "validate_confirm_booking"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        raw = tracker.get_slot("confirm_booking")

        # Not yet answered — do nothing
        if raw is None:
            return []

        # Already a bool — pass through unchanged
        return [SlotSet("confirm_booking", raw)]


class ActionFormatNumbers(Action):
    """
    Final safety pass before the summary to ensure clean integer display.
    """

    def name(self) -> Text:
        return "action_format_numbers"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        events = []
        for slot in ["num_guests", "num_rooms"]:
            val = tracker.get_slot(slot)
            if val is not None:
                try:
                    events.append(SlotSet(slot, str(int(float(val)))))
                except (ValueError, TypeError):
                    pass
        return events


class ActionSessionEnd(Action):
    """
    Overrides Rasa Pro's built-in pattern_end_of_conversation to stay silent.
    """

    def name(self) -> Text:
        return "action_session_end"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        return []