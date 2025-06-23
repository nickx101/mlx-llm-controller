class MLXController {
    constructor() {
        this.apiBase = 'http://127.0.0.1:8000';
        this.currentModel = null;
        this.isGenerating = false;
        this.stopSequences = [];
        
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
        document.getElementById('user-input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                this.sendMessage();
            }
        });
        
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
            this.showSystemMessage('Server not available. Please start the API server.');
            this.updateConnectionStatus(false);
        }
    }
    
    async loadAvailableModels() {
        try {
            const response = await fetch(`${this.apiBase}/models`);
            const data = await response.json();
            
            const select = document.getElementById('model-select');
            select.innerHTML = '<option value="">Select a model...</option>';
            
            data.available_models.forEach(model => {
                const option = document.createElement('option');
                option.value = model;
                option.textContent = model;
                select.appendChild(option);
            });
            
            if (data.current_model) {
                select.value = data.current_model;
                this.currentModel = data.current_model;
            }
            
        } catch (error) {
            console.error('Error loading models:', error);
            this.showSystemMessage('Error loading available models.');
        }
    }
    
    updateModelStatus(modelInfo) {
        const statusDot = document.getElementById('status-dot');
        const statusText = document.getElementById('model-status');
        
        if (modelInfo.loaded) {
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
            this.showSystemMessage('Please select a model first.');
            return;
        }
        
        this.showSystemMessage(`Loading model: ${selectedModel}...`);
        
        try {
            const response = await fetch(`${this.apiBase}/models/load`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    model_path: selectedModel
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showSystemMessage(`Model loaded successfully: ${selectedModel}`);
                this.updateModelStatus(data.model_info);
            } else {
                this.showSystemMessage(`Error loading model: ${data.error}`);
            }
            
        } catch (error) {
            console.error('Error loading model:', error);
            this.showSystemMessage('Error communicating with server.');
        }
    }
    
    async unloadModel() {
        try {
            const response = await fetch(`${this.apiBase}/models/unload`, {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showSystemMessage('Model unloaded successfully.');
                this.updateModelStatus({loaded: false});
            } else {
                this.showSystemMessage(`Error unloading model: ${data.error}`);
            }
            
        } catch (error) {
            console.error('Error unloading model:', error);
            this.showSystemMessage('Error communicating with server.');
        }
    }
    
    getGenerationParameters() {
        return {
            temperature: parseFloat(document.getElementById('temperature').value),
            top_p: parseFloat(document.getElementById('top-p').value),
            top_k: parseInt(document.getElementById('top-k').value) || 0,
            max_length: parseInt(document.getElementById('max-length').value),
            frequency_penalty: parseFloat(document.getElementById('frequency-penalty').value),
            presence_penalty: parseFloat(document.getElementById('presence-penalty').value),
            repetition_penalty: parseFloat(document.getElementById('repetition-penalty').value),
            stop_sequences: this.getStopSequences(),
            stream: document.getElementById('stream-mode').checked
        };
    }
    
    getStopSequences() {
        const inputs = document.querySelectorAll('.stop-sequence-input input');
        const sequences = [];
        inputs.forEach(input => {
            if (input.value.trim()) {
                sequences.push(input.value.trim());
            }
        });
        return sequences;
    }
    
    async sendMessage() {
        if (!this.currentModel) {
            this.showSystemMessage('Please load a model first.');
            return;
        }
        
        if (this.isGenerating) {
            return;
        }
        
        const userInput = document.getElementById('user-input');
        const message = userInput.value.trim();
        
        if (!message) {
            return;
        }
        
        this.addMessage('user', message);
        userInput.value = '';
        this.adjustTextareaHeight(userInput);
        
        const params = this.getGenerationParameters();
        const messages = this.getConversationHistory();
        
        this.isGenerating = true;
        this.updateGeneratingState(true);
        
        try {
            if (params.stream) {
                await this.streamGenerate(messages, params);
            } else {
                await this.generateText(messages, params);
            }
        } catch (error) {
            console.error('Generation error:', error);
            this.showSystemMessage(`Generation failed: ${error.message}`);
        } finally {
            this.isGenerating = false;
            this.updateGeneratingState(false);
        }
    }
    
    async generateText(messages, params) {
        try {
            const response = await fetch(`${this.apiBase}/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    messages: messages,
                    parameters: params
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.addMessage('assistant', data.result.text);
                this.showGenerationInfo(data.result);
            } else {
                this.showSystemMessage(`Generation failed: ${data.error}`);
            }
            
        } catch (error) {
            throw new Error(`Network error: ${error.message}`);
        }
    }
    
    async streamGenerate(messages, params) {
        const response = await fetch(`${this.apiBase}/generate/stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                messages: messages,
                parameters: params
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        let assistantMessageElement = this.addMessage('assistant', '');
        let fullText = '';
        
        try {
            while (true) {
                const { done, value } = await reader.read();
                
                if (done) break;
                
                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');
                
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            
                            if (data.error) {
                                this.showSystemMessage(`Stream error: ${data.error}`);
                                return;
                            }
                            
                            if (data.token) {
                                fullText += data.token;
                                assistantMessageElement.querySelector('.message-content').textContent = fullText;
                                this.scrollToBottom();
                            }
                            
                            if (data.finished) {
                                this.showGenerationInfo(data);
                                break;
                            }
                            
                        } catch (parseError) {
                            console.error('Error parsing stream data:', parseError);
                        }
                    }
                }
            }
        } finally {
            reader.releaseLock();
        }
    }
    
    getConversationHistory() {
        const messages = [];
        const messageElements = document.querySelectorAll('.message:not(.system)');
        
        messageElements.forEach(element => {
            const role = element.classList.contains('user') ? 'user' : 'assistant';
            const content = element.querySelector('.message-content').textContent;
            messages.push({ role, content });
        });
        
        return messages;
    }
    
    addMessage(role, content) {
        const messagesContainer = document.getElementById('messages');
        const messageElement = document.createElement('div');
        messageElement.className = `message ${role}`;
        
        const contentElement = document.createElement('div');
        contentElement.className = 'message-content';
        contentElement.textContent = content;
        
        messageElement.appendChild(contentElement);
        messagesContainer.appendChild(messageElement);
        
        this.scrollToBottom();
        return messageElement;
    }
    
    showSystemMessage(message) {
        const messagesContainer = document.getElementById('messages');
        const messageElement = document.createElement('div');
        messageElement.className = 'message system';
        
        const contentElement = document.createElement('div');
        contentElement.className = 'message-content';
        contentElement.textContent = message;
        
        messageElement.appendChild(contentElement);
        messagesContainer.appendChild(messageElement);
        
        this.scrollToBottom();
    }
    
    scrollToBottom() {
        const messagesContainer = document.getElementById('messages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    updateGeneratingState(generating) {
        const sendBtn = document.getElementById('send-btn');
        
        if (generating) {
            sendBtn.innerHTML = '<div class="loading"></div>Generating...';
            sendBtn.disabled = true;
        } else {
            sendBtn.innerHTML = 'Send';
            sendBtn.disabled = !this.currentModel;
        }
    }
    
    showGenerationInfo(result) {
        const infoElement = document.getElementById('generation-info');
        
        let infoText = `Generation completed in ${result.generation_time?.toFixed(2) || 'N/A'}s`;
        
        if (result.token_count) {
            infoText += ` • ${result.token_count} tokens`;
        }
        
        if (result.model_name) {
            infoText += ` • Model: ${result.model_name}`;
        }
        
        infoElement.textContent = infoText;
        infoElement.style.display = 'block';
        
        setTimeout(() => {
            infoElement.style.display = 'none';
        }, 5000);
    }
    
    addDefaultStopSequences() {
        this.addStopSequence('</s>');
        this.addStopSequence('<|end|>');
    }
    
    addStopSequence(value = '') {
        const container = document.getElementById('stop-sequences');
        const wrapper = document.createElement('div');
        wrapper.className = 'stop-sequence-input';
        
        const input = document.createElement('input');
        input.type = 'text';
        input.value = value;
        input.placeholder = 'Enter stop sequence...';
        
        const removeBtn = document.createElement('button');
        removeBtn.className = 'remove-btn';
        removeBtn.textContent = '×';
        removeBtn.onclick = () => wrapper.remove();
        
        wrapper.appendChild(input);
        wrapper.appendChild(removeBtn);
        container.appendChild(wrapper);
    }
    
    updateAllParamValues() {
        const params = ['temperature', 'top-p', 'top-k', 'max-length', 'frequency-penalty', 'presence-penalty', 'repetition-penalty'];
        params.forEach(param => this.updateParamValue(param));
    }
}

