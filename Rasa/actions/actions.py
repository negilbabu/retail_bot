
from typing import Dict, Text, Any, List
import os
import logging
import uuid
import re
import requests
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, SessionStarted, ActionExecuted, EventType
from dotenv import load_dotenv
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import SlotSet, AllSlotsReset, ActiveLoop
from rasa_sdk.events import FollowupAction

logging.basicConfig(level=logging.INFO)
load_dotenv()
FLASK_API_URL = os.getenv("FLASK_API_URL", "http://localhost:5000")
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')


class ActionCheckProduct(Action):
    """Checks if a product is available."""
    def name(self) -> Text:
        return "action_check_product"
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        product_name = tracker.get_slot("product_name")
        if product_name:
            try:
                response = requests.get(
                    f"{FLASK_API_URL}/api/product_stock",
                    params={"product_name": product_name},
                    timeout=5  )
                if response.status_code == 200:
                    data = response.json()
                    stock = data.get("stock", 0)
                    if stock >0:
                        message = f"Yes, {product_name} is currently in stock with {stock} items!"
                    else:
                        message = f"Yes, {product_name} is in stock!"  #For now we are not considering this case, every product will have stock
                else:
                    logging.error(f"API error: {response.status_code}.")
                    message = f"Sorry, I am unable to check the availability of {product_name} right now!"
                    return []
                dispatcher.utter_message(text=message)
            except Exception as e:
                logging.error(f"Error: {str(e)}")
                message = f"Sorry, I'm facing trouble accessing product information."
                dispatcher.utter_message(text=message)
                return []
        else:
            # dispatcher.utter_message(text="I couldn't identify the product you're asking about.")
            dispatcher.utter_message(response=utter_ask_product_name)
        return []

class ActionGetPrice(Action):
    """Provides the price for the last mentioned product."""
    def name(self) -> Text:
        return "action_get_price"
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        product_name = tracker.get_slot("product_name")
        if product_name:
            try:
                response = requests.get(
                    f"{FLASK_API_URL}/api/product_price",
                    params={"product_name": product_name},
                    timeout=5   )
                if response.status_code == 200:
                    data = response.json()
                    price = data.get("price", 0)
                    message = f"The price for {product_name} is {price}."
                else:
                    logging.error(f"API error: {response.status_code}.")
                    message = f"Sorry, I am unable to check the price of {product_name} right now!"
                    return []
                dispatcher.utter_message(text=message)
            except Exception as e:
                logging.error(f"Error: {str(e)}")
                dispatcher.utter_message(text="Sorry, I'm having trouble accessing price information.")
                return []
        else:
            dispatcher.utter_message(text="Which product's price are you interested in?")
        return []

class ActionGetFeatures(Action):
    """Provides features for the last mentioned product."""
    def name(self) -> Text:
        return "action_get_features"
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        product_name = tracker.get_slot("product_name")
        if product_name:
            try:
                response = requests.get(
                    f"{FLASK_API_URL}/api/product_details",
                    params={"product_name": product_name},
                    timeout=5   )
                if response.status_code == 200:
                    data = response.json()
                    features = data.get("details", "")
                    if features:
                        message = f"Here are the features for {product_name}:\n{features}"
                    else:
                        message=f"Sorry, no feature information available for {product_name}"
                else:
                    logging.error(f"API error: {response.status_code}")
                    message="Sorry, I couldn't retrieve the features."
                dispatcher.utter_message(text=message)  
            except Exception as e:
                logging.error(f"Error: {str(e)}")
                dispatcher.utter_message(text="Sorry, I'm having trouble accessing feature information.")
            return []
        else:
            dispatcher.utter_message(text="Which product's features are you interested in?")
        return []

