/*
Frontend JavaScript example for VizLearn API
Demonstrates how to integrate with the streaming API from a web frontend
*/

const API_BASE_URL = 'http://localhost:8000';
const API_KEY = 'vizlearn-static-key-2025';

class VizLearnAPI {
    constructor(baseUrl = API_BASE_URL, apiKey = API_KEY) {
        this.baseUrl = baseUrl;
        this.apiKey = apiKey;
    }

    // Helper method to create headers
    getHeaders(isJson = true) {
        const headers = {
            'Authorization': `Bearer ${this.apiKey}`
        };
        
        if (isJson) {
            headers['Content-Type'] = 'application/json';
        }
        
        return headers;
    }

    // Health check
    async healthCheck() {
        try {
            const response = await fetch(`${this.baseUrl}/health`);
            return await response.json();
        } catch (error) {
            console.error('Health check failed:', error);
            throw error;
        }
    }

    // Get supported content types
    async getContentTypes() {
        try {
            const response = await fetch(`${this.baseUrl}/content-types`, {
                headers: this.getHeaders(false)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Failed to get content types:', error);
            throw error;
        }
    }

    // Batch content generation
    async generateContent(title, description, numQuestions = 5, questionTypes = null) {
        try {
            const payload = {
                title,
                description,
                num_questions: numQuestions,
                question_types: questionTypes
            };

            const response = await fetch(`${this.baseUrl}/generate-content`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Content generation failed:', error);
            throw error;
        }
    }

    // Streaming content generation
    async generateContentStream(title, description, numQuestions = 5, questionTypes = null, onProgress = null, onComplete = null, onError = null) {
        try {
            const payload = {
                title,
                description,
                num_questions: numQuestions,
                question_types: questionTypes
            };

            const response = await fetch(`${this.baseUrl}/generate-content/stream`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                
                if (done) break;
                
                buffer += decoder.decode(value, { stream: true });
                
                // Process complete lines
                const lines = buffer.split('\n');
                buffer = lines.pop(); // Keep incomplete line in buffer
                
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            
                            switch (data.status) {
                                case 'started':
                                    console.log('Generation started:', data.message);
                                    break;
                                    
                                case 'progress':
                                    console.log('New question generated:', data.item.title);
                                    if (onProgress) {
                                        onProgress(data.item);
                                    }
                                    break;
                                    
                                case 'completed':
                                    console.log('Generation completed:', data.message);
                                    if (onComplete) {
                                        onComplete();
                                    }
                                    return;
                                    
                                case 'error':
                                    console.error('Generation error:', data.message);
                                    if (onError) {
                                        onError(new Error(data.message));
                                    }
                                    return;
                            }
                        } catch (parseError) {
                            console.warn('Failed to parse SSE data:', parseError);
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Streaming failed:', error);
            if (onError) {
                onError(error);
            }
            throw error;
        }
    }
}

// Example usage in HTML page
function createExampleHTML() {
    return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VizLearn API Example</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .question { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .question-title { font-weight: bold; color: #333; }
        .question-type { color: #666; font-size: 0.9em; }
        .loading { color: #007bff; }
        .error { color: #dc3545; }
        .success { color: #28a745; }
        button { padding: 10px 20px; margin: 5px; cursor: pointer; }
        input, textarea { width: 100%; padding: 8px; margin: 5px 0; }
    </style>
</head>
<body>
    <h1>VizLearn API Example</h1>
    
    <div>
        <label>Title:</label>
        <input type="text" id="title" value="Introduction to JavaScript" />
        
        <label>Description:</label>
        <textarea id="description" rows="3">Basic JavaScript concepts including variables, functions, and control structures</textarea>
        
        <label>Number of Questions:</label>
        <input type="number" id="numQuestions" value="3" min="1" max="10" />
        
        <button onclick="generateBatch()">Generate (Batch)</button>
        <button onclick="generateStream()">Generate (Streaming)</button>
        <button onclick="checkHealth()">Health Check</button>
    </div>
    
    <div id="status"></div>
    <div id="questions"></div>

    <script>
        // Insert the VizLearnAPI class here
        const api = new VizLearnAPI();
        
        async function checkHealth() {
            const status = document.getElementById('status');
            status.innerHTML = '<div class="loading">Checking health...</div>';
            
            try {
                const health = await api.healthCheck();
                status.innerHTML = '<div class="success">API is healthy: ' + JSON.stringify(health) + '</div>';
            } catch (error) {
                status.innerHTML = '<div class="error">Health check failed: ' + error.message + '</div>';
            }
        }
        
        async function generateBatch() {
            const title = document.getElementById('title').value;
            const description = document.getElementById('description').value;
            const numQuestions = parseInt(document.getElementById('numQuestions').value);
            
            const status = document.getElementById('status');
            const questionsDiv = document.getElementById('questions');
            
            status.innerHTML = '<div class="loading">Generating content (batch)...</div>';
            questionsDiv.innerHTML = '';
            
            try {
                const result = await api.generateContent(title, description, numQuestions);
                status.innerHTML = '<div class="success">Generated ' + result.total_questions + ' questions!</div>';
                
                result.playground_items.forEach((item, index) => {
                    questionsDiv.innerHTML += createQuestionHTML(item, index + 1);
                });
            } catch (error) {
                status.innerHTML = '<div class="error">Generation failed: ' + error.message + '</div>';
            }
        }
        
        async function generateStream() {
            const title = document.getElementById('title').value;
            const description = document.getElementById('description').value;
            const numQuestions = parseInt(document.getElementById('numQuestions').value);
            
            const status = document.getElementById('status');
            const questionsDiv = document.getElementById('questions');
            
            status.innerHTML = '<div class="loading">Generating content (streaming)...</div>';
            questionsDiv.innerHTML = '';
            
            let questionCount = 0;
            
            try {
                await api.generateContentStream(
                    title,
                    description,
                    numQuestions,
                    null,
                    // onProgress
                    (item) => {
                        questionCount++;
                        questionsDiv.innerHTML += createQuestionHTML(item, questionCount);
                        status.innerHTML = '<div class="loading">Generated ' + questionCount + ' questions so far...</div>';
                    },
                    // onComplete
                    () => {
                        status.innerHTML = '<div class="success">Streaming completed! Generated ' + questionCount + ' questions.</div>';
                    },
                    // onError
                    (error) => {
                        status.innerHTML = '<div class="error">Streaming failed: ' + error.message + '</div>';
                    }
                );
            } catch (error) {
                status.innerHTML = '<div class="error">Streaming failed: ' + error.message + '</div>';
            }
        }
        
        function createQuestionHTML(item, index) {
            return \`
                <div class="question">
                    <div class="question-title">Q\${index}: \${item.title}</div>
                    <div class="question-type">Type: \${item.type}</div>
                    <div>Description: \${item.description}</div>
                    <div>Content: <pre>\${JSON.stringify(item.content, null, 2)}</pre></div>
                    \${item.hints ? '<div>Hint: ' + item.hints + '</div>' : ''}
                </div>
            \`;
        }
    </script>
</body>
</html>
    `;
}

// Export for Node.js usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { VizLearnAPI, createExampleHTML };
}
