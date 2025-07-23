# Rasa CALM Agent Implementation

This directory will contain the modern Rasa implementation using CALM (Conversational AI with Language Models) for the car buying assistant.

## Planned Features

The Rasa CALM agent will provide the same functionality as the vanilla LLM agent:

- **Car Inventory Search** - Find available cars by type, price, and condition
- **Financing Calculator** - Calculate loan payments for different terms
- **Web Research** - Real-time car reviews and recommendations  
- **Loan Qualification** - Check customer loan approval and terms

## Modern Rasa Architecture

This implementation will leverage:

### **CALM (Conversational AI with Language Models)**
- **LLM-native approach** - Uses language models for natural conversation
- **Business logic integration** - Structured workflows with LLM flexibility
- **Flow-based conversations** - Guided multi-turn interactions
- **Fallback handling** - Robust error recovery and clarification

### **Production Features**
- **Intent classification** - Structured understanding of user goals
- **Entity extraction** - Precise parameter extraction from natural language
- **Conversation analytics** - Built-in tracking and monitoring
- **Testing framework** - Comprehensive conversation testing tools
- **Deployment tools** - Production-ready containerization and scaling

## Shared Resources

Both implementations will use the same mock APIs from `../shared_apis/`:
- Car search API with realistic car database
- Financing calculation API  
- Customer profile API
- Loan qualification API
- Tavily web research integration

## Comparison Focus

This implementation will demonstrate how modern Rasa combines:
- **LLM flexibility** for natural language understanding
- **Structured business logic** for reliable, testable workflows
- **Enterprise tooling** for production deployment and monitoring