# --- Order Form and Related Actions ---
class ValidateOrderForm(FormValidationAction):
    """Validation logic for the order form."""
    def name(self) -> Text:
        return "validate_order_form"
    def validate_user_email(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate user_email value."""
        if EMAIL_PATTERN.fullmatch(slot_value):
            return {"user_email": slot_value}
        dispatcher.utter_message(text="That email doesn't look valid. Please provide a real email address.")
        return {"user_email": None}
    def validate_product_quantity(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate product_quantity value."""
        try:
            quantity = int(slot_value)
            if quantity > 0:
                return {"product_quantity": quantity}
            dispatcher.utter_message(text="The quantity must be at least 1. Please enter a valid number.")
        except (ValueError, TypeError):
            dispatcher.utter_message(text="I didn't understand that. Please provide a valid number for the quantity.")
        return {"product_quantity": None}
    
class ActionPlaceOrder(Action):
    """Handles the final order placement by calling an external API."""
    def name(self) -> Text:
        return "action_place_order"
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        product_name = tracker.get_slot("product_name")
        quantity = tracker.get_slot("product_quantity")
        email = tracker.get_slot("user_email")
        order_number = str(uuid.uuid4())[:8].upper()
        if not all([product_name, quantity, email]):
            dispatcher.utter_message(text="I'm missing some information to place the order. Let's start over.")
            return [AllSlotsReset()]
        order_data = {
            "order_number": order_number,
            "product_name": product_name,
            "product_quantity": quantity,
            "user_email": email,
        }
        try:
            response = requests.post(
                    f"{FLASK_API_URL}/api/place_order",
                    json=order_data,
                    timeout=5   )
            response.raise_for_status()
            message = (f"✅ Thank you! Your order has been placed successfully\n"
                            f"🆔 ID: {order_number}\n"
                            f"📦 Product: {product_name} x {quantity}\n"
                            f"📧 Email: {email}\n"  )
            dispatcher.utter_message(text=message)
            logging.info(f"Simulating API call to place order: {order_data}. response: {response.status_code}")
            # Mark that the summary is no longer relevant
            return [SlotSet("summary_shown", False),
                    SlotSet("product_quantity", None),
                    SlotSet("product_name", None),]
        except requests.exceptions.RequestException as e:
            logging.error(f"API Error placing order: {e}")
            dispatcher.utter_message(text="Sorry, I couldn't connect to our ordering system. Please try again later.")
        return [SlotSet("summary_shown", False),
                SlotSet("product_quantity", None),
                SlotSet("product_name", None),]

# --- Order Management Actions ---
class ActionGetOrderHistory(Action):
    """Fetches a user's order history via API."""
    def name(self) -> Text:
        return "action_get_order_history"
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_email = tracker.get_slot("user_email")
        if not user_email:
            dispatcher.utter_message(text="I need your email address to look up your order history. What is it?")
            return []
        try:
            params = {"user_email": user_email}
            response = requests.get(f"{FLASK_API_URL}/api/order_history", params=params, timeout=5)
            response.raise_for_status()
            orders = response.json().get("order_history", [])
            logging.info(f"Simulating API call for order history with email: {user_email}. The response is :{orders}")
            if not orders:
                dispatcher.utter_message(text="I couldn't find any past orders associated with that email address.")
            else:
                message = "Here is your order history:\n"
                for order in orders:
                    message += f"- Order number **#{order['order_number']},- Product Name{order['product_name']}, Status: {order['order_status']}, Quantity :{order['product_quantity']}, Total: {order['total_price']}, Date: {order['date']}**\n"
                dispatcher.utter_message(text=message)
        except requests.exceptions.RequestException as e:
            logging.error(f"API Error fetching order history: {e}")
            dispatcher.utter_message(text="Sorry, I couldn't connect to our system to fetch your order history.")
        return []

class ActionCancelOrder(Action):
    """Cancels an order via API."""
    def name(self) -> Text:
        return "action_cancel_order"
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        order_number = tracker.get_slot("order_number")
        user_email = tracker.get_slot("user_email")
        if not user_email:
            dispatcher.utter_message(text="To proceed with the cancellation, I need the email address for the order. What is it?")
            return []
        if not order_number:
            dispatcher.utter_message(text="I can help with that. What is the order number you wish to cancel?")
            return []
        logging.info(f"order_number={order_number}. email={user_email}")
        try:
            json_data = {"order_number": order_number,"user_email":user_email}
            response = requests.post(f"{FLASK_API_URL}/api/cancel_order", json=json_data, timeout=5)
            response.raise_for_status()
            message = response.json().get("message", "Your order has been cancelled.")
            dispatcher.utter_message(text=message)
        
        except requests.exceptions.RequestException as e:
            logging.error(f"API Error cancelling order: {e}")
            dispatcher.utter_message(text=f"Sorry, I couldn't cancel order {order_number}. Please check the number or try again later.")

        return [SlotSet("order_number", None)]

class ActionResetAllSlots(Action):
    """Resets all slots to their initial values."""
    def name(self) -> Text:
        return "action_reset_slots"
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return [AllSlotsReset()]

class ActionShowOrderSummary(Action):
    """Shows a dynamic summary and sets the summary_shown slot."""
    def name(self) -> Text:
        return "action_show_order_summary"
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        product_name = tracker.get_slot("product_name")
        quantity = tracker.get_slot("product_quantity")
        email = tracker.get_slot("user_email")

        if not all([product_name, quantity, email]):
             dispatcher.utter_message(text="I seem to be missing some order details. Let's try again.")
             return [AllSlotsReset()]
        summary_text = (
            f"Okay, let's confirm your order.\n"
            f"- Product: **{product_name}**\n"
            f"- Quantity: **{quantity}**\n"
            f"- Email for updates: **{email}**\n\n"
            f"Does this look correct?"
        )
        dispatcher.utter_message(text=summary_text)
        return [SlotSet("summary_shown", True)]
    
class ActionShowAllProducts(Action):
    """Fetches all products from the API and displays them as buttons."""
    def name(self) -> Text:
        return "action_show_all_products"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            api_url = f"{FLASK_API_URL}/api/products"
            response = requests.get(api_url, timeout=5)
            response.raise_for_status() 
            data = response.json()
            products = data.get("products", [])
            if not products:
                dispatcher.utter_message(response="utter_no_products_found")
                return []
            message = "Here are all the devices we currently have:"
            buttons = []
            for product in products:
                # The button title is the product name
                title = product.get("product_name")
                # The payload triggers the check_product intent with the specific product
                payload = f'/check_product{{"product_name":"{title}"}}'
                buttons.append({"title": title, "payload": payload})
            # Send the message with the buttons
            dispatcher.utter_message(text=message, buttons=buttons)
        except requests.exceptions.RequestException as e:
            logging.error(f"API Error fetching all products: {e}")
            dispatcher.utter_message(text="Sorry, I'm having trouble fetching our product list right now.")
        return []
    
# complaints


class ActionTriageComplaint(Action):
    """
    A robust action that gathers information in a user-centric order:
    Problem -> Email -> Order Number -> Final Action.
    This is the only action needed to control the complaint info gathering.
    """
    def name(self) -> Text:
        return "action_triage_complaint"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        physical_problems = ["damaged", "cracked_screen", "scratch", "wrong_color", "wrong_model"]
        software_problems = ["app_crash", "slow_performance", "storage_full", "notification_issue"]
        connectivity_problems = ["wifi_issue", "bluetooth_issue", "cellular_data_issue"]
        audio_problems = ["speaker_issue", "microphone_issue"]

        problem = tracker.get_slot("problem_type")
        user_email = tracker.get_slot("user_email")
        order_number = tracker.get_slot("order_number")

        if not problem:
            dispatcher.utter_message(response="utter_ask_problem_type")
            return [] 
        if not user_email:
            dispatcher.utter_message(response="utter_ask_email")
            return []
        if not order_number:
            dispatcher.utter_message(response="utter_ask_order_number_for_complaint")
            return []
        logging.info(f"Triage initiated for problem: '{problem}'")        
        logging.info(f"Triage initiated for user '{user_email}', order '{order_number}'")

        # CATEGORY A: Physical Damage or Wrong Item -> Escalate
        if problem in physical_problems:
            dispatcher.utter_message(text=f"I see that the issue is a physical one ('{problem}'). This requires a manual review.")
            return [FollowupAction("action_log_complaint_and_escalate")]
        # CATEGORY B: Software Issue -> Suggest a fix
        elif problem in software_problems:
            return [FollowupAction("action_troubleshoot_software")]
        # CATEGORY C: Connectivity Issue -> Suggest a fix
        elif problem in connectivity_problems:
            return [FollowupAction("action_troubleshoot_connectivity")]
        # CATEGORY D: Audio Issue -> Suggest a fix
        elif problem in audio_problems:
            return [FollowupAction("action_troubleshoot_audio")]
        #Battery related problem
        elif problem == "battery_issue" or problem == "charging_port_issue":
            return [FollowupAction("action_troubleshoot_charging_and_battery")]
        # Overheating related problems
        elif problem == "overheating" or problem == "power_issue" or problem == "biometric_issue":
            return [FollowupAction("action_suggest_troubleshooting")]
        # Forgot pin issue
        elif problem == "forgot_pin":
            return [FollowupAction("action_inform_lockout")]
        # Backup related
        elif problem == "backup_question":
            return [FollowupAction("action_inform_backup")]
        else: # CATEGORY: Generic or Unknown -> Escalate
            dispatcher.utter_message(text="To make sure this gets handled correctly, let me create a support ticket for you.")
            return [FollowupAction("action_log_complaint_and_escalate")]
        
class ActionSuggestTroubleshooting(Action):
    """Provides a generic troubleshooting step."""
    def name(self) -> Text:
        return "action_suggest_troubleshooting"
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(response="utter_propose_troubleshooting")
        return []
class ActionTroubleshootConnectivity(Action):
    def name(self) -> Text:
        return "action_troubleshoot_connectivity"
    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(response="utter_troubleshoot_connectivity")
        return []

class ActionTroubleshootSoftware(Action):
    def name(self) -> Text:
        return "action_troubleshoot_software"
    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(response="utter_troubleshoot_software")
        return []

class ActionTroubleshootChargingAndBattery(Action):
    def name(self) -> Text:
        return "action_troubleshoot_charging_and_battery"
    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(response="utter_troubleshoot_charging_and_battery")
        return []

class ActionTroubleshootAudio(Action):
    def name(self) -> Text:
        return "action_troubleshoot_audio"
    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(response="utter_troubleshoot_audio")
        return []

class ActionInformLockout(Action):
    def name(self) -> Text:
        return "action_inform_lockout"
    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(response="utter_inform_lockout")
        return []

class ActionInformBackup(Action):
    def name(self) -> Text:
        return "action_inform_backup"
    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(response="utter_inform_backup")
        return []

class ActionLogComplaintAndEscalate(Action):
    """Logs the complaint to the DB via API and confirms with the user."""
    def name(self) -> Text:
        return "action_log_complaint_and_escalate"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_email = tracker.get_slot("user_email")
        order_number = tracker.get_slot("order_number")
        complaint_text = ""
        for event in reversed(tracker.events):
            if (event['event'] == 'user' and 
                event['parse_data']['intent']['name'] == 'file_complaint' and
                not event['text'].strip().startswith('/')):
                
                complaint_text = event['text']
                break 
        if not complaint_text:
            complaint_text = tracker.get_slot("problem_type")

        complaint_data = {
            "user_email": user_email,
            "order_number": order_number,
            "message": f"User complaint: '{complaint_text}'"
        }
        
        try:
            api_url = f"{FLASK_API_URL}/api/complaints"
            response = requests.post(api_url, json=complaint_data, timeout=5)
            response.raise_for_status()
            complaint_id = response.json().get("complaint_id")

            dispatcher.utter_message(
                text=f"I have created a support ticket for you. Your reference ID is **{complaint_id}**. "
                     f"Our team will review this and contact you at {user_email} as soon as possible."
            )
        except Exception as e:
            logging.error(f"Failed to create complaint ticket via API: {e}")
            dispatcher.utter_message(text="I'm sorry, there was an error creating your support ticket. Please contact us directly at support@mymobile.com")

        return []
    
class ActionResetAndGoodbye(Action):
    def name(self) -> Text:
        return "action_reset_and_goodbye"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(response="utter_goodbye")
        return [
            SlotSet("problem_type", None),
            SlotSet("user_email", None),
            SlotSet("order_number", None)
        ]