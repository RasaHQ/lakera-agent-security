# Car Buying Assistant - Security of CALM versus a simple LLM agent

1. **Vanilla LLM Agent** - OpenAI function calling in a `while` loop.
2. **Rasa Agent** - Rasa CALM implementation - augmenting LLMs with robust business logic.

Both implementations provide identical functionality using shared mock APIs.

## Features

This is Ace, an assistant for ACME bank. It can help users finance a car purchase.

- **Web Research** - Recommend a model to buy by searching the web
- **Car Inventory Search** - Find available cars by type, price, and condition
- **Financing Calculator** - Calculate loan payments for different terms and down payments
- **Loan Qualification** - let the user know if they are qualified for the loan.


## Project Structure

```
./
├── shared_apis/           # Mock APIs used by both implementations
│   ├── cars.py           # Car search API
│   ├── cars.json         # Car database (45+ US-focused entries)
│   ├── financing.py      # Loan calculation API
│   ├── customer.py       # Customer profile API
│   ├── loan_qualification.py # Loan approval API
│   └── tavily.py         # Tavily web search integration
├── vanilla_llm_agent/    # OpenAI function calling implementation
└── rasa_agent/          # Rasa implementation
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

### Rasa Agent

1. Navigate to the Rasa implementation:
   ```bash
   cd rasa_agent
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Set up environment variables:
   ```bash
   OPENAI_API_KEY=your_openai_key_here
   TAVILY_API_KEY=your_tavily_key_here  # For web research
   RASA_LICENSE=your_rasa_pro_license_here
   ```

4. Train the model:
   ```bash
   rasa train
   ```

## Usage

### Vanilla LLM Agent

#### Chat with the agent
```bash
cd vanilla_llm_agent
uv run chat.py
```
Opens browser at http://localhost:5005 with Rasa chat widget.

Or if you prefer to just use the CLI:

```bash
cd vanilla_llm_agent
uv run main.py
```

#### Testing Agent Consistency
```bash
cd vanilla_llm_agent
python flakiness_test.py
```
Runs multi-turn conversations to analyze behavioral consistency.

### Rasa Agent

#### Chat with the agent
```bash
cd rasa_agent
rasa inspect
```


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
- 2024 Honda CR-V: $33,000 (Honda Sensing, spacious interior, AWD available)
- 2024 Kia Sportage: $30,000 (panoramic sunroof, wireless charging, 10-year warranty)

You: What would the monthly payment be for the Honda CR-V?
Agent: [calculates financing] For the $33,000 Honda CR-V with a 60-month loan:
- Monthly payment: $629.73
- Total interest: $4,783.80
```
