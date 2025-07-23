# Vanilla Agent

A simple OpenAI function calling agent that helps users search for cars using a mock car search API.

## Features

- Interactive car search agent with natural conversation
- Mock car search API with realistic car data
- OpenAI function calling integration
- Classic agent loop implementation

## Setup

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Set up your OpenAI API key in `.env`:
   ```bash
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

Run the interactive car search agent:

```bash
source .env && uv run main.py
```

The agent can help you find cars by:
- Car type (sedan, compact SUV, EV, truck, hatchback)
- Price range
- New or used condition

Type 'quit' to exit the conversation.

## Files

- `main.py` - Main entry point for the agent
- `agent_loop.py` - Classic agent loop implementation
- `car_search.py` - Single-shot car search example (like hello.py)
- `hello.py` - Weather API function calling example
- `cars_api/` - Mock car search API
  - `cars.py` - MockCarSearchAPI class
  - `cars.json` - Car database with ~30 realistic entries

## Example Conversation

```
You: I'm looking for a used compact SUV under $25,000
Agent: I found a used compact SUV for you:
- Model: 2020 Audi Q3
- Price: $23,500
- Features: Quattro AWD, navigation system
- Location: Luxury Used Car Depot
```