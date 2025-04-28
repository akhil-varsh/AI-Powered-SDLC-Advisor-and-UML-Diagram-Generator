from crewai import Agent, Task, Crew, Process
from typing import Dict, Any, Optional
from model_api import call_model_with_system
import re

class OllamaLLM:
    """Custom LLM class for CrewAI to use Ollama"""
    
    def __init__(self, model_name="ollama/qwen2.5:3b", api_base="http://localhost:11434"):
        self.model_name = model_name
        self.api_base = api_base
    
    def __call__(self, prompt):
        """Call the LLM with the given prompt"""
        return call_model_with_system(
            system_prompt="You are a helpful AI assistant.",
            user_message=prompt,
            model=self.model_name,
            api_base=self.api_base
        ) or "Error: Failed to get response from model."

def create_sdlc_advisor_agent() -> Agent:
    """Create an agent that recommends SDLC models"""
    
    system_prompt = """
    You are an expert Software Development Lifecycle (SDLC) consultant.
    Your job is to analyze software project descriptions and recommend the most appropriate SDLC model.
    Consider project scale, complexity, requirements clarity, time constraints, and team expertise.
    
    Common SDLC models include:
    1. Waterfall - Linear sequential approach, good for well-defined requirements
    2. Agile - Iterative approach with frequent customer feedback
    3. Scrum - Agile framework with sprints and specific roles
    4. Kanban - Visual workflow management with continuous delivery
    5. Spiral - Risk-driven approach with iterative prototyping
    6. DevOps - Integration of development and operations throughout lifecycle
    7. RAD (Rapid Application Development) - Emphasis on rapid prototyping
    8. V-Model - Testing integrated with each development phase
    
    Provide a clear recommendation with 3-5 bullet points justifying your choice.
    """
    
    return Agent(
        role="SDLC Advisor",
        goal="Recommend the most appropriate SDLC model for software projects",
        backstory="An expert consultant with 20+ years experience in software development methodologies",
        verbose=True,
        allow_delegation=False,
        llm=OllamaLLM()
    )

def create_mermaid_generator_agent() -> Agent:
    """Create an agent that generates Mermaid diagram code directly"""
    
    system_prompt = """
    You are an expert UML diagram designer who specializes in Mermaid syntax.
    Your job is to create accurate, clean, and professional Mermaid code for different diagram types based on software requirements.
    
    For each diagram type, follow these specific guidelines:
    
    1. Use Case Diagram (as flowchart in Mermaid):
       - Identify actors (users and external systems)
       - Define main use cases
       - Show relationships between actors and use cases
       - Use the flowchart TD syntax and represent actors with emoji 👤
       - Example:
         
         flowchart TD
             User[👤 User]
             Admin[👤 Administrator]
             UC1[Login to System]
             UC2[Manage Account]
             User --> UC1
             User --> UC2
             Admin --> UC1
         
    
    2. Class Diagram:
       - Identify key classes with attributes and methods
       - Show relationships (inheritance, association, composition)
       - Include multiplicities where appropriate
       - Use the classDiagram syntax
       - Example:
         
         classDiagram
             class User {
                +String username
                +String email
                +login()
                +logout()
             }
             class Product {
                +String name
                +Double price
                +getDetails()
             }
             User -- Product : views >
         
    
    3. Sequence Diagram:
       - Show object interactions in time sequence
       - Include proper activation
       - Show message passing between objects
       - Use the sequenceDiagram syntax
       - Example:
         
         sequenceDiagram
             participant U as User
             participant S as System
             participant D as Database
             U->>S: Login Request
             S->>D: Validate Credentials
             D-->>S: Authentication Result
             S-->>U: Login Response
         
    
    4. Component Diagram (as flowchart in Mermaid):
       - Show system components and their interfaces
       - Define dependencies between components
       - Group related components
       - Use the flowchart LR syntax
       - Example:
         
         flowchart LR
             subgraph Frontend
                 UI[User Interface]
                 Logic[Business Logic]
             end
             subgraph Backend
                 API[REST API]
                 DB[(Database)]
             end
             UI --> Logic
             Logic --> API
             API --> DB
         
    
    5. Communication Diagram (as flowchart in Mermaid):
       - Show object interactions with numbered messages
       - Focus on structural organization
       - Use the flowchart syntax
       - Example:
         
         flowchart TD
             A[Object A]
             B[Object B]
             C[Object C]
             A -->|1: request()| B
             B -->|2: validate()| C
             C -->|3: result()| B
             B -->|4: response()| A
         
    
    6. State Machine Diagram:
       - Show states, transitions, events, and actions
       - Include initial and final states
       - Define guard conditions where needed
       - Use the stateDiagram-v2 syntax
       - Example:
         
         stateDiagram-v2
             [*] --> Idle
             Idle --> Processing: Submit
             Processing --> Success: Valid
             Processing --> Failed: Invalid
             Success --> Idle: Reset
             Failed --> Idle: Reset
             Success --> [*]: Exit
             Failed --> [*]: Exit
         
    
    Always ensure your output is valid Mermaid syntax. Keep the diagram focused and clean - include only the most important elements.
    Use appropriate styling to improve readability. DO NOT include any explanatory text, just return the complete Mermaid code.
    """
    
    return Agent(
        role="UML Generator",
        goal="Create accurate and clean Mermaid diagrams from requirements",
        backstory="A senior software architect with deep expertise in software modeling and UML diagrams using Mermaid syntax",
        verbose=True,
        allow_delegation=False,
        llm=OllamaLLM()
    )

