# Local LLM with Internet Access using LangChain

This project demonstrates how to connect a local Large Language Model (LLM) running on LM Studio to the internet for real-time information retrieval using LangChain and the DuckDuckGo search engine.

## Setup

1.  **LM Studio:**
    *   Make sure your local LLM is running on LM Studio and the server is started (usually at `http://localhost:1234/v1`).

2.  **Install Dependencies:**
    *   Make sure you have Python installed. Then, open your terminal, activate the virtual environment, and run:
        ```bash
        pip install -r requirements.txt
        ```

## Usage

Once the setup is complete, run the application:

```bash
python src/app.py
```

The agent can also scrape content from specific URLs. To use this feature, simply include a URL in your prompt and ask the agent to summarize it, extract information, or perform other tasks based on the content of the page.