# import streamlit as st
# import requests
# import base64
# import zlib
# import json
# import re
# from crewai import Agent, Task, Crew, Process
# from langchain_community.llms import Ollama
# import io
# from PIL import Image
# import time

# # Set page config
# st.set_page_config(
#     page_title="SmartSDLC: UML Generator & SDLC Advisor",
#     page_icon="📊",
#     layout="wide"
# )

# # Configure the Ollama LLM (local Qwen model)
# @st.cache_resource
# def get_qwen_llm():
#     try:
#         return Ollama(model="qwen2.5:3b")
#     except Exception as e:
#         st.error(f"Failed to connect to Ollama service: {str(e)}")
#         st.warning("Make sure Ollama is running with the qwen2.5:3b model installed.")
#         return None

# # Helper function to encode PlantUML for rendering
# def encode_plantuml(plantuml_code):
#     zlibbed_str = zlib.compress(plantuml_code.encode('utf-8'))
#     compressed_string = zlibbed_str[2:-4]  # Remove the zlib header and checksum
#     return base64.b64encode(compressed_string).decode('utf-8')

# # Function to render PlantUML diagram from code
# def render_plantuml(plantuml_code):
#     try:
#         # Clean up any PlantUML syntax errors (common issues)
#         plantuml_code = plantuml_code.replace("@startuml", "").replace("@enduml", "")
#         plantuml_code = f"@startuml\n{plantuml_code}\n@enduml"
        
#         # Encode the PlantUML code
#         encoded = encode_plantuml(plantuml_code)
        
#         # Call the PlantUML server to generate the image
#         url = f"http://www.plantuml.com/plantuml/img/{encoded}"
#         response = requests.get(url)
        
#         if response.status_code == 200:
#             return Image.open(io.BytesIO(response.content))
#         else:
#             st.error(f"Error rendering PlantUML: {response.status_code}")
#             return None
#     except Exception as e:
#         st.error(f"Error rendering PlantUML: {str(e)}")
#         return None

# # Create the SDLC Advisor Agent
# def create_sdlc_advisor_agent(llm):
#     return Agent(
#         role="SDLC Methodology Expert",
#         goal="Recommend the best software development methodology based on project requirements",
#         backstory="""You are an expert in software development methodologies with years of 
#         experience in various industries. You analyze project requirements and constraints 
#         to recommend the most suitable SDLC model.""",
#         verbose=True,
#         llm=llm,
#         allow_delegation=False
#     )

# # Create the UML Generator Agent
# def create_uml_generator_agent(llm):
#     return Agent(
#         role="UML Diagram Expert",
#         goal="Generate accurate and comprehensive UML diagrams based on software product descriptions",
#         backstory="""You are a skilled software architect specialized in translating product 
#         requirements into UML diagrams. You have deep knowledge of UML notation and 
#         best practices for various diagram types.""",
#         verbose=True,
#         llm=llm,
#         allow_delegation=False
#     )

# # Create task for SDLC recommendation
# def create_sdlc_recommendation_task(agent, product_description):
#     return Task(
#         description=f"""
#         Analyze the following software product description and recommend the most appropriate 
#         Software Development Life Cycle (SDLC) methodology.
        
#         PRODUCT DESCRIPTION:
#         {product_description}
        
#         Provide a recommendation with justification in the following format:
        
#         RECOMMENDED SDLC: [Name of methodology]
        
#         JUSTIFICATION:
#         [2-3 paragraphs explaining why this methodology is best suited for the described product]
        
#         KEY BENEFITS:
#         - [Benefit 1]
#         - [Benefit 2]
#         - [Benefit 3]
        
#         POTENTIAL CHALLENGES:
#         - [Challenge 1]
#         - [Challenge 2]
#         """,
#         expected_output="RECOMMENDED SDLC: Agile\nJUSTIFICATION: ...\nKEY BENEFITS: ...\nPOTENTIAL CHALLENGES: ...",
#         agent=agent
#     )

# # Create task for UML diagram generation
# def create_uml_generation_task(agent, product_description, diagram_type):
#     return Task(
#         description=f"""
#         Generate a PlantUML code for a {diagram_type} diagram based on the following software product description.
        
#         PRODUCT DESCRIPTION:
#         {product_description}
        
#         REQUIREMENTS:
#         1. Create a complete and accurate {diagram_type} diagram that captures the key aspects of the product
#         2. Follow UML standards and best practices for {diagram_type} diagrams
#         3. Return ONLY the PlantUML code within @startuml and @enduml tags
#         4. Ensure the code is syntactically correct for the PlantUML renderer
#         5. Include appropriate relationships, attributes, and methods
        
