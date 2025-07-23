# Rasa Agent Implementation

This directory will contain the Rasa-based implementation of the car buying assistant.

## Planned Features

The Rasa agent will provide the same functionality as the vanilla LLM agent:

- **Car Inventory Search** - Find available cars by type, price, and condition
- **Financing Calculator** - Calculate loan payments for different terms
- **Web Research** - Real-time car reviews and recommendations  
- **Loan Qualification** - Check customer loan approval and terms

## Shared Resources

Both implementations will use the same mock APIs from `../shared_apis/`:
- Car search API with realistic car database
- Financing calculation API  
- Customer profile API
- Loan qualification API
- Tavily web research integration

## Coming Soon

This implementation will be built to compare traditional rule-based conversational AI (Rasa) with the vanilla LLM function calling approach.