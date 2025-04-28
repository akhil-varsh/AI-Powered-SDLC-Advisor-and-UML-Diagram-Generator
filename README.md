# SmartSDLC: UML Generator & SDLC Advisor

![AI-Powered-SDLC-Advisor-and-UML-Diagram-Generator Logo](https://img.shields.io/badge/SmartSDLC-UML%20%26%20SDLC%20Advisor-blue)
[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.26+-red.svg)](https://streamlit.io/)
[![CrewAI](https://img.shields.io/badge/CrewAI-Latest-orange.svg)](https://github.com/crewai/crewai)
[![Ollama](https://img.shields.io/badge/Ollama-Latest-purple.svg)](https://ollama.ai/)

## 📌 Overview

SmartSDLC is an AI-powered tool designed to assist software developers and project managers in UML diagram generation and SDLC (Software Development Life Cycle) methodology selection. By leveraging local AI models through Ollama, SmartSDLC generates professional UML diagrams and provides tailored SDLC recommendations based on project descriptions.

### ✨ Key Features

- **🔄 Multiple UML Diagram Types**: Generate Use Case, Class, Sequence, Component, Communication, and State Machine diagrams
- **🔍 SDLC Methodology Recommendations**: Get expert advice on the most suitable SDLC model for your project
- **🤖 AI-Powered Generation**: Utilizes AI agents working together via CrewAI framework
- **🖼️ Interactive Diagram Viewing**: See diagrams rendered in real-time
- **🔽 Export Options**: Save diagrams as images or copy Mermaid code
- **💻 Local Processing**: Runs on your local machine using Ollama (no data sent to external APIs)

## 📋 Prerequisites

- Python 3.11 or higher
- [Ollama](https://ollama.ai/) installed and running locally
- Qwen 2.5:3B model pulled in Ollama

## 🚀 Installation

### 1. Clone the repository
```bash
git clone https://github.com/akhil-varsh/AI-Powered-SDLC-Advisor-and-UML-Diagram-Generator.git
cd AI-Powered-SDLC-Advisor-and-UML-Diagram-Generator
```

### 2. Set up a virtual environment (optional but recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Install and start Ollama
Download Ollama from [https://ollama.ai/](https://ollama.ai/) and start the server.

### 5. Pull the required model
```bash
ollama pull qwen2.5:3b
```

## 💻 Usage

### Starting the application
```bash
streamlit run app.py
```

### Using the interface
1. Describe your software product in the text area
2. Select the type of UML diagram you want to generate
3. Adjust temperature and max tokens if needed
4. Click "Generate UML & SDLC Recommendation"
5. View your diagram and SDLC recommendation
6. Export or copy the diagram as needed

## 🏗️ Project Structure

- `app.py`: Main Streamlit application interface
- `model_api.py`: API for interacting with Ollama models
- `crew_orchestration.py`: CrewAI setup for agent collaboration
- `mermaid_renderer.py`: Rendering Mermaid diagrams


## 🔄 How It Works

AI-Powered-SDLC-Advisor-and-UML-Diagram-Generator uses a multi-agent approach through CrewAI to:

1. Analyze your software product description
2. Generate appropriate UML diagrams in Mermaid syntax
3. Recommend the most suitable SDLC methodology
4. Render the diagrams for interactive viewing

The agents work together sequentially:
- The SDLC Advisor agent evaluates project requirements and constraints
- The UML Generator agent creates accurate Mermaid code for the selected diagram type

## 📚 Supported Diagram Types

- **Use Case Diagram**: Shows interactions between users and system
- **Class Diagram**: Shows system classes, attributes, methods, and relationships
- **Sequence Diagram**: Shows object interactions arranged in time sequence
- **Component Diagram**: Shows system components and their interfaces
- **Communication Diagram**: Shows object interactions with numbered messages
- **State Machine Diagram**: Shows states, transitions, events, and actions

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) for the web interface
- [CrewAI](https://github.com/crewai/crewai) for the agent orchestration framework
- [Ollama](https://ollama.ai/) for local model hosting
- [Mermaid.js](https://mermaid-js.github.io/mermaid/) for diagram visualization
- [Qwen](https://huggingface.co/qwen) for the underlying language model