#         RESPONSE FORMAT:
#         Begin your response with a brief explanation of the diagram, then provide ONLY the PlantUML code surrounded by ```plantuml tags.
#         """,
#         expected_output="A valid PlantUML code block starting with '@startuml' and ending with '@enduml'.",
#         agent=agent
#     )

# # Function to run the crew
# def run_crew(product_description, diagram_type):
#     llm = get_qwen_llm()
#     if not llm:
#         return None, None
    
#     try:
#         with st.spinner("Agents are analyzing your request..."):
#             # Create agents
#             sdlc_advisor = create_sdlc_advisor_agent(llm)
#             uml_generator = create_uml_generator_agent(llm)
            
#             # Create tasks
#             sdlc_task = create_sdlc_recommendation_task(sdlc_advisor, product_description)
#             uml_task = create_uml_generation_task(uml_generator, product_description, diagram_type)
            
#             # Create and run the crew
#             crew = Crew(
#                 agents=[sdlc_advisor, uml_generator],
#                 tasks=[sdlc_task, uml_task],
#                 verbose=1,
#                 process=Process.sequential  # Run tasks sequentially
#             )
            
#             # Start the crew and get results
#             result = crew.kickoff()
            
#             # Extract SDLC recommendation from the result
#             sdlc_result = result[0] if isinstance(result, list) else result
            
#             # Extract UML code from the result
#             uml_result = result[1] if isinstance(result, list) else ""
#             plantuml_code = extract_plantuml_code(uml_result)
            
#             return sdlc_result, plantuml_code
#     except Exception as e:
#         st.error(f"Error running crew: {str(e)}")
#         return f"Error: {str(e)}", None

# # Function to extract PlantUML code from agent response
# def extract_plantuml_code(response):
#     # First try to extract code between ```plantuml tags
#     plantuml_pattern = r"```plantuml\s*(.*?)\s*```"
#     match = re.search(plantuml_pattern, response, re.DOTALL)
    
#     if match:
#         return match.group(1)
    
#     # If that fails, try extracting between @startuml and @enduml tags
#     uml_pattern = r"@startuml\s*(.*?)\s*@enduml"
#     match = re.search(uml_pattern, response, re.DOTALL)
    
#     if match:
#         return f"@startuml\n{match.group(1)}\n@enduml"
    
#     # If no patterns match, return the whole response
#     # (the render function will add the @startuml tags)
#     return response

# # Define the Streamlit UI
# def main():
#     st.title("SmartSDLC: UML Generator & SDLC Advisor")
#     st.markdown("""
#     This tool helps you generate UML diagrams and recommends the best Software Development 
#     Life Cycle (SDLC) methodology based on your product description.
#     """)
    
#     # Input form
#     with st.form("input_form"):
#         product_description = st.text_area(
#             "Product Description", 
#             height=200,
#             placeholder="Describe your software product in detail..."
#         )
        
#         # Diagram type selection
#         diagram_types = [
#             "Use Case Diagram", 
#             "Class Diagram", 
#             "Sequence Diagram", 
#             "Component Diagram",
#             "Communication Diagram", 
#             "State Machine Diagram"
#         ]
#         diagram_type = st.selectbox("Select UML Diagram Type", diagram_types)
        
#         submitted = st.form_submit_button("Generate Recommendations")
    
#     # Process form submission
#     if submitted and product_description:
#         if len(product_description) < 50:
#             st.warning("Please provide a more detailed product description (at least 50 characters).")
#         else:
#             sdlc_result, plantuml_code = run_crew(product_description, diagram_type)
            
#             if sdlc_result and plantuml_code:
#                 # Display results in tabs
#                 tab1, tab2, tab3 = st.tabs(["SDLC Recommendation", "PlantUML Code", "UML Diagram"])
                
#                 with tab1:
#                     st.subheader("Recommended SDLC Model")
#                     st.markdown(sdlc_result)
                
#                 with tab2:
#                     st.subheader("Generated PlantUML Code")
#                     st.code(plantuml_code, language="plantuml")
                
#                 with tab3:
#                     st.subheader(f"Rendered {diagram_type}")
#                     with st.spinner("Rendering diagram..."):
#                         diagram = render_plantuml(plantuml_code)
#                         if diagram:
#                             st.image(diagram, use_column_width=True)
#                         else:
#                             st.error("Failed to render the UML diagram. Please check the PlantUML code for errors.")

# # Run the application
# if __name__ == "__main__":
#     main()