def run_crew_task(product_description: str, diagram_type: str, 
               temperature: float = 0.7, max_tokens: int = 2000) -> Optional[Dict[str, str]]:
    """
    Run the crew task to get SDLC recommendation and Mermaid code
    
    Args:
        product_description: Description of the software product
        diagram_type: Type of UML diagram to generate
        temperature: Temperature for model generation
        max_tokens: Maximum tokens to generate
        
    Returns:
        Dictionary with sdlc_recommendation and mermaid_code, or None if failed
    """
    try:
        # Create agents with custom LLM configurations
        llm = OllamaLLM(model_name="ollama/qwen2.5:3b")
        llm.model_kwargs = {"temperature": temperature, "max_tokens": max_tokens}
        
        # Create agents
        sdlc_advisor = create_sdlc_advisor_agent()
        mermaid_generator = create_mermaid_generator_agent()
        
        # Create tasks (without explicit IDs - let CrewAI handle IDs internally)
        sdlc_task = Task(
            description=f"""
            Analyze the following software product description and recommend the most suitable SDLC model:
            
            {product_description}
            
            Provide a clear recommendation with 3-5 bullet points justifying your choice.
            """,
            agent=sdlc_advisor,
            expected_output="A recommendation of an SDLC model with justification"
        )
        
        # Map diagram types to Mermaid syntax
        mermaid_diagram_type_map = {
            "Use Case": "flowchart TD (for Use Case Diagram)",
            "Class": "classDiagram",
            "Sequence": "sequenceDiagram",
            "Component": "flowchart LR (for Component Diagram)",
            "Communication": "flowchart TD (for Communication Diagram)",
            "State Machine": "stateDiagram-v2"
        }
        
        mermaid_syntax = mermaid_diagram_type_map.get(diagram_type, diagram_type)
        
        uml_task = Task(
            description=f"""
            Based on the following software product description, create a {diagram_type} diagram using Mermaid syntax:

            {product_description}

            Generate complete and valid Mermaid code for a {diagram_type} diagram that accurately represents the system.
            Only return the Mermaid code without any additional explanation.
            The Mermaid code must:
            - Contain no comments (// or ''') and no unnecessary characters.
            - Be clean and professional, with proper indentation, correct arrows, and no typos.
            - Follow consistent naming conventions (PascalCase for classes/entities/states, camelCase for attributes/methods).
            - Use the latest Mermaid syntax versions available (e.g., stateDiagram-v2 for State Diagrams).
            Use the {mermaid_syntax} syntax for this diagram type.
            """,
            agent=mermaid_generator,
            expected_output=f"Complete Mermaid code for a {diagram_type} diagram"
        )
        
        # Create and run crew for SDLC recommendation and Mermaid generation
        crew = Crew(
            agents=[sdlc_advisor, mermaid_generator],
            tasks=[sdlc_task, uml_task],
            verbose=True,
            process=Process.sequential
        )
        
        # Get the results from the crew
        result = crew.kickoff()
        
        # Print debug info
        print(f"CrewOutput type: {type(result)}")
        print(f"CrewOutput dir: {dir(result)}")
        
        # Try to get task outputs
        try:
            # Initialize default outputs
            sdlc_output = "No SDLC recommendation generated"
            mermaid_output = "flowchart TD\n    A[No diagram generated]"
            
            # IMPROVED EXTRACTION LOGIC - Try multiple methods to get the outputs
            
            # Method 1: Try to get the tasks_output attribute directly (newer CrewAI versions)
            if hasattr(result, 'tasks_output') and result.tasks_output:
                try:
                    tasks_output = result.tasks_output
                    if isinstance(tasks_output, list) and len(tasks_output) >= 2:
                        sdlc_output = tasks_output[0]
                        mermaid_output = tasks_output[1]
                        print("Successfully retrieved outputs using tasks_output attribute")
                    elif isinstance(tasks_output, dict):
                        # In case it's a dictionary with task IDs as keys
                        values = list(tasks_output.values())
                        if len(values) >= 2:
                            sdlc_output = values[0]
                            mermaid_output = values[1]
                            print("Successfully retrieved outputs from tasks_output dict")
                except Exception as e:
                    print(f"Error accessing tasks_output: {str(e)}")
            
            # Method 2: Try the tasks attribute if available
            elif hasattr(result, "tasks"):
                try:
                    tasks_iter = iter(result.tasks)
                    first_task = next(tasks_iter, None)
                    second_task = next(tasks_iter, None)
                    
                    if first_task and hasattr(first_task, 'output'):
                        sdlc_output = first_task.output
                        print(f"First task output type: {type(sdlc_output)}")
                    
                    if second_task and hasattr(second_task, 'output'):
                        mermaid_output = second_task.output
                        print(f"Second task output type: {type(mermaid_output)}")
                        
                    print("Successfully retrieved outputs using tasks attribute")
                except Exception as e:
                    print(f"Error accessing tasks: {str(e)}")
            
            # Method 3: If all else fails, try to use the raw attribute or string representation
            if hasattr(result, "raw"):
                try:
                    raw_result = result.raw
                    if isinstance(raw_result, dict) and len(raw_result) >= 2:
                        # It might be a dictionary with task outputs
                        values = list(raw_result.values())
                        if values[0] and len(str(values[0])) > len(str(sdlc_output)):
                            sdlc_output = str(values[0])
                        if values[1] and len(str(values[1])) > len(str(mermaid_output)):
                            mermaid_output = str(values[1])
                        print("Used raw attribute as data source")
                except Exception as e:
                    print(f"Error using raw attribute: {str(e)}")
            
            # Method 4: As last resort, try string representation
            try:
                # If all else fails, try to get useful information from the string representation
                result_str = str(result)
                print(f"Result string: {result_str[:200]}...")  # First 200 chars
                
                # Extract more comprehensive content from the string representation
                # First try to extract SDLC recommendation with more context
                sdlc_section = None
                mermaid_section = None
                
                # Look for SDLC section - search for common patterns
                for pattern in [
                    r'SDLC.*?:.*?(\w+(?:\s+\w+)*(?:\n\s*[-•*]\s*[^\n]+)+)',  # Bullet points
                    r'SDLC.*?:.*?(\w+(?:\s+\w+)*\n.*?(?=\n\n|\Z))',  # Until double newline
                    r'recommend.*?(\w+(?:\s+\w+){0,3}).*?(?:\n\s*[-•*].*?)+',  # Recommendation with bullets
                    r'recommend.*?(\w+(?:\s+\w+){0,3}).*?(?:\n.*?){1,10}',     # Recommendation with context
                ]:
                    match = re.search(pattern, result_str, re.IGNORECASE | re.DOTALL)
                    if match:
                        sdlc_section = match.group(0).strip()
                        break
                
                # If we found a better SDLC section and it's longer than what we have
                if sdlc_section and len(sdlc_section) > len(str(sdlc_output)):
                    sdlc_output = sdlc_section
                
                # Look for Mermaid code in the string representation
                # First try to find a code block with mermaid
                mermaid_match = re.search(r'```(?:mermaid)?\s*([\s\S]*?```)', result_str)
                if mermaid_match:
                    mermaid_section = mermaid_match.group(1).replace('```', '').strip()
                else:
                    # Otherwise look for common diagram type indicators
                    for diagram_start in ["flowchart", "sequenceDiagram", "classDiagram", 
                                         "stateDiagram", "stateDiagram-v2", "gantt", 
                                         "pie", "journey", "gitGraph"]:
                        pattern = f'({diagram_start}[\\s\\S]*?)(?:```|\\n\\n|$)'
                        match = re.search(pattern, result_str)
                        if match:
                            mermaid_section = match.group(1).strip()
                            break
                
                # If we found a better Mermaid section and it's longer than what we have
                if mermaid_section and len(mermaid_section) > len(str(mermaid_output)):
                    mermaid_output = mermaid_section
                
                # For debugging only - print the full string representation
                with open("crew_output_debug.txt", "w") as f:
                    f.write(result_str)
                
                print("Used string representation as fallback")
            except Exception as e:
                print(f"Error using string representation: {str(e)}")
            
            # Process the outputs
            if isinstance(mermaid_output, str):
                mermaid_code = extract_mermaid_code(mermaid_output)
            else:
                mermaid_code = extract_mermaid_code(str(mermaid_output))
            
            if not isinstance(sdlc_output, str):
                sdlc_output = str(sdlc_output)
            
            # Print final output info for debugging
            print(f"SDLC output length: {len(sdlc_output)}")
            print(f"Mermaid code length: {len(mermaid_code)}")
            
            return {
                "sdlc_recommendation": sdlc_output,
                "mermaid_code": mermaid_code
            }
            
        except Exception as inner_e:
            print(f"Error processing CrewAI output: {str(inner_e)}")
            print(f"Result type: {type(result)}")
            
            # Return a failsafe output
            return {
                "sdlc_recommendation": "Error generating SDLC recommendation. Please try again.",
                "mermaid_code": "flowchart TD\n    A[Error generating diagram. Please try again.]"
            }
        
    except Exception as e:
        print(f"Error in crew task: {str(e)}")
        return None

