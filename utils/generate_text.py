# utils/generate_text.py

import openai
import os

def generate_text(minutes=0, seconds=10, api_key=None, model="gpt-4o-mini"):
    # Calculate total duration in seconds
    duration_seconds = (minutes * 60) + seconds
    
    # Estimate words based on average speaking rate (120 words per minute for radio communication)
    estimated_words = int((duration_seconds / 60) * 120)
    
    prompt = (
        f"Generate exactly {estimated_words} words of realistic radio transmission text in a military-style satcom setting. "
        f"Use terminology like 'copy', 'over', 'grid', 'squad', 'target', 'recon', 'command', etc. "
        f"It should sound like field communication and be approximately {duration_seconds} seconds long when spoken at normal pace. "
        f"IMPORTANT: Generate ONLY the spoken text. Do NOT include any stage directions, speaker names, brackets, or formatting. "
        f"Just write the actual words that would be spoken over the radio. "
        f"Make it exactly {estimated_words} words to match the {duration_seconds} second duration."
    )
    
    try:
        # Use provided API key or fall back to environment variable
        if api_key:
            client = openai.OpenAI(api_key=api_key)
        else:
            client = openai.OpenAI()  # uses OPENAI_API_KEY from env
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max(400, estimated_words * 2),  # Ensure enough tokens for longer texts
            temperature=0.7
        )

        # Clean up the response to remove any stage directions or formatting
        content = response.choices[0].message.content.strip()
        
        # Remove common stage direction patterns
        import re
        # Remove text in brackets, parentheses, or with common stage direction words
        content = re.sub(r'\[.*?\]', '', content)  # Remove [bracketed text]
        content = re.sub(r'\(.*?\)', '', content)  # Remove (parenthetical text)
        content = re.sub(r'^[A-Z\s]+:', '', content)  # Remove "SPEAKER:" prefixes
        content = re.sub(r'^\s*[-–—]\s*', '', content)  # Remove leading dashes
        content = re.sub(r'\s*[-–—]\s*$', '', content)  # Remove trailing dashes
        
        # Clean up extra whitespace
        content = re.sub(r'\s+', ' ', content).strip()
        
        # Verify word count - if too short, try to regenerate with more specific instructions
        actual_words = len(content.split())
        if actual_words < estimated_words * 0.7:  # If we got less than 70% of expected words
            # Try one more time with more specific instructions
            retry_prompt = (
                f"Generate a longer radio transmission text with EXACTLY {estimated_words} words. "
                f"Current text is only {actual_words} words, but we need {estimated_words} words. "
                f"Make it longer and more detailed while maintaining the military radio communication style. "
                f"Use terminology like 'copy', 'over', 'grid', 'squad', 'target', 'recon', 'command', etc. "
                f"IMPORTANT: Generate ONLY the spoken text, no stage directions or formatting."
            )
            
            try:
                retry_response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": retry_prompt}],
                    max_tokens=max(600, estimated_words * 3),
                    temperature=0.7
                )
                
                retry_content = retry_response.choices[0].message.content.strip()
                # Apply same cleanup to retry content
                retry_content = re.sub(r'\[.*?\]', '', retry_content)
                retry_content = re.sub(r'\(.*?\)', '', retry_content)
                retry_content = re.sub(r'^[A-Z\s]+:', '', retry_content)
                retry_content = re.sub(r'^\s*[-–—]\s*', '', retry_content)
                retry_content = re.sub(r'\s*[-–—]\s*$', '', retry_content)
                retry_content = re.sub(r'\s+', ' ', retry_content).strip()
                
                # Use retry content if it's longer
                if len(retry_content.split()) > actual_words:
                    content = retry_content
            except:
                pass  # If retry fails, use original content
        
        return content

    except openai.AuthenticationError:
        return "Error: Invalid OpenAI API key. Please check your configuration."
    except openai.RateLimitError:
        return "Error: Rate limit exceeded. Please try again later."
    except openai.APIError as e:
        return f"Error: OpenAI API error: {str(e)}"
    except Exception as e:
        return f"Error generating text: {str(e)}"
