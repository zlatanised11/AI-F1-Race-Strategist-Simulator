import openai
import os
from tenacity import retry, stop_after_attempt, wait_exponential

class GPTHelper:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def summarize_text(self, text: str, max_tokens: int = 150) -> str:
        """General purpose text summarization"""
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes text concisely."},
                {"role": "user", "content": f"Summarize this text: {text}"}
            ],
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of text"""
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Analyze the sentiment of this text. Respond with only one word: Positive, Neutral, or Negative."},
                {"role": "user", "content": f"Text: {text}"}
            ],
            max_tokens=10
        )
        return response.choices[0].message.content
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate_race_summary(self, prompt: str) -> str:
        """Generate a comprehensive race summary"""
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a Formula 1 analyst. Generate a comprehensive race summary based on the provided data."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        return response.choices[0].message.content