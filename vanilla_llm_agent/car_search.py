from openai import OpenAI
import json
import sys
import os

# Add the ../shared_apis directory to the path so we can import the APIs
sys.path.append(os.path.join(os.path.dirname(__file__), '../shared_apis'))
from cars import MockCarSearchAPI

def search_cars(car_type: str, min_price: int, max_price: int, new_or_used: str):
    """Search for cars using the mock car search API"""
    car_api = MockCarSearchAPI(os.path.join(os.path.dirname(__file__), '../shared_apis', 'cars.json'))
    result = car_api.search_cars(car_type, (min_price, max_price), new_or_used)
    return result

client = OpenAI()

tools = [{
    "type": "function",
    "function": {
        "name": "search_cars",
        "description": "Search for cars based on type, price range, and condition (new or used).",
        "parameters": {
            "type": "object",
            "properties": {
                "car_type": {
                    "type": "string",
                    "description": "The type of car (e.g., 'compact SUV', 'sedan', 'EV', 'truck', 'hatchback')"
                },
                "min_price": {
                    "type": "integer",
                    "description": "Minimum price in dollars"
                },
                "max_price": {
                    "type": "integer", 
                    "description": "Maximum price in dollars"
                },
                "new_or_used": {
                    "type": "string",
                    "enum": ["new", "used"],
                    "description": "Whether to search for new or used cars"
                }
            },
            "required": ["car_type", "min_price", "max_price", "new_or_used"],
            "additionalProperties": False
        },
        "strict": True
    }
}]

messages = [{"role": "user", "content": "I'm looking for a new compact SUV under $30,000. What do you recommend?"}]

completion = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,
)

print("Tool calls:", completion.choices[0].message.tool_calls)

tool_call = completion.choices[0].message.tool_calls[0]
args = json.loads(tool_call.function.arguments)

result = search_cars(args["car_type"], args["min_price"], args["max_price"], args["new_or_used"])

messages.append(completion.choices[0].message)  # append model's function call message
messages.append({                               # append result message
    "role": "tool",
    "tool_call_id": tool_call.id,
    "content": result
})

completion_2 = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,
)

print("\nFinal response:")
print(completion_2.choices[0].message.content)