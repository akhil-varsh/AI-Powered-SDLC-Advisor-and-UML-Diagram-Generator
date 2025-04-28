import logging
import re
from typing import Dict, Optional, Union, Tuple
import uuid
import os
import tempfile

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_plantuml_to_mermaid(plantuml_code: str) -> str:
    """
    Convert PlantUML code to Mermaid syntax. This is a simplified converter
    and works best for basic diagrams.
    
    Args:
        plantuml_code: PlantUML source code
        
    Returns:
        Equivalent Mermaid diagram code
    """
    # Extract the content between @startuml and @enduml
    match = re.search(r'@startuml(.*?)@enduml', plantuml_code, re.DOTALL)
    if match:
        content = match.group(1).strip()
    else:
        content = plantuml_code.strip()
    
    # Detect diagram type based on content
    if 'class ' in content.lower():
        return convert_class_diagram(content)
    elif 'actor ' in content.lower() or 'usecase ' in content.lower():
        return convert_usecase_diagram(content)
    elif '-->' in content or '->' in content or '=>' in content:
        if 'participant ' in content.lower() or 'actor ' in content.lower():
            return convert_sequence_diagram(content)
        else:
            return convert_flowchart(content)
    elif '[' in content and ']' in content and ('component ' in content.lower() or 'interface ' in content.lower()):
        return convert_component_diagram(content)
    elif 'state ' in content.lower():
        return convert_state_diagram(content)
    else:
        # Default to flowchart if type can't be determined
        return convert_flowchart(content)

def convert_class_diagram(content: str) -> str:
    """Convert PlantUML class diagram to Mermaid class diagram"""
    mermaid = "classDiagram\n"
    
    # Process class definitions
    class_pattern = r'class\s+(\w+)(?:\s*{(.*?)})?'
    for match in re.finditer(class_pattern, content, re.DOTALL):
        class_name = match.group(1)
        mermaid += f"    class {class_name}\n"
        
        if match.group(2):  # If there are attributes/methods
            attrs = match.group(2).strip().split('\n')
            for attr in attrs:
                attr = attr.strip()
                if attr:
                    # Add + for public, - for private attributes/methods
                    if '+' in attr:
                        mermaid += f"    {class_name} : +{attr.split('+')[1].strip()}\n"
                    elif '-' in attr:
                        mermaid += f"    {class_name} : -{attr.split('-')[1].strip()}\n"
                    else:
                        mermaid += f"    {class_name} : {attr}\n"
    
    # Process relationships
    relations = [
        (r'(\w+)\s+--\s+(\w+)', "--"),  # Association
        (r'(\w+)\s+\.\.\s+(\w+)', ".."),  # Dependency
        (r'(\w+)\s+<\|--\s+(\w+)', "<|--"),  # Inheritance
        (r'(\w+)\s+\*--\s+(\w+)', "*--"),  # Composition
        (r'(\w+)\s+o--\s+(\w+)', "o--")   # Aggregation
    ]
    
    for pattern, rel_type in relations:
        for match in re.finditer(pattern, content):
            mermaid += f"    {match.group(1)} {rel_type} {match.group(2)}\n"
    
    return mermaid

def convert_usecase_diagram(content: str) -> str:
    """Convert PlantUML use case diagram to Mermaid flowchart (closest equivalent)"""
    mermaid = "flowchart TD\n"
    
    # Convert actors
    actor_pattern = r'actor\s+(\w+)'
    for match in re.finditer(actor_pattern, content):
        actor_name = match.group(1)
        mermaid += f"    {actor_name}[👤 {actor_name}]\n"
    
    # Convert use cases
    usecase_pattern = r'usecase\s+"?(.*?)"?(?:\s+as\s+(\w+))?'
    for match in re.finditer(usecase_pattern, content):
        usecase_text = match.group(1)
        usecase_id = match.group(2) if match.group(2) else usecase_text.replace(" ", "_")
        mermaid += f"    {usecase_id}[({usecase_text})]\n"
    
    # Convert relationships
    relation_pattern = r'(\w+)\s*-+>\s*(\w+)\s*:'
    for match in re.finditer(relation_pattern, content):
        mermaid += f"    {match.group(1)} -->|uses| {match.group(2)}\n"
    
    # Simple connections
    simple_relation = r'(\w+)\s*--\s*(\w+)'
    for match in re.finditer(simple_relation, content):
        mermaid += f"    {match.group(1)} --- {match.group(2)}\n"
        
    return mermaid

def convert_sequence_diagram(content: str) -> str:
    """Convert PlantUML sequence diagram to Mermaid sequence diagram"""
    mermaid = "sequenceDiagram\n"
    
    # Convert participants
    participant_pattern = r'(participant|actor)\s+"?(.*?)"?(?:\s+as\s+(\w+))?'
    for match in re.finditer(participant_pattern, content):
        name = match.group(2)
        alias = match.group(3) if match.group(3) else name.replace(" ", "_")
        mermaid += f"    participant {alias} as {name}\n"
    
    # Convert messages
    message_patterns = [
        (r'(\w+)\s*->\s*(\w+)\s*:\s*(.*?)(?:\n|$)', "->"),  # Solid arrow
        (r'(\w+)\s*-->\s*(\w+)\s*:\s*(.*?)(?:\n|$)', "->>"),  # Dashed arrow
        (r'(\w+)\s*<-\s*(\w+)\s*:\s*(.*?)(?:\n|$)', "<-"),  # Return solid
        (r'(\w+)\s*<--\s*(\w+)\s*:\s*(.*?)(?:\n|$)', "<<-")   # Return dashed
    ]
    
    for pattern, arrow in message_patterns:
        for match in re.finditer(pattern, content):
            from_part = match.group(1)
            to_part = match.group(2)
            message = match.group(3).strip()
            mermaid += f"    {from_part}{arrow}{to_part}: {message}\n"
    
    return mermaid

