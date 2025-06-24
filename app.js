class MLXController {
    constructor() {
        this.apiBase = 'http://localhost:8000';
        this.currentModel = null;
        this.isGenerating = false;
        this.stopSequences = [];
        this.conversationHistory = [];
        
        this.init();
    }
    
    async init() {
        await this.loadAvailableModels();
        await this.checkServerStatus();
        this.setupEventListeners();
        this.addDefaultStopSequences();
        this.updateAllParamValues();
    }
    
    setupEventListeners() {
        // Enter key to send message
        document.getElementById('user-input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                this.sendMessage();
            }
        });
        
        // Auto-resize textarea
        document.getElementById('user-input').addEventListener('input', (e) => {
            this.adjustTextareaHeight(e.target);
        });
    }
    
    adjustTextareaHeight(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }
    
    async checkServerStatus() {
        try {
            const response = await fetch(`${this.apiBase}/health`);
            const data = await response.json();
            
            if (data.status === 'healthy') {
                this.updateModelStatus(data.model_info);
            }
        } catch (error) {
            this.showSystemMessage('Server not available. Please start the MLX AI Controller.');
            this.updateConnectionStatus(false);
        }
    }
    
    async loadAvailableModels() {
        try {
            const response = await fetch(`${this.apiBase}/models`);
            const data = await response.json();
            
            const select = document.getElementById('model-select');
            select.innerHTML = '<option value="">Select a model...</option>';
            
            if (data.available_models && data.available_models.length > 0) {
                data.available_models.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model;
                    option.textContent = model;
                    select.appendChild(option);
                });
            }
            
            if (data.current_model) {
                select.value = data.current_model;
                this.currentModel = data.current_model;
            }
            
        } catch (error) {
            console.error('Error loading models:', error);
            this.showSystemMessage('Error loading available models. Make sure MLX AI Controller is running.');
        }
    }
    
    updateModelStatus(modelInfo) {
        const statusDot = document.getElementById('status-dot');
        const statusText = document.getElementById('model-status');
        
        if (modelInfo && modelInfo.loaded) {
            statusDot.classList.remove('disconnected');
            statusText.textContent = `Loaded: ${modelInfo.model_name}`;
            this.currentModel = modelInfo.model_name;
            this.updateConnectionStatus(true);
        } else {
            statusDot.classList.add('disconnected');
            statusText.textContent = 'No model loaded';
            this.currentModel = null;
            this.updateConnectionStatus(false);
        }
    }
    
    updateConnectionStatus(connected) {
        const sendBtn = document.getElementById('send-btn');
        sendBtn.disabled = !connected || this.isGenerating;
    }
    
    async loadModel() {
        const select = document.getElementById('model-select');
        const selectedModel = select.value;
        
        if (!selectedModel) {
            this.showSystemMessage('Please select a model to load.');
            return;
        }
        
        this.showSystemMessage(`Loading model: ${selectedModel}...`);
        
        try {
            const response = await fetch(`${this.apiBase}/models/load`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ model_path: selectedModel })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showSystemMessage(`✅ Model loaded successfully: ${selectedModel}`);
                this.currentModel = selectedModel;
                this.updateModelStatus({ loaded: true, model_name: selectedModel });
            } else {
                this.showSystemMessage(`❌ Failed to load model: ${data.error || 'Unknown error'}`);
            }
        } catch (error) {
            this.showSystemMessage(`❌ Error loading model: ${error.message}`);
        }
    }
    
    async unloadModel() {
        if (!this.currentModel) {
            this.showSystemMessage('No model currently loaded.');
            return;
        }
        
        try {
            const response = await fetch(`${this.apiBase}/models/unload`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showSystemMessage('Model unloaded successfully.');
                this.currentModel = null;
                this.updateModelStatus({ loaded: false });
            } else {
                this.showSystemMessage(`Failed to unload model: ${data.error || 'Unknown error'}`);
            }
        } catch (error) {
            this.showSystemMessage(`Error unloading model: ${error.message}`);
        }
    }
    
    showSystemMessage(message) {
        const messagesDiv = document.getElementById('messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message system';
        messageDiv.innerHTML = `<div class="message-content">${message}</div>`;
        messagesDiv.appendChild(messageDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
    
    showUserMessage(message) {
        const messagesDiv = document.getElementById('messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user';
        messageDiv.innerHTML = `<div class="message-content">${message}</div>`;
        messagesDiv.appendChild(messageDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
    
    showAssistantMessage(message) {
        const messagesDiv = document.getElementById('messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant';
        messageDiv.innerHTML = `<div class="message-content">${message}</div>`;
        messagesDiv.appendChild(messageDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
        return messageDiv;
    }
    
    async sendMessage() {
        const userInput = document.getElementById('user-input');
        const message = userInput.value.trim();
        
        if (!message) return;
        
        if (!this.currentModel) {
            this.showSystemMessage('Please load a model first.');
            return;
        }
        
        // Show user message
        this.showUserMessage(message);
        userInput.value = '';
        
        // Add to conversation history
        this.conversationHistory.push({ role: 'user', content: message });
        
        // Disable send button and show loading
        this.isGenerating = true;
        this.updateConnectionStatus(true);
        
        const sendBtn = document.getElementById('send-btn');
        const originalText = sendBtn.textContent;
        sendBtn.innerHTML = '<div class="loading"></div>Generating...';
        
        try {
            const parameters = this.getGenerationParameters();
            const requestData = {
                messages: this.conversationHistory,
                parameters: parameters
            };
            
            const response = await fetch(`${this.apiBase}/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            });
            
            if (response.ok) {
                const data = await response.json();
                const assistantMessage = data.response || data.text || 'No response received';
                
                // Show assistant message
                this.showAssistantMessage(assistantMessage);
                
                // Add to conversation history
                this.conversationHistory.push({ role: 'assistant', content: assistantMessage });
                
                // Show generation info if available
                if (data.generation_info) {
                    this.showGenerationInfo(data.generation_info);
                }
            } else {
                const errorData = await response.json().catch(() => ({}));
                this.showSystemMessage(`❌ Error: ${errorData.error || 'Failed to generate response'}`);
            }
        } catch (error) {
            this.showSystemMessage(`❌ Network error: ${error.message}`);
        }
        
        // Re-enable send button
        this.isGenerating = false;
        this.updateConnectionStatus(true);
        sendBtn.innerHTML = originalText;
    }
    
    getGenerationParameters() {
        return {
            temperature: parseFloat(document.getElementById('temperature').value),
            top_p: parseFloat(document.getElementById('top-p').value),
            top_k: parseInt(document.getElementById('top-k').value),
            max_length: parseInt(document.getElementById('max-length').value),
            frequency_penalty: parseFloat(document.getElementById('frequency-penalty').value),
            presence_penalty: parseFloat(document.getElementById('presence-penalty').value),
            repetition_penalty: parseFloat(document.getElementById('repetition-penalty').value),
            stop_sequences: this.stopSequences,
            stream: document.getElementById('stream-mode').checked
        };
    }
    
    showGenerationInfo(info) {
        const infoDiv = document.getElementById('generation-info');
        infoDiv.style.display = 'block';
        infoDiv.innerHTML = `
            <strong>Generation Info:</strong><br>
            Time: ${info.generation_time || 'N/A'}s<br>
            Tokens: ${info.tokens_generated || 'N/A'}<br>
            Speed: ${info.tokens_per_second || 'N/A'} tokens/s
        `;
    }
    
    updateAllParamValues() {
        this.updateParamValue('temperature');
        this.updateParamValue('top-p');
        this.updateParamValue('top-k');
        this.updateParamValue('max-length');
        this.updateParamValue('frequency-penalty');
        this.updateParamValue('presence-penalty');
        this.updateParamValue('repetition-penalty');
    }
    
    addDefaultStopSequences() {
        // Add some default stop sequences
        this.stopSequences = [];
    }
    
    addStopSequence() {
        const container = document.getElementById('stop-sequences');
        const div = document.createElement('div');
        div.className = 'stop-sequence-input';
        div.innerHTML = `
            <input type="text" placeholder="Enter stop sequence" onchange="mlxController.updateStopSequences()">
            <button type="button" class="remove-btn" onclick="this.parentElement.remove(); mlxController.updateStopSequences();">Remove</button>
        `;
        container.appendChild(div);
    }
    
    updateStopSequences() {
        const inputs = document.querySelectorAll('#stop-sequences input');
        this.stopSequences = Array.from(inputs)
            .map(input => input.value.trim())
            .filter(value => value.length > 0);
    }
}

// UI Helper Functions
function updateParamValue(paramName) {
    const input = document.getElementById(paramName);
    const valueSpan = document.getElementById(`${paramName}-value`);
    if (input && valueSpan) {
        const value = parseFloat(input.value);
        valueSpan.textContent = value.toFixed(2);
    }
}

function toggleSection(sectionId) {
    const section = document.getElementById(sectionId);
    const header = section.previousElementSibling;
    
    section.classList.toggle('collapsed');
    header.classList.toggle('collapsed');
}

// Wrapper functions for HTML onclick events
function loadModel() {
    mlxController.loadModel();
}

function unloadModel() {
    mlxController.unloadModel();
}

function sendMessage() {
    mlxController.sendMessage();
}

function addStopSequence() {
    mlxController.addStopSequence();
}

// Initialize the controller when page loads
let mlxController;
document.addEventListener('DOMContentLoaded', () => {
    mlxController = new MLXController();
});