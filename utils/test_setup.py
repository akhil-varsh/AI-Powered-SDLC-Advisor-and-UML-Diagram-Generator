"""
SmartSDLC Setup Test Script
---------------------------
This script verifies that all required components are properly set up
and functioning for the SmartSDLC application.
"""

import sys
import requests
import zlib
import base64
import io
from PIL import Image
import time

def check_package(package_name):
    """Verify if a Python package is installed."""
    try:
        __import__(package_name)
        return True, f"✅ {package_name} is installed"
    except ImportError:
        return False, f"❌ {package_name} is not installed. Run: pip install {package_name}"

def check_ollama_connection():
    """Verify connection to Ollama service."""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5:3b",
                "prompt": "Say hello",
                "stream": False
            },
            timeout=5
        )
        if response.status_code == 200:
            return True, "✅ Successfully connected to Ollama service"
        else:
            return False, f"❌ Ollama returned status code {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "❌ Failed to connect to Ollama. Ensure Ollama service is running."
    except requests.exceptions.Timeout:
        return False, "❌ Connection to Ollama timed out"
    except Exception as e:
        return False, f"❌ Error connecting to Ollama: {str(e)}"

def check_qwen_model():
    """Verify Qwen model is available in Ollama."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            for model in models:
                if "qwen2.5:3b" in model.get("name", ""):
                    return True, "✅ qwen2.5:3b model is available in Ollama"
            return False, "❌ qwen2.5:3b model not found in Ollama. Run: ollama pull qwen2.5:3b"
        else:
            return False, f"❌ Failed to get models list. Status code: {response.status_code}"
    except Exception as e:
        return False, f"❌ Error checking for Qwen model: {str(e)}"

def test_plantuml_rendering():
    """Test PlantUML rendering capability."""
    try:
        # Simple test diagram
        plantuml_code = "@startuml\nclass Test\nTest : +method()\n@enduml"
        
        # Encode for PlantUML server
        zlibbed_str = zlib.compress(plantuml_code.encode('utf-8'))
        compressed_string = zlibbed_str[2:-4]
        encoded = base64.b64encode(compressed_string).decode('utf-8')
        
        # Fetch from PlantUML server
        url = f"http://www.plantuml.com/plantuml/img/{encoded}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            # Try to open the image to verify it's valid
            Image.open(io.BytesIO(response.content))
            return True, "✅ Successfully rendered a test UML diagram"
        else:
            return False, f"❌ PlantUML server returned status code {response.status_code}"
    except Exception as e:
        return False, f"❌ Error testing PlantUML rendering: {str(e)}"

def main():
    """Run all tests and report results."""
    print("SmartSDLC Setup Test")
    print("===================")
    
    all_passed = True
    
    # Check required packages
    packages = ["streamlit", "requests", "crewai", "langchain_community", "PIL"]
    for package in packages:
        success, message = check_package(package)
        print(message)
        all_passed = all_passed and success
    
    print("\nChecking Ollama Service:")
    success, message = check_ollama_connection()
    print(message)
    all_passed = all_passed and success
    
    if success:
        print("\nChecking for Qwen Model:")
        success, message = check_qwen_model()
        print(message)
        all_passed = all_passed and success
    
    print("\nTesting PlantUML Rendering:")
    success, message = test_plantuml_rendering()
    print(message)
    all_passed = all_passed and success
    
    print("\nOverall Result:")
    if all_passed:
        print("✅ All tests passed! You're ready to run SmartSDLC.")
    else:
        print("❌ Some tests failed. Please fix the issues above before running SmartSDLC.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())