def convert_component_diagram(content: str) -> str:
    """Convert PlantUML component diagram to Mermaid flowchart"""
    mermaid = "flowchart LR\n"
    
    # Convert components
    component_pattern = r'(?:component|interface)\s+"?(.*?)"?(?:\s+as\s+(\w+))?'
    for match in re.finditer(component_pattern, content):
        name = match.group(1)
        alias = match.group(2) if match.group(2) else name.replace(" ", "_")
        mermaid += f"    {alias}[{name}]\n"
    
    # Process relationships 
    for match in re.finditer(r'(\w+)\s*-->\s*(\w+)', content):
        mermaid += f"    {match.group(1)} --> {match.group(2)}\n"
        
    # Process other types of connections
    for match in re.finditer(r'(\w+)\s*--\s*(\w+)', content):
        mermaid += f"    {match.group(1)} --- {match.group(2)}\n"
        
    return mermaid

def convert_state_diagram(content: str) -> str:
    """Convert PlantUML state diagram to Mermaid state diagram"""
    mermaid = "stateDiagram-v2\n"
    
    # Convert states
    state_pattern = r'state\s+"?(.*?)"?(?:\s+as\s+(\w+))?'
    for match in re.finditer(state_pattern, content):
        name = match.group(1)
        alias = match.group(2) if match.group(2) else name.replace(" ", "_")
        mermaid += f"    {alias}: {name}\n"
    
    # Convert transitions
    transition_pattern = r'(\w+)\s*-->\s*(\w+)(?:\s*:\s*(.*?))?(?:\n|$)'
    for match in re.finditer(transition_pattern, content):
        from_state = match.group(1)
        to_state = match.group(2)
        label = f": {match.group(3)}" if match.group(3) else ""
        mermaid += f"    {from_state} --> {to_state}{label}\n"
        
    return mermaid

def convert_flowchart(content: str) -> str:
    """Convert generic PlantUML to Mermaid flowchart"""
    mermaid = "flowchart TD\n"
    
    # Extract nodes (anything that appears before --> or --)
    nodes = set()
    for line in content.split('\n'):
        if '-->' in line or '--' in line:
            parts = re.split(r'-->|--', line)
            if len(parts) > 1:
                nodes.add(parts[0].strip())
                nodes.add(parts[1].strip())
    
    # Add nodes
    for node in nodes:
        if node:
            node_id = node.replace(" ", "_")
            mermaid += f"    {node_id}[{node}]\n"
    
    # Add relationships
    for line in content.split('\n'):
        if '-->' in line:
            parts = line.split('-->')
            if len(parts) == 2:
                from_node = parts[0].strip().replace(" ", "_")
                to_node = parts[1].strip().replace(" ", "_")
                mermaid += f"    {from_node} --> {to_node}\n"
        elif '--' in line:
            parts = line.split('--')
            if len(parts) == 2:
                node1 = parts[0].strip().replace(" ", "_")
                node2 = parts[1].strip().replace(" ", "_")
                mermaid += f"    {node1} --- {node2}\n"
                
    return mermaid

def generate_mermaid_html(mermaid_code: str, height: int = 500) -> str:
    """
    Generate HTML with embedded Mermaid code
    
    Args:
        mermaid_code: Mermaid diagram code
        height: Height of the diagram in pixels
        
    Returns:
        HTML string with embedded Mermaid diagram
    """
    # Sanitize the mermaid code for HTML embedding
    mermaid_code = mermaid_code.replace('"', '\\"').replace('\n', '\\n')
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mermaid Diagram</title>
        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
        <script>
            mermaid.initialize({{
                startOnLoad: true,
                theme: 'default',
                securityLevel: 'loose',
                flowchart: {{ htmlLabels: true }}
            }});
        </script>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 10px;
            }}
            .mermaid {{
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="mermaid">
{mermaid_code}
        </div>
    </body>
    </html>
    """
    
    return html

def save_mermaid_html_to_temp(mermaid_code: str) -> Tuple[str, bool]:
    """
    Save Mermaid HTML to a temporary file
    
    Args:
        mermaid_code: Mermaid diagram code
        
    Returns:
        Tuple of (file_path, success_flag)
    """
    try:
        # Generate unique ID for the file
        unique_id = str(uuid.uuid4())[:8]
        
        # Create temp file path
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, f"mermaid_diagram_{unique_id}.html")
        
        # Generate HTML content
        html_content = generate_mermaid_html(mermaid_code)
        
        # Write to file
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        logger.info(f"Mermaid diagram saved to {temp_file}")
        return temp_file, True
        
    except Exception as e:
        error_msg = f"Failed to save Mermaid HTML: {str(e)}"
        logger.error(error_msg)
        return error_msg, False