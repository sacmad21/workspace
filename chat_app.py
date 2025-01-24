import azure.functions as func
import logging
import os
from groq import Groq
from typing import Dict, List


# Get a free API key from https://console.groq.com/keys
GROQ_API_TOKEN = "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"

os.environ["GROQ_API_KEY"] = GROQ_API_TOKEN

LLAMA3_70B_INSTRUCT = "llama3-70b-8192"
LLAMA3_8B_INSTRUCT = "llama3-8b-8192"

DEFAULT_MODEL = LLAMA3_70B_INSTRUCT

client = Groq()

def assistant(content: str):
    return { "role": "assistant", "content": content }

def user(content: str):
    return { "role": "user", "content": content }

def chat_completion(
    messages: List[Dict],
    model = DEFAULT_MODEL,
    temperature: float = 0.6,
    top_p: float = 0.9,
) -> str:
    response = client.chat.completions.create(
        messages=messages,
        model=model,
        temperature=temperature,
        top_p=top_p,
    )
    return response.choices[0].message.content
        

def completion(
    prompt: str,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.6,
    top_p: float = 0.9,
) -> str:
    return chat_completion(
        [user(prompt)],
        model=model,
        temperature=temperature,
        top_p=top_p,
    )

def complete_and_print(prompt: str, model: str = DEFAULT_MODEL) -> str:
    print(f'==============\n{prompt}\n==============')
    response = completion(prompt, model)
    print(response, end='\n\n')
    return response

complete_and_print("Who is India' godfather ?")