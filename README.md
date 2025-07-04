# Learning Agent

This project is a learning agent that generates educational content, including chapters, topics, and tests, based on a given subject. It uses a local Llama model for content generation and provides an API for interaction.

## Features

*   **Dynamic Content Generation:** Creates chapters, topics, and descriptions for any subject.
*   **Test Generation:** Generates tests to assess user learning.
*   **Llama Integration:** Utilizes a local Llama model for natural language processing.
*   **API-Driven:** Provides a simple API for easy integration with other applications.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd learning_agent
    ```

2.  **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    ```

3.  **Activate the virtual environment:**
    ```bash
    source venv/bin/activate
    ```

4.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Run the application:**
    ```bash
    uvicorn app.main:app --reload
    ```
    The application will be available at `http://127.0.0.1:8000`.

2.  **API Endpoints:**
    *   `GET /chapters/{subject}`: Generates chapters for the given subject.
    *   `POST /test`: Generates a test for a given chapter.

## Testing

To run the tests, use the following command:

```bash
pytest
```

## Model Configuration

To use a real Llama model, you need to download a model file in GGUF format and update the `MODEL_PATH` in `learning_agent/app/api/learning.py` with the path to your model file.

If a model is not available, the application will use a fake model for testing purposes.