function updateParamValue(paramName) {
    const input = document.getElementById(paramName);
    const valueDisplay = document.getElementById(`${paramName}-value`);
    
    if (input && valueDisplay) {
        let value = input.value;
        
        if (paramName === 'top-k' || paramName === 'max-length') {
            value = parseInt(value);
        } else {
            value = parseFloat(value);
            if (paramName !== 'temperature' && paramName !== 'repetition-penalty') {
                value = value.toFixed(2);
            } else {
                value = value.toFixed(2);
            }
        }
        
        valueDisplay.textContent = value;
    }
}

function toggleSection(sectionId) {
    const content = document.getElementById(sectionId);
    const header = content.previousElementSibling;
    
    if (content.classList.contains('collapsed')) {
        content.classList.remove('collapsed');
        header.classList.remove('collapsed');
        content.style.maxHeight = content.scrollHeight + 'px';
    } else {
        content.classList.add('collapsed');
        header.classList.add('collapsed');
        content.style.maxHeight = '0';
    }
}

function loadModel() {
    window.mlxController.loadModel();
}

function unloadModel() {
    window.mlxController.unloadModel();
}

function sendMessage() {
    window.mlxController.sendMessage();
}

function addStopSequence() {
    window.mlxController.addStopSequence();
}

document.addEventListener('DOMContentLoaded', () => {
    window.mlxController = new MLXController();
});