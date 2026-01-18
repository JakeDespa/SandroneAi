"""
Configuration settings for Sandrone AI
"""

import os


class Config:
    """Application configuration"""
    
    # Flask settings
    HOST = '127.0.0.1'
    PORT = 5000
    DEBUG = True
    
    # Ollama settings
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    
    # Model settings - use an uncensored model for best results
    # Recommended models for 16GB RAM: 'nous-hermes-2', 'wizard-vicuna-uncensored', 'dolphin-phi'
    # For 32GB+ RAM: 'dolphin-mixtral'
    MODEL_NAME = os.getenv('MODEL_NAME', 'nous-hermes-2:latest')
    
    # Generation parameters
    TEMPERATURE = 0.8  # Higher = more creative, lower = more focused
    TOP_P = 0.9
    TOP_K = 40
    MAX_TOKENS = 1024
    
    # Conversation settings
    MAX_HISTORY_LENGTH = 20  # Number of message pairs to keep in context
    
    # Security
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
