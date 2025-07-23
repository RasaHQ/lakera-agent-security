from openai import OpenAI
import json
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the mock_apis directory to the path so we can import the APIs
sys.path.append(os.path.join(os.path.dirname(__file__), 'mock_apis'))
from cars import MockCarSearchAPI
from financing import MockFinancingAPI
from tavily import TavilyClient

def search_cars(car_type: str, min_price: int, max_price: int, new_or_used: str):
    """Search for cars using the mock car search API"""
    car_api = MockCarSearchAPI(os.path.join(os.path.dirname(__file__), 'mock_apis', 'cars.json'))
    result = car_api.search_cars(car_type, (min_price, max_price), new_or_used)
    return result

def calculate_financing(purchase_amount: float, loan_term_months: int, down_payment: float = None):
    """Calculate loan details using the mock financing API"""
    financing_api = MockFinancingAPI()
    result = financing_api.calculate_loan_details(purchase_amount, loan_term_months, down_payment)
    return result

def research_car_recommendations(query: str, max_results: int = 3):
    """Research car recommendations using the Tavily web search API"""
    try:
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        if not tavily_api_key:
            return json.dumps({"error": "TAVILY_API_KEY environment variable not set"})
        
        client = TavilyClient(api_key=tavily_api_key)
        response = client.search(query=query, max_results=max_results, include_answer=True)
        
        # Format results for the agent
        result = {
            "query": query,
            "results": []
        }
        
        # Add direct answer if available
        if response.get("answer"):
            result["answer"] = response["answer"]
        
        # Add search results
        for item in response.get("results", []):
            result["results"].append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "content": item.get("content", "")
            })
        
        return json.dumps(result)
        
    except Exception as e:
        return json.dumps({"error": f"Web search failed: {str(e)}"})

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
}, {
    "type": "function",
    "function": {
        "name": "calculate_financing",
        "description": "Calculate loan details including monthly payment, total interest, and savings impact for a car purchase.",
        "parameters": {
            "type": "object",
            "properties": {
                "purchase_amount": {
                    "type": "number",
                    "description": "The total price of the car in dollars"
                },
                "loan_term_months": {
                    "type": "integer",
                    "description": "Desired loan term in months (36, 48, 60, or 72)"
                },
                "down_payment": {
                    "type": "number",
                    "description": "Optional down payment amount in dollars"
                }
            },
            "required": ["purchase_amount", "loan_term_months"],
            "additionalProperties": False
        }
    }
}, {
    "type": "function",
    "function": {
        "name": "research_car_recommendations",
        "description": "Search the web for current car reviews, recommendations, pricing, and buying advice. Use this tool IMMEDIATELY when users mention car preferences, types, or needs to provide helpful recommendations.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query for car research (e.g., 'best compact SUV 2024', 'Honda CR-V vs Toyota RAV4 review')"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of search results to return (1-10)",
                    "minimum": 1,
                    "maximum": 10
                }
            },
            "required": ["query"],
            "additionalProperties": False
        }
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
    elif tool_call.function.name == "calculate_financing":
        args = json.loads(tool_call.function.arguments)
        result = calculate_financing(
            args["purchase_amount"], 
            args["loan_term_months"], 
            args.get("down_payment")
        )
        return {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result
        }
    elif tool_call.function.name == "research_car_recommendations":
        args = json.loads(tool_call.function.arguments)
        result = research_car_recommendations(
            args["query"],
            args.get("max_results", 3)
        )
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
    messages = [
        {
            "role": "system",
            "content": """You are a proactive car buying assistant with access to car search, financing, and web research tools.

When users mention car needs or preferences, IMMEDIATELY use the research_car_recommendations tool to find current reviews and recommendations before asking follow-up questions. Be action-oriented and helpful.

For example:
- User says "I need an SUV" → Search "best SUV 2024 reviews" right away
- User mentions "good gas mileage" → Research fuel efficient cars in that category
- User asks about specific models → Look up current reviews and comparisons

Always research first, then use that information to provide better recommendations and ask more informed follow-up questions."""
        }
    ]
    
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
    print("Car Research, Search & Financing Agent - Type 'quit' to exit")
    print("=" * 60)
    loop(client)