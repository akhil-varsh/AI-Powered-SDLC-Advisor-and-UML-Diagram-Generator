import requests
import json
from typing import List, Dict, Any, Optional

def call_model(
    messages: List[Dict[str, str]], 
    model: str = "qwen2.5:3b", 
    api_base: str = "http://localhost:11434",
    max_tokens: int = 2000,
    temperature: float = 0.7
) -> Optional[str]:
    """
    Call the DeepSeek model via Ollama API.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content'
        model: Model name (default: deepseek-coder:1.5b)
        api_base: API base URL (default: localhost)
        max_tokens: Maximum tokens to generate
        temperature: Temperature for generation
        
    Returns:
        Generated text or None if failed
    """
    try:
        # Construct API endpoint
        url = f"{api_base}/api/chat"
        
        # Prepare request payload
        payload = {
            "model": model,
            "messages": messages,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        # Make API request
        response = requests.post(url, json=payload)
        
        # Check if request was successful
        if response.status_code == 200:
            result = response.json()
            return result.get("message", {}).get("content")
        else:
            print(f"API error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error calling model: {str(e)}")
        return None

def call_model_with_system(
    system_prompt: str,
    user_message: str,
    model: str = "qwen2.5:3b",
    api_base: str = "http://localhost:11434"
) -> Optional[str]:
    """
    Convenience function to call the model with a system prompt and user message.
    
    Args:
        system_prompt: System prompt to guide model behavior
        user_message: User query
        model: Model name
        api_base: API base URL
        
    Returns:
        Generated text or None if failed
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
    return call_model(messages, model, api_base)

# For testing
if __name__ == "__main__":
    # Test the API call
    test_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Write a brief hello world program in Python."}
    ]
    
    response = call_model(test_messages)
    print(response)