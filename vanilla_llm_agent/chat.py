#!/usr/bin/env python3
"""
Web chat interface for the car buying assistant.
Compatible with Rasa's chat widget using Socket.IO.
"""

import asyncio
import json
import sys
import os
import webbrowser
from datetime import datetime
from typing import Dict, Any
import socketio
from aiohttp import web, web_runner
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the ../shared_apis directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../shared_apis'))
from agent_loop import tools, handle_tool_call, SYSTEM_PROMPT
from openai import OpenAI

class ChatAgent:
    def __init__(self):
        # Check for API key before creating client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.client = OpenAI(api_key=api_key)
        self.conversations = {}  # Store conversations by session_id

    def get_conversation(self, session_id: str):
        """Get or create conversation for a session"""
        if session_id not in self.conversations:
            self.conversations[session_id] = [SYSTEM_PROMPT]
        return self.conversations[session_id]

    async def process_message(self, session_id: str, message: str):
        """Process a user message and return agent response"""
        messages = self.get_conversation(session_id)
        messages.append({"role": "user", "content": message})
        
        try:
            # Get LLM response
            completion = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                tools=tools,
                temperature=0.7
            )
            
            response_message = completion.choices[0].message
            messages.append(response_message)
            
            # Handle tool calls
            if response_message.tool_calls:
                for tool_call in response_message.tool_calls:
                    tool_result = handle_tool_call(tool_call)
                    messages.append(tool_result)
                
                # Get final response after tool execution
                completion = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    tools=tools,
                    temperature=0.7
                )
                
                final_response = completion.choices[0].message
                messages.append(final_response)
                return final_response.content or "I'm having trouble responding right now."
            
            return response_message.content or "I'm having trouble responding right now."
            
        except Exception as e:
            print(f"Error processing message: {e}")
            return "I'm sorry, I encountered an error processing your request. Please try again."

# Create Socket.IO server
sio = socketio.AsyncServer(
    cors_allowed_origins="*",
    logger=False,
    engineio_logger=False
)

# Chat agent will be created in main() after environment check
agent = None

@sio.event
async def connect(sid, environ):
    """Handle client connection"""
    print(f"Client {sid} connected")

@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    print(f"Client {sid} disconnected")
    # Clean up conversation
    if sid in agent.conversations:
        del agent.conversations[sid]

@sio.event
async def session_request(sid, data):
    """Handle Rasa widget session request"""
    print(f"Session request from {sid}: {data}")
    # Send back session confirmation
    await sio.emit('session_confirm', {
        'session_id': sid
    }, room=sid)
    
    # Send welcome message
    welcome_message = {
        'text': 'Hi! I can help you find and finance a car.',
        'data': {
            'sender_id': 'bot',
            'timestamp': datetime.now().isoformat()
        }
    }
    await sio.emit('bot_uttered', welcome_message, room=sid)

@sio.event
async def user_uttered(sid, data):
    """Handle user message from Rasa widget"""
    try:
        message = data.get('message', '')
        print(f"User message from {sid}: {message}")
        
        if not message.strip():
            return
        
        # Process the message with our agent
        response = await agent.process_message(sid, message)
        
        # Send response back in Rasa format
        bot_message = {
            'text': response,
            'data': {
                'sender_id': 'bot',
                'timestamp': datetime.now().isoformat()
            }
        }
        
        await sio.emit('bot_uttered', bot_message, room=sid)
        
    except Exception as e:
        print(f"Error handling user message: {e}")
        error_message = {
            'text': "I'm sorry, I encountered an error. Please try again.",
            'data': {
                'sender_id': 'bot',
                'timestamp': datetime.now().isoformat()
            }
        }
        await sio.emit('bot_uttered', error_message, room=sid)

async def create_app():
    """Create the web application"""
    app = web.Application()
    
    # Serve static files (index.html)
    async def serve_index(request):
        index_path = os.path.join(os.path.dirname(__file__), 'index.html')
        try:
            with open(index_path, 'r') as f:
                content = f.read()
            return web.Response(text=content, content_type='text/html')
        except FileNotFoundError:
            return web.Response(text="index.html not found", status=404)
    
    # REST endpoint for chat messages
    async def chat_message(request):
        """Handle REST API chat messages"""
        try:
            data = await request.json()
            message = data.get('message', '')
            session_id = data.get('session_id', 'rest-session')
            
            if not message.strip():
                return web.json_response({
                    'error': 'Message cannot be empty'
                }, status=400)
            
            # Process the message with our agent
            response = await agent.process_message(session_id, message)
            
            return web.json_response({
                'response': response,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            })
            
        except json.JSONDecodeError:
            return web.json_response({
                'error': 'Invalid JSON in request body'
            }, status=400)
        except Exception as e:
            print(f"Error in REST endpoint: {e}")
            return web.json_response({
                'error': 'Internal server error'
            }, status=500)
    
    # Add routes
    app.router.add_get('/', serve_index)
    app.router.add_get('/index.html', serve_index)
    app.router.add_post('/chat', chat_message)
    
    # Attach Socket.IO
    sio.attach(app, socketio_path='/socket.io/')
    
    return app

async def main():
    """Main function to start the chat server"""
    global agent
    
    # Check required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY environment variable not set")
        return
    
    if not os.getenv("TAVILY_API_KEY"):
        print("⚠️  WARNING: TAVILY_API_KEY not set, web research will fail")
    
    # Create the chat agent after environment check
    try:
        agent = ChatAgent()
    except ValueError as e:
        print(f"❌ ERROR: {e}")
        return
    
    # Create and start the web server
    app = await create_app()
    
    runner = web_runner.AppRunner(app)
    await runner.setup()
    
    # Get port from environment variable (for Render) or default to 5005
    port = int(os.getenv('PORT', 5005))
    
    site = web_runner.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    print("🚀 Car Assistant Chat Server Started!")
    print("=" * 50)
    print(f"🌐 Server running at: http://0.0.0.0:{port}")
    print(f"💬 Chat interface: http://0.0.0.0:{port}/")
    print(f"🔌 Socket.IO endpoint: http://0.0.0.0:{port}/socket.io/")
    print(f"🌐 REST API endpoint: POST http://0.0.0.0:{port}/chat")
    print()
    print("REST API Usage:")
    print('  curl -X POST http://localhost:' + str(port) + '/chat \\')
    print("    -H 'Content-Type: application/json' \\")
    print("    -d '{\"message\": \"I need help buying a car\", \"session_id\": \"my-session\"}'")
    print()
    
    # Only open browser in local development
    if os.getenv('PORT') is None:  # Local development
        print("Opening browser...")
        webbrowser.open(f'http://localhost:{port}/')
    else:  # Production deployment
        print("Running in production mode")
    
    try:
        # Keep the server running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down server...")
        await runner.cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped.")