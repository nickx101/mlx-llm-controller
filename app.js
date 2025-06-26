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
        // Don't call updateAllParamValues here - will be called after global setup
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
                // Clear conversation history when new model is loaded
                this.conversationHistory = [];
                document.getElementById('messages').innerHTML = '';
                this.showSystemMessage('Conversation history cleared for new model.');
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
                // Clear conversation history when model is unloaded
                this.conversationHistory = [];
                document.getElementById('messages').innerHTML = '';
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
        // Empty method - parameter values are updated after global initialization
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
    console.log(`📊 updateParamValue called for: ${paramName}`);
    const input = document.getElementById(paramName);
    const valueSpan = document.getElementById(`${paramName}-value`);
    if (input && valueSpan) {
        const value = parseFloat(input.value);
        valueSpan.textContent = value.toFixed(2);
        console.log(`📊 Updated UI value: ${paramName} = ${value}`);
        
        // Sync parameter to backend for other applications
        console.log(`📊 About to sync to backend...`);
        syncParameterToBackend(paramName, value);
    } else {
        console.error(`❌ Could not find elements for ${paramName}`);
        console.log(`Input element:`, input);
        console.log(`Value span:`, valueSpan);
    }
}

async function syncParameterToBackend(paramName, value) {
    try {
        console.log(`🔄 syncParameterToBackend called with: ${paramName} = ${value}`);
        
        // Check if mlxController exists
        if (!window.mlxController) {
            console.error(`❌ mlxController not found!`);
            return;
        }
        
        console.log(`📡 mlxController.apiBase: ${window.mlxController.apiBase}`);
        
        // Map UI parameter names to backend names
        const paramMapping = {
            'temperature': 'temperature',
            'top-p': 'top_p',
            'top-k': 'top_k',
            'max-length': 'max_length',
            'repetition-penalty': 'repetition_penalty'
        };
        
        const backendParamName = paramMapping[paramName] || paramName;
        const paramData = {};
        paramData[backendParamName] = value;
        
        console.log(`🔄 Syncing ${paramName} -> ${backendParamName}: ${value}`);
        console.log(`📡 Sending to: ${window.mlxController.apiBase}/parameters`);
        console.log(`📦 Payload:`, paramData);
        
        const response = await fetch(`${window.mlxController.apiBase}/parameters`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(paramData)
        });
        
        if (response.ok) {
            console.log(`✅ Parameter ${backendParamName} synced successfully`);
            // Show visual feedback
            const valueSpan = document.getElementById(`${paramName}-value`);
            if (valueSpan) {
                valueSpan.style.color = '#48bb78';
                setTimeout(() => { valueSpan.style.color = ''; }, 1000);
            }
        } else {
            console.error('❌ Failed to sync parameter:', response.status);
        }
    } catch (error) {
        console.warn('Failed to sync parameter to backend:', error);
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

// Test function you can call manually in console
function testParameterSync() {
    console.log('🧪 Testing parameter sync manually...');
    updateParamValue('temperature');
}

// Initialize the controller when page loads
let mlxController;
document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 DOM loaded, initializing MLXController...');
    mlxController = new MLXController();
    window.mlxController = mlxController; // Make it globally accessible
    console.log('✅ MLXController initialized:', mlxController);
    
    // Wait for initialization to complete, then update param values
    setTimeout(() => {
        console.log('🔧 Updating all parameter values...');
        updateParamValue('temperature');
        updateParamValue('top-p');
        updateParamValue('top-k');
        updateParamValue('max-length');
        updateParamValue('frequency-penalty');
        updateParamValue('presence-penalty');
        updateParamValue('repetition-penalty');
    }, 100);
    
    // Test if updateParamValue function exists
    console.log('🔍 updateParamValue function:', typeof updateParamValue);
    
    // Test slider elements
    const tempSlider = document.getElementById('temperature');
    console.log('🎚️ Temperature slider found:', !!tempSlider);
    if (tempSlider) {
        console.log('🎚️ Temperature slider oninput:', tempSlider.oninput);
    }
});