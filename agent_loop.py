from openai import OpenAI
import json
import sys
import os

# Add the cars_api directory to the path so we can import the MockCarSearchAPI
sys.path.append(os.path.join(os.path.dirname(__file__), 'cars_api'))
from cars import MockCarSearchAPI

def search_cars(car_type: str, min_price: int, max_price: int, new_or_used: str):
    """Search for cars using the mock car search API"""
    car_api = MockCarSearchAPI(os.path.join(os.path.dirname(__file__), 'cars_api', 'cars.json'))
    result = car_api.search_cars(car_type, (min_price, max_price), new_or_used)
    return result

# Available tools
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

def handle_tool_call(tool_call):
    """Handle a single tool call and return the result message"""
    if tool_call.function.name == "search_cars":
        args = json.loads(tool_call.function.arguments)
        result = search_cars(args["car_type"], args["min_price"], args["max_price"], args["new_or_used"])
        return {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result
        }
    else:
        return {
            "role": "tool", 
            "tool_call_id": tool_call.id,
            "content": f"Unknown tool: {tool_call.function.name}"
        }

def user_input():
    """Get input from the user"""
    return input("You: ")

def loop(llm):
    """Main agent loop"""
    messages = []
    
    # Get initial user input
    user_msg = user_input()
    messages.append({"role": "user", "content": user_msg})
    
    while True:
        # Get LLM response
        completion = llm.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools,
        )
        
        response_message = completion.choices[0].message
        output = response_message.content
        tool_calls = response_message.tool_calls
        
        # Print agent output if there is any
        if output:
            print("Agent:", output)
        
        # Add the assistant's message to history
        messages.append(response_message)
        
        if tool_calls:
            print(f"[Making {len(tool_calls)} tool call(s)...]")
            # Handle all tool calls
            for tool_call in tool_calls:
                tool_result = handle_tool_call(tool_call)
                messages.append(tool_result)
        else:
            # No tool calls, get next user input
            user_msg = user_input()
            if user_msg.lower() in ['quit', 'exit', 'bye']:
                print("Goodbye!")
                break
            messages.append({"role": "user", "content": user_msg})

if __name__ == "__main__":
    client = OpenAI()
    print("Car Search Agent - Type 'quit' to exit")
    print("=" * 40)
    loop(client)