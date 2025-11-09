import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(dotenv_path="C:/Users/paing/LLMProjects/llm_engineering/api_key.env", override=True)
groq_api_key = os.getenv('GROQ_API_KEY')
ollama_api_key = os.getenv('OLLAMA_API_KEY')
OLLAMA_BASE_URL = "http://localhost:11434/v1"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

def create_clients():
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY is not set in environment variables!")
    if not ollama_api_key:
        raise ValueError("OLLAMA_API_KEY is not set in environment variables!")
    
    ollama = OpenAI(base_url=OLLAMA_BASE_URL, api_key=ollama_api_key)
    groq = OpenAI(base_url=GROQ_BASE_URL, api_key=groq_api_key)

    clients = {
        "groq": groq,
        "ollama": ollama,
        "models": {
            "GROQ_MODEL": "openai/gpt-oss-20b",
            "OLLAMA_MODEL": "ollama3.2"
        }
    }
    return clients