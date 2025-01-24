import openai

client = openai.OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key="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",
)

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Write a haiku about recursion in programming.",
        },
    ],
    max_tokens=500,
)
print("GPT Response :::::::::::::::::: \n", response)
choices: any = response.choices[0]
text = choices.message
response_content = text.content.strip()
print("response", response_content)