# Car Buying Assistant - LLM vs Rasa Comparison

A comparison project between two different approaches to building conversational AI for car buying assistance:

1. **Vanilla LLM Agent** - OpenAI function calling with direct tool integration
2. **Rasa Agent** - Traditional rule-based conversational AI framework

Both implementations provide identical functionality using shared mock APIs.

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

## Project Structure

```
vanilla_agent/
├── shared_apis/           # Mock APIs used by both implementations
│   ├── cars.py           # Car search API
│   ├── cars.json         # Car database (~30 entries)  
│   ├── financing.py      # Loan calculation API
│   ├── customer.py       # Customer profile API
│   ├── loan_qualification.py # Loan approval API
│   └── tavily.py         # Tavily web search integration
├── vanilla_llm_agent/    # OpenAI function calling implementation
│   ├── main.py          # CLI entry point
│   ├── chat.py          # Web chat server
│   ├── agent_loop.py    # Core agent implementation
│   ├── flakiness_test.py # Multi-turn consistency testing
│   └── ...              # Other supporting files
└── rasa_agent/          # Rasa implementation (coming soon)
    └── README.md        # Planned Rasa implementation
```

## Setup

### Vanilla LLM Agent

1. Navigate to the vanilla implementation:
   ```bash
   cd vanilla_llm_agent
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Set up environment variables in `.env`:
   ```bash
   OPENAI_API_KEY=your_openai_key_here
   TAVILY_API_KEY=your_tavily_key_here  # For web research
   ```

## Usage

### Vanilla LLM Agent

#### CLI Interface
```bash
cd vanilla_llm_agent
uv run main.py
```

#### Web Chat Interface
```bash
cd vanilla_llm_agent
uv run chat.py
```
Opens browser at http://localhost:5005 with Rasa chat widget.

#### Testing Agent Consistency
```bash
cd vanilla_llm_agent
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

## Shared APIs

Both implementations use the same mock APIs to ensure fair comparison:

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

## Comparison Goals

This project aims to compare:

### **Vanilla LLM Agent Advantages:**
- **Natural language understanding** - Handles arbitrary user inputs
- **Context retention** - Maintains conversation state automatically  
- **Proactive behavior** - Can research and suggest without explicit commands
- **Flexibility** - Easy to add new capabilities via function calling

### **Rasa Agent Advantages:**
- **Predictable behavior** - Rule-based responses are consistent
- **Training data control** - Explicit intent/entity modeling
- **Enterprise features** - Built-in analytics, testing, deployment tools
- **Offline capability** - Can run without external LLM dependencies

### **Key Metrics:**
- **Consistency** - How often does the agent behave the same way?
- **Accuracy** - Does it call the right tools with correct parameters?
- **User Experience** - Which feels more natural to interact with?
- **Maintainability** - Which is easier to debug and extend?

## Development Notes

- **Flakiness Testing**: Use `flakiness_test.py` to measure behavioral consistency
- **Shared APIs**: Both implementations use identical backend services
- **Fair Comparison**: Same conversation scenarios tested on both agents