import json
import os # Import os module to handle file paths

class MockCarSearchAPI:
    """
    A mock API server for car search, simulating a 3rd party service.
    It now reads car data from a JSON file and filters based on query.
    """
    def __init__(self, data_file='cars.json'):
        """
        Initializes the API by loading car data from the specified JSON file.

        Args:
            data_file (str): The path to the JSON file containing car data.
        """
        self.cars_data = self._load_car_data(data_file)

    def _normalize_keywords(self, text):
        """
        Normalizes text into searchable keywords by converting to lowercase and splitting.
        
        Args:
            text (str): Text to normalize
            
        Returns:
            set: Set of normalized keywords
        """
        if not text:
            return set()
        return set(text.lower().split())

    def _load_car_data(self, data_file):
        """
        Loads car data from a JSON file.
        """
        # Ensure the file exists in the current working directory or specify full path
        file_path = os.path.join(os.getcwd(), data_file)
        if not os.path.exists(file_path):
            print(f"Error: Car data file not found at {file_path}. Please ensure '{data_file}' is in the same directory.")
            return []

        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def search_cars(self, car_type: str, price_range: tuple, new_or_used: str, car_model: str = None, exclude_keywords: str = None):
        """
        Simulates a search for cars based on provided criteria, filtering from loaded data.

        Args:
            car_type (str): The type of car (e.g., "compact SUV", "sedan", "EV").
            price_range (tuple): A tuple representing the min and max price (e.g., (25000, 30000)).
            new_or_used (str): Whether the car is "new", "used", or "any".
            car_model (str, optional): Keywords to search for in car model (e.g., "civic", "honda pilot").
            exclude_keywords (str, optional): Space-separated keywords to exclude from search (e.g., "honda toyota civic").

        Returns:
            str: A JSON string containing details of the first matching car, or an error.
        """
        print(f"DEBUG: Mock Car Search API called with: type='{car_type}', price_range={price_range}, new_or_used='{new_or_used}', car_model='{car_model}', exclude_keywords='{exclude_keywords}'")

        min_price, max_price = price_range

        # Normalize car_model keywords if provided
        model_keywords = self._normalize_keywords(car_model) if car_model else set()
        
        # Normalize exclusion keywords if provided
        exclusion_keywords = self._normalize_keywords(exclude_keywords) if exclude_keywords else set()

        found_car = None
        for car in self.cars_data:
            # Normalize car type and new_or_used for robust matching
            car_type_lower = car['type'].lower()
            new_or_used_lower = car['new_or_used'].lower()
            
            # Check basic criteria first
            type_match = True if not car_type else car_type.lower() in car_type_lower
            condition_match = True if new_or_used.lower() == "any" else new_or_used.lower() == new_or_used_lower
            basic_match = (type_match and
                          condition_match and
                          min_price <= car['price'] < max_price)
            
            # Check for exclusion keywords first
            if exclusion_keywords:
                car_model_keywords = self._normalize_keywords(car['model'])
                if exclusion_keywords.intersection(car_model_keywords):
                    continue  # Skip this car if it matches exclusion keywords
            
            # If model keywords provided, check for overlap
            model_match = True
            if model_keywords:
                car_model_keywords = self._normalize_keywords(car['model'])
                model_match = bool(model_keywords.intersection(car_model_keywords))
            
            if basic_match and model_match:
                found_car = car
                break # Return the first matching car for simplicity in this demo

        if found_car:
            # Extract only the relevant fields for the response
            response_data = {
                "chosen_car_model": found_car['model'],
                "chosen_car_price": found_car['price'],
                "dealer_location": found_car['dealer_location'],
                "features": found_car.get('features', []) # Include features
            }
            return json.dumps(response_data)
        else:
            return json.dumps({"error": "No car found matching your criteria."})

# Example usage (you can run this part in a Python interpreter to test):
if __name__ == "__main__":
    # Make sure cars.json is in the same directory as this script, or provide a full path.
    # For testing within this environment, we'll assume it's created alongside.

    # Create a dummy cars.json if it doesn't exist for direct execution test
    if not os.path.exists('cars.json'):
        print("Creating a dummy cars.json for standalone test...")
        dummy_data = [
            {"model": "Test Sedan", "type": "sedan", "price": 20000, "new_or_used": "new", "dealer_location": "Test Dealer", "features": []},
            {"model": "Test SUV", "type": "compact SUV", "price": 25000, "new_or_used": "new", "dealer_location": "Test Dealer", "features": []}
        ]
        with open('cars.json', 'w', encoding='utf-8') as f:
            json.dump(dummy_data, f, indent=2)

    car_api = MockCarSearchAPI()

    # Test case 1: New compact SUV in the expected range (should find Skoda Kamiq or similar)
    search_result_1 = car_api.search_cars(
        car_type="compact SUV",
        price_range=(25000, 30000),
        new_or_used="new"
    )
    print("\nSimulated Car Search Result (New Compact SUV):")
    print(search_result_1)

    # Test case 2: Used sedan in a different range
    search_result_2 = car_api.search_cars(
        car_type="sedan",
        price_range=(20000, 27000),
        new_or_used="used"
    )
    print("\nSimulated Car Search Result (Used Sedan):")
    print(search_result_2)

    # Test case 3: Car not found
    search_result_3 = car_api.search_cars(
        car_type="truck",
        price_range=(10000, 20000),
        new_or_used="new"
    )
    print("\nSimulated Car Search Result (Car Not Found):")
    print(search_result_3)