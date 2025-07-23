# Vanilla Agent

A comprehensive OpenAI function calling agent that helps users with car buying decisions through search, financing, and web research capabilities. Features both CLI and web chat interfaces.

## Features

### 🚗 Core Functionality
- **Car Inventory Search** - Find available cars by type, price, and condition
- **Financing Calculator** - Calculate loan payments for different terms and down payments
- **Web Research** - Real-time car reviews and recommendations via Tavily API
- **Proactive Agent** - Automatically researches when users mention car preferences

### 🖥️ Dual Interface
- **CLI Mode** - Terminal-based conversation (`uv run main.py`)
- **Web Mode** - Browser chat widget compatible with Rasa UI (`uv run chat.py`)

### 🧪 Testing & Analysis
- **Flakiness Testing** - Multi-turn conversation consistency analysis
- **Behavior Transcripts** - See exact agent decision points and variations

## Setup

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Set up environment variables in `.env`:
   ```bash
   OPENAI_API_KEY=your_openai_key_here
   TAVILY_API_KEY=your_tavily_key_here  # For web research
   ```

## Usage

### CLI Interface
```bash
uv run main.py
```

### Web Chat Interface
```bash
uv run chat.py
```
Opens browser at http://localhost:5005 with Rasa chat widget.

### Testing Agent Consistency
```bash
python flakiness_test.py
```
Runs multi-turn conversations to analyze behavioral consistency.

## Agent Capabilities

The agent can help with:

### 🔍 Car Search
- Type: sedan, compact SUV, EV, truck, hatchback
- Price range filtering
- New vs used vehicles
- Inventory of ~30 realistic car entries

### 💰 Financing
- Monthly payment calculations
- Loan terms: 36, 48, 60, 72 months
- Down payment scenarios
- Interest rate modeling

### 🌐 Web Research  
- Current car reviews and recommendations
- Model comparisons
- Market insights via Tavily search

## Project Structure

```
vanilla_agent/
├── main.py              # CLI entry point
├── chat.py              # Web chat server
├── agent_loop.py        # Core agent implementation
├── flakiness_test.py    # Multi-turn consistency testing
├── test_agent.py        # Basic functionality tests
├── index.html           # Chat widget interface
├── mock_apis/           # Mock API implementations
│   ├── cars.py          # Car search API
│   ├── cars.json        # Car database (~30 entries)
│   ├── financing.py     # Loan calculation API
│   └── tavily.py        # Tavily web search integration
├── car_search.py        # Single-shot example
├── hello.py             # Weather API example
└── socketio.py          # Rasa socketio channel (reference)
```

## Example Conversations

### Multi-turn car buying flow:
```
You: I need a reliable family SUV with good gas mileage
Agent: [researches best family SUVs automatically]
Based on current research, I found excellent options like the Honda CR-V for reliability 
and fuel economy, Toyota RAV4 for standard AWD...

You: My budget is $25,000-$35,000 for a new SUV  
Agent: [searches inventory] I found several SUVs in your range:
- 2025 Skoda Kamiq: $28,000 (panoramic sunroof, heated seats)
- 2024 Peugeot 2008: $29,500 (i-Cockpit, blind spot monitoring)

You: What would the monthly payment be for the Skoda?
Agent: [calculates financing] For the $28,000 Skoda Kamiq with a 60-month loan:
- Monthly payment: $534.73
- Total interest: $4,083.80
```

## Development Notes

- **Agent Consistency**: Use `flakiness_test.py` to measure behavioral consistency across identical scenarios
- **Tool Integration**: All APIs use the same OpenAI function calling pattern
- **Session Management**: Web interface maintains conversation context per user
- **Error Handling**: Graceful degradation when APIs are unavailable

## API Keys Required

- **OpenAI API Key**: Required for LLM functionality
- **Tavily API Key**: Optional, needed for web research features (agent works without it)