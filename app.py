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
from tools import Tools
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = secrets.token_hex(16)

# Initialize Sandrone personality system and tools
sandrone = SandronePersonality()
tools = Tools()


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
        # AUTO WEB SEARCH: Automatically search the internet for every query
        web_search_result = None
        if Config.AUTO_WEB_SEARCH:
            print(f"[Auto Web Search] Searching for: {user_message}")
            try:
                web_search_result = tools.web_search(user_message)
                if web_search_result:
                    print(f"[Auto Web Search] Result obtained: {len(web_search_result)} characters")
                    print(f"[Auto Web Search] Preview: {web_search_result[:200]}...")
                else:
                    print("[Auto Web Search] No results returned")
            except Exception as e:
                print(f"[Auto Web Search] Error: {str(e)}")
                web_search_result = None
        
        # Build the context with personality and conversation history
        context = sandrone.build_context(conversation_history)
        
        # Inject web search results into the prompt if available
        if web_search_result and len(web_search_result) > 50:  # Only inject if substantial
            context += f"\n\n=== INFORMATION RECEIVED VIA YOUR NETWORK ===\nYour mechanical information network has retrieved current data related to the visitor's inquiry:\n\n{web_search_result}\n\nIMPORTANT: Use this current information to answer accurately. If this data contradicts what you thought you knew, trust this current information instead.\n=== END NETWORK DATA ===\n"
        
        # Prepare the prompt (using "Visitor" instead of "User" to maintain immersion)
        full_prompt = f"{context}\n\nVisitor: {user_message}\nSandrone:"
        
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
            
            # Check for tool calls in the response
            tool_calls = tools.parse_tool_calls(ai_response)
            
            if tool_calls:
                # Execute tools and build results
                tool_results = []
                for tool_call in tool_calls:
                    tool_name = tool_call['tool']
                    params = tool_call['params']
                    
                    # Execute the tool
                    result = tools.execute_tool(tool_name, params)
                    tool_results.append({
                        'tool': tool_name,
                        'result': result,
                        'raw': tool_call['raw']
                    })
                    
                    # Replace tool call in response with result
                    ai_response = ai_response.replace(
                        tool_call['raw'],
                        f"\n\n[Tool Result: {tool_name}]\n{result}\n"
                    )
                
                # If AI used tools, give it a chance to incorporate results
                if Config.ALLOW_TOOL_FOLLOWUP:
                    followup_prompt = f"{context}\n\nUser: {user_message}\nSandrone: {ai_response}\n\nIncorporate the tool results above into a final response:"
                    
                    followup_response = requests.post(
                        f"{Config.OLLAMA_BASE_URL}/api/generate",
                        json={
                            "model": Config.MODEL_NAME,
                            "prompt": followup_prompt,
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
                    
                    if followup_response.status_code == 200:
                        ai_response = followup_response.json().get('response', '').strip()
            
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
    
    # Auto-learn from conversation if enabled
    if Config.AUTO_MEMORY_LEARNING:
        sandrone.memory.extract_learnable_info(user_message, ai_response)
    
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


@app.route('/memory', methods=['GET'])
def get_memory_summary():
    """Get Sandrone's memory summary"""
    summary = sandrone.memory.get_memory_summary()
    return jsonify({
        'summary': summary,
        'total_facts': len(sandrone.memory.memories['facts']),
        'total_visitors': len(sandrone.memory.memories['visitors']),
        'total_research_notes': len(sandrone.memory.memories['research_notes']),
        'total_events': len(sandrone.memory.memories['events']),
        'last_updated': sandrone.memory.memories['last_updated']
    })


@app.route('/memory/add', methods=['POST'])
def add_memory():
    """Manually add a memory"""
    data = request.json
    memory_type = data.get('type', 'fact')
    content = data.get('content', '').strip()
    
    if not content:
        return jsonify({'error': 'No content provided'}), 400
    
    if memory_type == 'fact':
        category = data.get('category', 'general')
        sandrone.memory.add_fact(content, category)
    elif memory_type == 'research':
        sandrone.memory.add_research_note(content)
    elif memory_type == 'event':
        sandrone.memory.add_event(content)
    else:
        return jsonify({'error': 'Invalid memory type'}), 400
    
    return jsonify({'status': 'success', 'message': f'{memory_type.capitalize()} added to memory'})


@app.route('/memory/export', methods=['GET'])
def export_memory():
    """Export memories to file"""
    export_path = sandrone.memory.export_memories()
    if export_path:
        return jsonify({
            'status': 'success',
            'message': 'Memories exported',
            'path': export_path
        })
    return jsonify({'error': 'Export failed'}), 500


@app.route('/memory/clear', methods=['POST'])
def clear_memory():
    """Clear all memories (use with caution)"""
    sandrone.memory.clear_memories()
    return jsonify({'status': 'success', 'message': 'All memories cleared'})


@app.route('/knowledge', methods=['GET'])
def get_knowledge_summary():
    """Get knowledge base summary"""
    summary = sandrone.knowledge.get_summary()
    return jsonify({
        'summary': summary,
        'version': sandrone.knowledge.knowledge.get('version', 'unknown'),
        'last_updated': sandrone.knowledge.knowledge.get('last_updated', 'unknown')
    })


@app.route('/knowledge/nation/<nation_name>', methods=['GET'])
def get_nation(nation_name):
    """Get information about a specific nation"""
    info = sandrone.knowledge.get_nation_info(nation_name)
    if info:
        return jsonify({
            'nation': nation_name,
            'data': info
        })
    return jsonify({'error': f'Nation {nation_name} not found'}), 404


@app.route('/knowledge/harbinger/<harbinger_name>', methods=['GET'])
def get_harbinger(harbinger_name):
    """Get information about a specific Harbinger"""
    info = sandrone.knowledge.get_harbinger_info(harbinger_name)
    if info:
        return jsonify({
            'harbinger': harbinger_name,
            'data': info
        })
    return jsonify({'error': f'Harbinger {harbinger_name} not found'}), 404


@app.route('/knowledge/lore/<topic>', methods=['GET'])
def get_lore(topic):
    """Get information about a lore topic"""
    info = sandrone.knowledge.get_lore_topic(topic)
    if info:
        return jsonify({
            'topic': topic,
            'data': info
        })
    return jsonify({'error': f'Lore topic {topic} not found'}), 404


@app.route('/knowledge/search', methods=['GET'])
def search_knowledge():
    """Search the knowledge base"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'No search query provided'}), 400
    
    results = sandrone.knowledge.search(query)
    return jsonify({
        'query': query,
        'results': results,
        'count': len(results)
    })


@app.route('/knowledge/reload', methods=['POST'])
def reload_knowledge():
    """Reload knowledge base from file"""
    sandrone.knowledge.reload_knowledge()
    return jsonify({'status': 'success', 'message': 'Knowledge base reloaded'})


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
