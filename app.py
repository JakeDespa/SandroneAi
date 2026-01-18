"""
Sandrone AI - Local AI Chatbot with Sandrone's Personality
Main Flask application for the web interface
"""

from flask import Flask, render_template, request, jsonify, session
import requests
import json
from datetime import datetime
import secrets
from sandrone_personality import SandronePersonality
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = secrets.token_hex(16)

# Initialize Sandrone personality system
sandrone = SandronePersonality()


def check_ollama_connection():
    """Check if Ollama is running and accessible"""
    try:
        response = requests.get(f"{Config.OLLAMA_BASE_URL}/api/tags", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def generate_response(user_message, conversation_history):
    """Generate a response using Ollama with Sandrone's personality"""
    try:
        # Build the context with personality and conversation history
        context = sandrone.build_context(conversation_history)
        
        # Prepare the prompt
        full_prompt = f"{context}\n\nUser: {user_message}\nSandrone:"
        
        # Call Ollama API
        response = requests.post(
            f"{Config.OLLAMA_BASE_URL}/api/generate",
            json={
                "model": Config.MODEL_NAME,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": Config.TEMPERATURE,
                    "top_p": Config.TOP_P,
                    "top_k": Config.TOP_K,
                    "num_predict": Config.MAX_TOKENS
                }
            },
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get('response', '').strip()
            
            # Apply personality filter to ensure consistent character
            ai_response = sandrone.filter_response(ai_response)
            
            return ai_response
        else:
            return "My puppet systems are experiencing technical difficulties. How irritating."
            
    except Exception as e:
        print(f"Error generating response: {e}")
        return "It seems my mechanical systems need adjustment. Try again."


@app.route('/')
def index():
    """Render the main chat interface"""
    # Initialize session conversation history
    if 'conversation_history' not in session:
        session['conversation_history'] = []
    
    ollama_status = check_ollama_connection()
    return render_template('index.html', 
                         sandrone_name=sandrone.name,
                         ollama_status=ollama_status)


@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    data = request.json
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'error': 'Empty message'}), 400
    
    # Check Ollama connection
    if not check_ollama_connection():
        return jsonify({
            'error': 'Ollama is not running. Please start Ollama first.',
            'response': 'My systems cannot connect to the local LLM. Ensure Ollama is running.'
        }), 503
    
    # Get or initialize conversation history
    if 'conversation_history' not in session:
        session['conversation_history'] = []
    
    conversation_history = session['conversation_history']
    
    # Add user message to history
    conversation_history.append({
        'role': 'user',
        'content': user_message,
        'timestamp': datetime.now().isoformat()
    })
    
    # Generate AI response
    ai_response = generate_response(user_message, conversation_history)
    
    # Add AI response to history
    conversation_history.append({
        'role': 'assistant',
        'content': ai_response,
        'timestamp': datetime.now().isoformat()
    })
    
    # Keep only last N messages to prevent context overflow
    if len(conversation_history) > Config.MAX_HISTORY_LENGTH * 2:
        conversation_history = conversation_history[-(Config.MAX_HISTORY_LENGTH * 2):]
    
    session['conversation_history'] = conversation_history
    session.modified = True
    
    return jsonify({
        'response': ai_response,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/reset', methods=['POST'])
def reset():
    """Reset the conversation history"""
    session['conversation_history'] = []
    session.modified = True
    return jsonify({'status': 'success', 'message': 'Conversation reset'})


@app.route('/personality', methods=['GET'])
def get_personality():
    """Get Sandrone's personality information"""
    return jsonify(sandrone.get_personality_info())


@app.route('/status', methods=['GET'])
def status():
    """Check system status"""
    ollama_status = check_ollama_connection()
    return jsonify({
        'ollama_connected': ollama_status,
        'model': Config.MODEL_NAME,
        'personality': sandrone.name
    })


if __name__ == '__main__':
    print("=" * 60)
    print("🤖 Sandrone AI - Local Chatbot")
    print("=" * 60)
    print(f"Model: {Config.MODEL_NAME}")
    print(f"Personality: {sandrone.name}")
    print(f"Server: http://localhost:{Config.PORT}")
    
    # Check Ollama connection
    if check_ollama_connection():
        print("✓ Ollama connection: OK")
    else:
        print("✗ Ollama connection: FAILED")
        print("  Please start Ollama before using the chatbot:")
        print("  Run: ollama serve")
    
    print("=" * 60)
    print()
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
