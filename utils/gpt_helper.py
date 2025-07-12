import openai
import os
from tenacity import retry, stop_after_attempt, wait_exponential

class GPTHelper:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def summarize_radio(self, text: str) -> str:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a Formula 1 analyst summarizing team radio communications. Be concise and highlight key information."},
                {"role": "user", "content": f"Summarize this F1 team radio message in 1-2 sentences: {text}"}
            ],
            temperature=0.7,
            max_tokens=100
        )
        return response.choices[0].message.content
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def analyze_sentiment(self, text: str) -> str:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Analyze the sentiment of this F1 team radio message. Respond with only one word: Positive, Neutral, or Negative."},
                {"role": "user", "content": f"Message: {text}"}
            ],
            temperature=0.3,
            max_tokens=10
        )
        return response.choices[0].message.content