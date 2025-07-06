# Learning Agent

This project is a learning agent that generates educational content, including chapters, topics, and tests, based on a given subject. It uses a local Llama model (or other LLMs) for content generation and provides an API for interaction.

## Features

- **Dynamic Content Generation:** Creates chapters, topics, and descriptions for any subject.
- **Test Generation:** Generates tests to assess user learning.
- **Multiple LLM Providers:** Supports Llama, OpenAI, Gemini, DeepSeek, Anthropic, and more (see `app/llm/`).
- **API-Driven:** Provides a simple API for easy integration with other applications.

## Project Structure

```
learning_agent/
├── app/
│   ├── api/              # API endpoints (FastAPI)
│   ├── llm/              # LLM provider implementations
│   ├── models/           # Pydantic models
│   ├── services/         # Business logic/services
│   └── main.py           # FastAPI app entry point
├── tests/                # Test cases
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

## Installation

1. **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd learning_agent
    ```

2. **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    ```

3. **Activate the virtual environment:**
    ```bash
    source venv/bin/activate
    ```

4. **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. **Run the application:**
    ```bash
    uvicorn app.main:app --reload
    ```
    The application will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000).

2. **API Endpoints:**
    - `GET /course/{subject}`: Generates a full course (with chapters, sections, and paragraphs) for the given subject. Optional query parameter: `llm_provider_name` (default: "llama").
    - `POST /exam`: Generates an exam for a given paragraph. The request body should include the paragraph (as JSON: `{ "paragraph": "..." }`). Optional query parameter: `llm_provider_name`.
    - `GET /course/{subject}/part`: Retrieves a specific part of the course (chapter, section, or paragraph) by IDs. Requires `chapter_id` (and optionally `section_id`, `paragraph_id`) as query parameters. Optional query parameter: `llm_provider_name`.

## Testing

To run the tests, use the following command:

```bash
pytest
```

## Model Configuration

To use a real Llama model, download a model file in GGUF format and update the `MODEL_PATH` in `app/api/learning.py` with the path to your model file.

If a model is not available, the application will use a fake model for testing purposes.

You can also switch between different LLM providers by modifying the provider in the code (see `app/llm/`).
