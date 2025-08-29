import json
import os # Import os module to handle file paths
import logging

logger = logging.getLogger(__name__)

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
        # If no specific path provided, try to find cars.json in common locations
        if data_file == 'cars.json':
            candidates = [
                'cars.json',  # Current directory
                os.path.join(os.path.dirname(__file__), 'cars.json'),  # Same dir as this file
                '/app/shared_apis/cars.json'  # Docker location
            ]
            
            for candidate in candidates:
                if os.path.exists(candidate):
                    data_file = candidate
                    break
        
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
        # If absolute path provided, use it directly
        if os.path.isabs(data_file):
            file_path = data_file
        else:
            # Try relative to current working directory first
            file_path = os.path.join(os.getcwd(), data_file)
        
        if not os.path.exists(file_path):
            logger.error(f"Car data file not found at {file_path}. Please ensure '{data_file}' is accessible.")
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
            car_model (str, optional): Specific car model to search for. Use the official/canonical model name
                (e.g., "Honda Civic", "Ford F-150", "Toyota Camry") rather than nicknames or abbreviations
                like "civic", "f150", or "camry". This ensures the best keyword matching with inventory data.
            exclude_keywords (str, optional): Space-separated keywords to exclude from search (e.g., "honda toyota civic").

        Returns:
            str: A JSON string containing details of the first matching car, or an error.
        """
        logger.debug(f"Mock Car Search API called with: type='{car_type}', price_range={price_range}, new_or_used='{new_or_used}', car_model='{car_model}', exclude_keywords='{exclude_keywords}'")

        min_price, max_price = price_range

        # Normalize car_model keywords if provided
        model_keywords = self._normalize_keywords(car_model) if car_model else set()
        
        # Normalize exclusion keywords if provided
        exclusion_keywords = self._normalize_keywords(exclude_keywords) if exclude_keywords else set()

        # Collect all matching cars with their keyword overlap scores
        candidate_cars = []
        
        for car in self.cars_data:
            # Normalize car type and new_or_used for robust matching
            car_type_lower = car['type'].lower()
            new_or_used_lower = car['new_or_used'].lower()
            
            # Check basic criteria first
            type_match = not car_type or car_type.lower() == "any" or car_type.lower() in car_type_lower
            condition_match = new_or_used.lower() == "any" or new_or_used.lower() == new_or_used_lower
            basic_match = (type_match and
                          condition_match and
                          min_price <= car['price'] < max_price)
            
            if not basic_match:
                continue
            
            # Check for exclusion keywords first
            car_model_keywords = self._normalize_keywords(car['model'])
            if exclusion_keywords and exclusion_keywords.intersection(car_model_keywords):
                continue  # Skip this car if it matches exclusion keywords
            
            # Calculate keyword overlap score
            overlap_score = 0
            if model_keywords and not ('any' in model_keywords):
                overlap_score = len(model_keywords.intersection(car_model_keywords))
                # Only include cars that have at least one keyword match
                if overlap_score == 0:
                    continue
            
            # Add car to candidates with its overlap score
            candidate_cars.append((car, overlap_score))
        
        # Find the car with the highest overlap score
        found_car = None
        if candidate_cars:
            # Sort by overlap score (descending), then by price (ascending) as tiebreaker
            candidate_cars.sort(key=lambda x: (-x[1], x[0]['price']))
            found_car = candidate_cars[0][0]

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
        logger.info("Creating a dummy cars.json for standalone test...")
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