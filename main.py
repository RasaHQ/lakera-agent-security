from openai import OpenAI
import sys
import os

# Add the mock_apis directory to the path so we can import the APIs
sys.path.append(os.path.join(os.path.dirname(__file__), 'mock_apis'))

from agent_loop import loop

def main():
    client = OpenAI()
    print("Car Research, Search & Financing Agent - Type 'quit' to exit")
    print("=" * 40)
    loop(client)

if __name__ == "__main__":
    main()
