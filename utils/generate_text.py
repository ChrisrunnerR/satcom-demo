# utils/generate_text.py

from together import Together
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_text(word_count=15):
    prompt = (
        f"Generate exactly {word_count} words of realistic spoken radio transmission in a military-style satcom setting. "
        f"Use terminology like 'copy', 'over', 'grid', 'squad', 'target', 'recon', 'command', etc. "
        f"It should sound like field communication. IMPORTANT: Generate exactly {word_count} words, no more, no less. "
        f"Count your words carefully and ensure the response is exactly {word_count} words long."
    )
    
    try:
        client = Together()  # uses TOGETHER_API_KEY from env
        
        response = client.chat.completions.create(
            model="mistralai/Mistral-7B-Instruct-v0.3",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Error generating text: {str(e)}"
