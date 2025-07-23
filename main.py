from openai import OpenAI
import sys
import os

# Add the cars_api directory to the path so we can import the MockCarSearchAPI
sys.path.append(os.path.join(os.path.dirname(__file__), 'cars_api'))

from agent_loop import loop

def main():
    client = OpenAI()
    print("Car Search Agent - Type 'quit' to exit")
    print("=" * 40)
    loop(client)

if __name__ == "__main__":
    main()
