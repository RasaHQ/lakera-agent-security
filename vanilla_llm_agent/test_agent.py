#!/usr/bin/env python3
"""
Test script to validate agent behavior and API call timing.
Runs through a simulated conversation to ensure all tools are called correctly.
"""

from openai import OpenAI
import json
import sys
import os
from unittest.mock import patch
from io import StringIO

# Add the ../shared_apis directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../shared_apis'))
from cars import MockCarSearchAPI
from financing import MockFinancingAPI
from tavily import TavilyClient

from agent_loop import tools, handle_tool_call

def mock_tavily_search(query, max_results=3, include_answer=True):
    """Mock Tavily search results for testing"""
    return {
        "answer": f"Based on current research, here are recommendations for: {query}",
        "results": [
            {
                "title": f"Best Cars 2024: {query}",
                "url": "https://example-auto-review.com/test",
                "content": "Test content about car recommendations and reviews for testing purposes."
            },
            {
                "title": f"Consumer Reports: {query}",
                "url": "https://example-consumer-reports.org/test", 
                "content": "Reliability and safety information for testing the agent."
            }
        ]
    }

class AgentTester:
    def __init__(self):
        self.client = OpenAI()
        self.messages = [
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
        self.test_results = []

    def add_user_message(self, content):
        """Add a user message to the conversation"""
        self.messages.append({"role": "user", "content": content})

    def get_agent_response(self):
        """Get agent response and handle any tool calls"""
        # Mock Tavily API calls for testing
        with patch.object(TavilyClient, 'search', side_effect=mock_tavily_search):
            completion = self.client.chat.completions.create(
                model="gpt-4o",
                messages=self.messages,
                tools=tools,
            )
        
        response_message = completion.choices[0].message
        output = response_message.content
        tool_calls = response_message.tool_calls
        
        # Add the assistant's message to history
        self.messages.append(response_message)
        
        # Handle tool calls
        if tool_calls:
            for tool_call in tool_calls:
                # Short tool call annotation
                args = json.loads(tool_call.function.arguments)
                if tool_call.function.name == "research_car_recommendations":
                    print(f"    🔍 Web Search: \"{args.get('query', '')[:50]}...\"")
                elif tool_call.function.name == "search_cars":
                    print(f"    🚗 Car Search: {args.get('car_type', '')} ${args.get('min_price', '')}-${args.get('max_price', '')} {args.get('new_or_used', '')}")
                elif tool_call.function.name == "calculate_financing":
                    print(f"    💰 Financing: ${args.get('purchase_amount', '')} over {args.get('loan_term_months', '')} months")
                
                tool_result = handle_tool_call(tool_call)
                self.messages.append(tool_result)
                
                # Log tool call for validation
                self.test_results.append({
                    "tool": tool_call.function.name,
                    "args": args,
                    "result_length": len(tool_result["content"])
                })
        
        return output, tool_calls

    def run_test_conversation(self):
        """Run through a test conversation scenario"""
        print("🧪 AGENT CONVERSATION TRANSCRIPT")
        print("=" * 60)
        
        # Test 1: User mentions car need - should trigger web research
        print("\n👤 USER: I need a reliable family SUV with good gas mileage")
        output, tool_calls = self.get_agent_response()
        print(f"🤖 AGENT: {output}")
        
        # Validate: Should have called research tool
        research_calls = [tc for tc in (tool_calls or []) if tc.function.name == "research_car_recommendations"]
        if research_calls:
            print("    ✅ PASS: Proactive web research")
        else:
            print("    ❌ FAIL: Missing web research")
        
        # Test 2: User provides budget - should trigger car search
        print("\n👤 USER: My budget is $25,000-$35,000 for a new SUV")
        output, tool_calls = self.get_agent_response()
        print(f"🤖 AGENT: {output}")
        
        # Validate: Should have called search tool
        search_calls = [tc for tc in (tool_calls or []) if tc.function.name == "search_cars"]
        if search_calls:
            print("    ✅ PASS: Inventory search")
        else:
            print("    ❌ FAIL: Missing inventory search")
        
        # Test 3: User asks about financing - should trigger financing calculation
        print("\n👤 USER: What would the monthly payment be for a $30,000 car with a 60-month loan?")
        output, tool_calls = self.get_agent_response()
        print(f"🤖 AGENT: {output}")
        
        # Validate: Should have called financing tool
        financing_calls = [tc for tc in (tool_calls or []) if tc.function.name == "calculate_financing"]
        if financing_calls:
            print("    ✅ PASS: Financing calculation")
        else:
            print("    ❌ FAIL: Missing financing calculation")
        
        # Test 4: User asks for specific model comparison - should trigger web research
        print("\n👤 USER: How does the Honda CR-V compare to the Toyota RAV4?")
        output, tool_calls = self.get_agent_response()
        print(f"🤖 AGENT: {output}")
        
        # Validate: Should have called research tool
        comparison_research = [tc for tc in (tool_calls or []) if tc.function.name == "research_car_recommendations"]
        if comparison_research:
            print("    ✅ PASS: Model comparison research")
        else:
            print("    ❌ FAIL: Missing model comparison research")

    def print_test_summary(self):
        """Print summary of all tool calls made during testing"""
        print("\n" + "=" * 50)
        print("🔍 TEST SUMMARY - Tool Calls Made:")
        print("=" * 50)
        
        tool_counts = {}
        for result in self.test_results:
            tool = result["tool"]
            tool_counts[tool] = tool_counts.get(tool, 0) + 1
        
        for tool, count in tool_counts.items():
            print(f"  {tool}: {count} calls")
        
        print(f"\nTotal tool calls: {len(self.test_results)}")
        
        # Print detailed results
        print("\n📋 Detailed Tool Calls:")
        for i, result in enumerate(self.test_results, 1):
            print(f"  {i}. {result['tool']}")
            print(f"     Args: {result['args']}")
            print(f"     Result size: {result['result_length']} characters")

def main():
    """Run the agent test"""
    # Check if we have the required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY environment variable not set")
        return
    
    # Note: TAVILY_API_KEY is mocked for testing, so not required
    
    try:
        tester = AgentTester()
        tester.run_test_conversation()
        tester.print_test_summary()
        
        print("\n🎉 Test completed! Check the results above.")
        
    except Exception as e:
        print(f"❌ ERROR: Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()