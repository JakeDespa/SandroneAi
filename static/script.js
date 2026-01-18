// Chat functionality
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const chatMessages = document.getElementById('chatMessages');
const resetButton = document.getElementById('resetButton');

// Auto-scroll to bottom of chat
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Add message to chat
function addMessage(content, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'assistant-message'}`;
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    const label = document.createElement('strong');
    label.textContent = isUser ? 'You:' : 'Sandrone:';
    
    const text = document.createElement('p');
    text.textContent = content;
    
    messageContent.appendChild(label);
    messageContent.appendChild(text);
    messageDiv.appendChild(messageContent);
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Add loading indicator
function addLoadingIndicator() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant-message';
    messageDiv.id = 'loadingIndicator';
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    const label = document.createElement('strong');
    label.textContent = 'Sandrone:';
    
    const loadingContainer = document.createElement('div');
    loadingContainer.style.display = 'flex';
    loadingContainer.style.gap = '5px';
    loadingContainer.style.padding = '5px 0';
    
    for (let i = 0; i < 3; i++) {
        const dot = document.createElement('span');
        dot.className = 'loading';
        loadingContainer.appendChild(dot);
    }
    
    messageContent.appendChild(label);
    messageContent.appendChild(loadingContainer);
    messageDiv.appendChild(messageContent);
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Remove loading indicator
function removeLoadingIndicator() {
    const indicator = document.getElementById('loadingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

// Send message
async function sendMessage(message) {
    if (!message.trim()) return;
    
    // Add user message to chat
    addMessage(message, true);
    
    // Clear input
    messageInput.value = '';
    
    // Show loading indicator
    addLoadingIndicator();
    
    // Disable input while processing
    messageInput.disabled = true;
    
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        });
        
        const data = await response.json();
        
        // Remove loading indicator
        removeLoadingIndicator();
        
        if (response.ok) {
            // Add AI response to chat
            addMessage(data.response, false);
        } else {
            // Show error message
            addMessage(data.error || 'An error occurred. Please try again.', false);
        }
    } catch (error) {
        removeLoadingIndicator();
        addMessage('Connection error. Please ensure the server is running.', false);
        console.error('Error:', error);
    } finally {
        // Re-enable input
        messageInput.disabled = false;
        messageInput.focus();
    }
}

// Reset conversation
async function resetConversation() {
    if (!confirm('Are you sure you want to reset the conversation?')) {
        return;
    }
    
    try {
        const response = await fetch('/reset', {
            method: 'POST'
        });
        
        if (response.ok) {
            // Clear chat messages
            chatMessages.innerHTML = '';
            
            // Add initial greeting
            addMessage('Hmph. Another visitor to waste my time. State your business.', false);
        }
    } catch (error) {
        console.error('Error resetting conversation:', error);
        alert('Failed to reset conversation');
    }
}

// Event listeners
chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const message = messageInput.value.trim();
    if (message) {
        sendMessage(message);
    }
});

resetButton.addEventListener('click', resetConversation);

// Focus input on load
messageInput.focus();

// Check status periodically
async function checkStatus() {
    try {
        const response = await fetch('/status');
        const data = await response.json();
        
        const statusDot = document.querySelector('.status-dot');
        const statusText = document.querySelector('.status-text');
        
        if (data.ollama_connected) {
            statusDot.className = 'status-dot status-online';
            statusText.textContent = 'Ollama Connected';
            messageInput.disabled = false;
            document.querySelector('.send-button').disabled = false;
        } else {
            statusDot.className = 'status-dot status-offline';
            statusText.textContent = 'Ollama Offline - Please start Ollama';
            messageInput.disabled = true;
            document.querySelector('.send-button').disabled = true;
        }
    } catch (error) {
        console.error('Status check failed:', error);
    }
}

// Check status every 10 seconds
setInterval(checkStatus, 10000);