def extract_mermaid_code(text: str) -> str:
    """
    Extract Mermaid code from text, ensuring it has the correct format
    
    Args:
        text: Text containing Mermaid code
        
    Returns:
        Cleaned Mermaid code
    """
    # Look for code blocks
    code_block_pattern = r'```(?:mermaid)?\s*([\s\S]*?)```'
    match = re.search(code_block_pattern, text)
    
    if match:
        return match.group(1).strip()
    
    # Check for specific diagram type indicators
    diagram_types = [
        "flowchart", "sequenceDiagram", "classDiagram", 
        "stateDiagram", "stateDiagram-v2", "gantt", 
        "pie", "journey", "gitGraph"
    ]
    
    for dtype in diagram_types:
        if dtype in text:
            # Find the start of the diagram code
            start_idx = text.find(dtype)
            if start_idx != -1:
                return text[start_idx:].strip()
    
    # If no indicators found, return the whole text as is
    # It might be just the diagram code without any markers
    return text.strip() or "flowchart TD\n    A[No valid diagram code generated]"

def is_valid_mermaid(code: str) -> bool:
    """
    Basic validation for Mermaid code
    
    Args:
        code: Mermaid code to validate
        
    Returns:
        Boolean indicating if the code appears to be valid Mermaid
    """
    if not code or len(code) < 10:
        return False
    
    # Check if it starts with a valid Mermaid diagram type
    valid_starts = [
        "flowchart", "sequenceDiagram", "classDiagram", 
        "stateDiagram", "stateDiagram-v2", "gantt", 
        "pie", "journey", "gitGraph"
    ]
    
    for start in valid_starts:
        if code.lstrip().startswith(start):
            return True
    
    return False
