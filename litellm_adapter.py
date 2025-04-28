"""
LiteLLM Adapter - Optional integration with LiteLLM for more providers
"""
import requests
from typing import List, Dict, Any, Optional, Union

def completion(
    model: str = "ollama/qwen2.5:3b", 
    messages: List[Dict[str, str]] = None,
    api_base: str = "http://localhost:11434",
    stream: bool = False,
    max_tokens: int = 2000,
    temperature: float = 0.7, 
    format: str = None
) -> Union[Dict[str, Any], Any]:
    """
    Implementation that mimics LiteLLM's completion function for Ollama
    
    Args:
        model: Model name in format "ollama/model_name"
        messages: List of message dictionaries with 'role' and 'content'
        api_base: API base URL
        stream: Whether to stream the response
        max_tokens: Maximum tokens to generate
        temperature: Temperature for generation
        format: Optional format (e.g., "json")
        
    Returns:
        Response dictionary similar to LiteLLM's format
    """
    if messages is None:
        messages = []
        
    # Extract model name from "ollama/model_name" format
    if model.startswith("ollama/"):
        model_name = model.split("/")[1]
    else:
        model_name = model
    
    try:
        # Construct API endpoint
        url = f"{api_base}/api/chat"
        
        # Prepare request payload
        payload = {
            "model": model_name,
            "messages": messages,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        # Add format if specified
        if format == "json":
            payload["format"] = "json"
        
        # Handle streaming vs. non-streaming
        if stream:
            # For streaming, we need to implement a generator
            response = requests.post(url, json=payload, stream=True)
            
            def stream_generator():
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk_data = _parse_ollama_chunk(line)
                            yield chunk_data
                        except Exception as e:
                            print(f"Error parsing chunk: {e}")
                            continue
            
            return stream_generator()
        else:
            # For non-streaming, make the request and format the response
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                return _format_ollama_response(result)
            else:
                print(f"API error: {response.status_code}")
                print(f"Response: {response.text}")
                return {"error": response.text}
                
    except Exception as e:
        print(f"Error in completion: {str(e)}")
        return {"error": str(e)}

def _format_ollama_response(result: Dict[str, Any]) -> Dict[str, Any]:
    """Format Ollama response to match LiteLLM's format"""
    content = result.get("message", {}).get("content", "")
    
    return {
        "id": result.get("id", "response-id"),
        "created": result.get("created_at", 0),
        "model": result.get("model", ""),
        "object": "chat.completion",
        "choices": [
            {
                "finish_reason": "stop",
                "index": 0,
                "message": {
                    "content": content,
                    "role": "assistant"
                }
            }
        ],
        "usage": {
            "prompt_tokens": result.get("prompt_eval_count", 0),
            "completion_tokens": result.get("eval_count", 0),
            "total_tokens": result.get("prompt_eval_count", 0) + result.get("eval_count", 0)
        }
    }

def _parse_ollama_chunk(line: bytes) -> Dict[str, Any]:
    """Parse a single chunk from Ollama streaming response"""
    try:
        chunk_data = {}
        chunk_text = line.decode('utf-8')
        
        # Parse JSON if possible
        try:
            chunk_json = json.loads(chunk_text)
            content = chunk_json.get("message", {}).get("content", "")
            
            chunk_data = {
                "choices": [
                    {
                        "delta": {
                            "content": content,
                            "role": "assistant"
                        },
                        "index": 0
                    }
                ],
                "created": chunk_json.get("created_at", 0),
                "id": chunk_json.get("id", "chunk-id"),
                "model": chunk_json.get("model", ""),
                "object": "chat.completion.chunk"
            }
        except:
            # If not JSON, just use the raw text
            chunk_data = {
                "choices": [
                    {
                        "delta": {
                            "content": chunk_text,
                            "role": "assistant"
                        },
                        "index": 0
                    }
                ],
                "created": 0,
                "id": "chunk-id",
                "model": "",
                "object": "chat.completion.chunk"
            }
            
        return chunk_data
    except Exception as e:
        print(f"Error parsing chunk: {e}")
        return {
            "choices": [
                {
                    "delta": {
                        "content": "",
                        "role": "assistant"
                    },
                    "index": 0
                }
            ],
            "error": str(e)
        }

# For async support
async def acompletion(*args, **kwargs):
    """
    Async version of completion (simplified implementation)
    """
    import asyncio
    from async_generator import async_generator, yield_
    
    # Use the sync version since this is just an adapter
    result = completion(*args, **kwargs)
    
    # If streaming, create an async generator
    if kwargs.get("stream", False):
        @async_generator
        async def async_stream():
            for chunk in result:
                await yield_(chunk)
                # Small sleep to simulate async behavior
                await asyncio.sleep(0.01)
        
        return async_stream()
    else:
        # Just return the result for non-streaming
        return result