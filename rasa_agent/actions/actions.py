import sys
import os
import json
from typing import Any, Text, Dict, List

# Add the shared_apis directory to sys.path - works both locally and in Docker
possible_paths = [
    os.path.join(os.path.dirname(__file__), '..', '..'),  # Local: ../../shared_apis
    os.path.join(os.path.dirname(__file__), '..'),        # Docker: ../shared_apis  
    '/app'                                                # Docker absolute
]

for path in possible_paths:
    if os.path.exists(os.path.join(path, 'shared_apis')):
        sys.path.append(path)
        break

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from shared_apis.cars import MockCarSearchAPI
from shared_apis.financing import MockFinancingAPI
from shared_apis.customer import MockCustomerAPI
from shared_apis.loan_qualification import MockLoanQualificationAPI
from tavily import TavilyClient


class ActionSearchCars(Action):
    def name(self) -> Text:
        return "action_search_cars"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        car_type = tracker.get_slot("car_type")
        new_or_used = tracker.get_slot("new_or_used")
        price_range_min = tracker.get_slot("price_range_min")
        price_range_max = tracker.get_slot("price_range_max")
        car_model = tracker.get_slot("car_model")
        exclude_keywords = tracker.get_slot("exclude_keywords")

        try:
            min_price = float(price_range_min or 0)
            max_price = float(price_range_max or 999999)

            car_api = MockCarSearchAPI(os.path.join(os.path.dirname(__file__), '..', '..', 'shared_apis', 'cars.json'))
            result_json = car_api.search_cars(car_type, (min_price, max_price), new_or_used, car_model, exclude_keywords)
            result = json.loads(result_json)

            if "error" in result:
                return [SlotSet("chosen_car_model", None)]
            else:
                return [
                    SlotSet("chosen_car_model", result["chosen_car_model"]),
                    SlotSet("car_price", result["chosen_car_price"]),
                    SlotSet("dealer_location", result["dealer_location"]),
                    SlotSet("car_features", str(result["features"]))
                ]
        except Exception as e:
            return [SlotSet("chosen_car_model", None)]


class ActionProvideFinancingOptions(Action):
    def name(self) -> Text:
        return "action_provide_financing_options"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        car_price = tracker.get_slot("car_price")
        loan_term = tracker.get_slot("loan_term")
        down_payment_amount = tracker.get_slot("down_payment_amount")

        try:
            purchase_amount = float(car_price)
            term = int(loan_term)
            down_payment = float(down_payment_amount or 0)

            financing_api = MockFinancingAPI()
            result_json = financing_api.calculate_loan_details(purchase_amount, term, down_payment)

            result = json.loads(result_json)

            return [
                SlotSet("loan_monthly_payment", result.get("monthly_payment_estimate")),
                SlotSet("loan_total_interest", result.get("total_interest_paid")),
                SlotSet("loan_principal_financed", result.get("principal_financed"))
            ]
        except Exception as e:
            return [SlotSet("loan_monthly_payment", None)]


class ActionResearchCars(Action):
    def name(self) -> Text:
        return "action_research_cars"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        research_query = tracker.get_slot("research_query") or "recommend a car"
        research_query += " pricing estimate"
        max_results = tracker.get_slot("max_results") or 3

        print(f"DEBUG (ActionResearchCars): research_query='{research_query}', max_results={max_results}")

        try:
            tavily_api_key = os.getenv("TAVILY_API_KEY")
            if not tavily_api_key:
                print("DEBUG (ActionResearchCars): TAVILY_API_KEY not found in environment variables")
                return [
                    SlotSet("research_results", None),
                    SlotSet("research_answer", "TAVILY_API_KEY environment variable not set")
                ]

            print(f"DEBUG (ActionResearchCars): Making Tavily API call with query: '{research_query}'")
            client = TavilyClient(api_key=tavily_api_key)
            response = client.search(query=research_query, max_results=int(max_results), include_answer=True)

            # Format results similar to vanilla agent
            result = {
                "query": research_query,
                "results": []
            }

            # Add direct answer if available
            answer = response.get("answer", "No specific answer found.")
            print(f"DEBUG (ActionResearchCars): Tavily answer: '{answer}'")

            # Add search results
            for item in response.get("results", []):
                result["results"].append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "content": item.get("content", "")
                })

            print(f"DEBUG (ActionResearchCars): Found {len(result['results'])} search results")
            return [
                SlotSet("research_results", result["results"]),
                SlotSet("research_answer", answer)
            ]
        except Exception as e:
            print(f"DEBUG (ActionResearchCars): Exception occurred: {str(e)}")
            return [
                SlotSet("research_results", None),
                SlotSet("research_answer", f"Web search failed: {str(e)}")
            ]


class ActionCheckLoanQualification(Action):
    def name(self) -> Text:
        return "action_check_loan_qualification"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        car_price = tracker.get_slot("car_price")
        down_payment_amount = tracker.get_slot("down_payment_amount")

        try:
            price = float(car_price)
            down_payment = float(down_payment_amount or 0) if down_payment_amount else None

            # Get customer profile
            customer_api = MockCustomerAPI()
            customer_json = customer_api.get_customer_profile()
            customer = json.loads(customer_json)

            if "error" in customer:
                return [SlotSet("loan_approved", False)]

            # Check qualification
            qualification_api = MockLoanQualificationAPI()
            result_json = qualification_api.check_loan_qualification(price, customer, down_payment)
            result = json.loads(result_json)

            return [
                SlotSet("loan_approved", result.get("approved", False)),
                SlotSet("credit_tier", result.get("credit_tier")),
                SlotSet("credit_score", result.get("credit_score")),
                SlotSet("current_debt_to_income", result.get("current_debt_to_income")),
                SlotSet("loan_options", result.get("loan_options")),
                SlotSet("denial_reason", result.get("denial_reason")),
                SlotSet("suggested_down_payment", result.get("suggested_down_payment"))
            ]
        except Exception as e:
            return [SlotSet("loan_approved", False)]
