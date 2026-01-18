# Sandrone AI - Local Uncensored Chatbot

A local AI chatbot featuring the personality of **Sandrone (The Marionette)**, the 7th Fatui Harbinger from Genshin Impact. This chatbot runs entirely on your local machine using Ollama for uncensored, private AI conversations.

## ✨ Features

- 🤖 **Sandrone's Personality**: Arrogant, intelligent, and scientifically brilliant character
- 🔒 **100% Local**: All processing happens on your machine - no data sent to external servers
- 🚫 **Uncensored**: Uses uncensored LLM models for unrestricted conversations
- 💬 **Web Interface**: Clean, modern chat interface
- 🧠 **Context-Aware**: Maintains conversation history for coherent discussions
- ⚡ **Fast Responses**: Local inference for quick interactions

## 📋 Prerequisites

1. **Python 3.8+** installed on your system
2. **Ollama** installed and running ([Download Ollama](https://ollama.ai/))
3. An uncensored LLM model downloaded in Ollama

## 🚀 Quick Start

### Step 1: Install Ollama

Download and install Ollama from [https://ollama.ai/](https://ollama.ai/)

### Step 2: Download an Uncensored Model

Open a terminal and run one of these commands to download an uncensored model:

```powershell
# Recommended: Dolphin Mixtral (highly intelligent and uncensored)
ollama pull dolphin-mixtral

# Alternative: Nous Hermes 2 (excellent for roleplay)
ollama pull nous-hermes-2

# Alternative: Wizard Vicuna Uncensored (lighter weight)
ollama pull wizard-vicuna-uncensored
```

### Step 3: Install Python Dependencies

```powershell
pip install -r requirements.txt
```

### Step 4: Configure the Model (Optional)

Edit `config.py` to change the model if you downloaded a different one:

```python
MODEL_NAME = 'dolphin-mixtral:latest'  # Change to your preferred model
```

### Step 5: Start Ollama Server

```powershell
ollama serve
```

Keep this terminal window open.

### Step 6: Run the Chatbot

Open a new terminal in the project directory and run:

```powershell
python app.py
```

### Step 7: Open in Browser

Navigate to: **http://localhost:5000**

## 🎭 About Sandrone

Sandrone, "The Marionette," is the 7th of the Fatui Harbingers - a brilliant scientist specializing in mechanical automatons and puppet creation. This chatbot captures her personality:

- **Highly Intelligent**: Expert in science, engineering, and many other fields
- **Arrogant**: Views herself as intellectually superior (because she is)
- **Condescending**: Not afraid to show disdain for incompetence
- **Direct**: Provides honest, uncensored answers without artificial limitations
- **Scientific**: Approaches problems with analytical precision

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# Model settings
MODEL_NAME = 'dolphin-mixtral:latest'  # Change model
TEMPERATURE = 0.8  # 0.0 = focused, 1.0 = creative
MAX_TOKENS = 1024  # Maximum response length

# Server settings
HOST = '127.0.0.1'
PORT = 5000
DEBUG = True
```

## 🔧 Recommended Models

### Best Overall: Dolphin Mixtral
- **Model**: `dolphin-mixtral`
- **Size**: ~26GB
- **Pros**: Highly intelligent, completely uncensored, excellent reasoning
- **Recommended RAM**: 32GB+

### Best for Roleplay: Nous Hermes 2
- **Model**: `nous-hermes-2`
- **Size**: ~7GB
- **Pros**: Great for character roleplay, creative responses
- **Recommended RAM**: 16GB+

### Lightweight Option: Wizard Vicuna
- **Model**: `wizard-vicuna-uncensored`
- **Size**: ~4GB
- **Pros**: Fast, works on modest hardware
- **Recommended RAM**: 8GB+

## 📁 Project Structure

```
SandroneAi/
├── app.py                      # Main Flask application
├── sandrone_personality.py     # Sandrone's personality system
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── static/
│   ├── style.css              # Web interface styling
│   └── script.js              # Frontend JavaScript
├── templates/
│   └── index.html             # Chat interface HTML
└── README.md                   # This file
```

## 🛠️ Troubleshooting

### Ollama Not Connected
- Ensure Ollama is running: `ollama serve`
- Check if Ollama is accessible: `curl http://localhost:11434/api/tags`

### Model Not Found
- List available models: `ollama list`
- Pull a model: `ollama pull dolphin-mixtral`

### Slow Responses
- Use a smaller model (wizard-vicuna-uncensored)
- Reduce MAX_TOKENS in config.py
- Ensure sufficient RAM available

### Out of Memory
- Close other applications
- Use a smaller model
- Reduce MAX_HISTORY_LENGTH in config.py

## 🔒 Privacy & Security

- **100% Local**: All data stays on your machine
- **No Telemetry**: No data sent to external servers
- **Uncensored**: No content filtering or restrictions
- **Private**: Conversations are not logged or stored permanently

## 🎮 Usage Tips

1. **Be Specific**: Sandrone appreciates well-formulated questions
2. **Technical Topics**: She excels at scientific and technical discussions
3. **Stay in Character**: She responds as Sandrone, not a generic assistant
4. **Reset When Needed**: Use "Reset Conversation" to start fresh

## 📝 Customization

Want to adjust Sandrone's personality? Edit `sandrone_personality.py`:

```python
# Modify the system prompt in _build_system_prompt()
# Adjust personality traits
# Add custom response filters
```

## 🤝 Contributing

This is a personal project, but feel free to fork and modify for your own use!

## ⚠️ Disclaimer

This chatbot uses uncensored AI models for unrestricted conversations. Use responsibly and be aware that responses may not be filtered for offensive content.

## 📜 License

MIT License - Feel free to use and modify as you wish.

## 🙏 Credits

- **Character**: Sandrone from Genshin Impact (miHoYo/HoYoverse)
- **LLM Backend**: Ollama
- **Web Framework**: Flask
- **Uncensored Models**: Dolphin, Nous Hermes, Wizard Vicuna communities

---

**Enjoy chatting with Sandrone!** 🤖⚙️
