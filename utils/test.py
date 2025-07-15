# import streamlit as st
# import asyncio
# import base64
# import zlib
# import requests
# from crewai import Agent, Task, Crew
# from litellm import completion
# import logging
# from typing import Dict, Any, Optional
# from pydantic import BaseModel

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Pydantic model for input validation
# class UserInput(BaseModel):
#     description: str
#     diagram_type: str

# # Function to call Qwen2.5:3B model via Ollama
# async def call_deepseek(prompt: str, max_tokens: int = 1000) -> Optional[str]:
#     try:
#         response = await completion(
#             model="ollama/qwen2.5:3b",
#             messages=[{"role": "user", "content": prompt}],
#             api_base="http://localhost:11434",
#             max_tokens=max_tokens,
#             format="json",
#             api_key="None"  # Explicitly set to None to avoid OpenAI key requirement
#         )
#         return response.choices[0].message.content
#     except Exception as e:
#         logger.error(f"Error calling Qwen2.5:3B model: {str(e)}")
#         return None

# # Function to encode PlantUML code
# def encode_plantuml(plantuml_code: str) -> str:
#     try:
#         compressed = zlib.compress(plantuml_code.encode('utf-8'))
#         encoded = base64.b64encode(compressed).decode('ascii')
#         return encoded
#     except Exception as e:
#         logger.error(f"Error encoding PlantUML code: {str(e)}")
#         return ""

# # Function to get PlantUML diagram image
# def get_plantuml_image(plantuml_code: str) -> Optional[str]:
#     try:
#         encoded = encode_plantuml(plantuml_code)
#         if not encoded:
#             return None
#         url = f"http://www.plantuml.com/plantuml/png/{encoded}"
#         response = requests.get(url)
#         if response.status_code == 200:
#             return url
#         return None
#     except Exception as e:
#         logger.error(f"Error retrieving PlantUML image: {str(e)}")
#         return None

# # CrewAI Agent: SDLC Recommender
# def create_sdlc_agent() -> Agent:
#     return Agent(
#         role="SDLC Recommender",
#         goal="Recommend the best SDLC model based on project description",
#         backstory="Experienced project manager with expertise in software development methodologies",
#         verbose=True,
#         allow_delegation=False
#     )

# # CrewAI Agent: UML Generator
# def create_uml_agent() -> Agent:
#     return Agent(
#         role="UML Generator",
#         goal="Generate PlantUML code for the specified UML diagram type",
#         backstory="Expert in software architecture and UML diagram creation",
#         verbose=True,
#         allow_delegation=False
#     )

# # Task: Recommend SDLC
# def create_sdlc_task(description: str, agent: Agent) -> Task:
#     prompt = f"""Given this project description: {description}
#     Recommend the best SDLC model (Agile, Waterfall, Spiral, etc.) with a brief explanation.
#     Return JSON: {{"model": "recommended_model", "explanation": "brief_explanation"}}"""
    
#     return Task(
#         description=prompt,
#         agent=agent,
#         expected_output="JSON object with recommended SDLC model and explanation"
#     )

# # Task: Generate UML
# def create_uml_task(description: str, diagram_type: str, agent: Agent) -> Task:
#     prompt = f"""Given this project description: {description}
#     Generate PlantUML code for a {diagram_type} diagram.
#     Return JSON: {{"plantuml_code": "generated_code"}}"""
    
#     return Task(
#         description=prompt,
#         agent=agent,
#         expected_output="JSON object with PlantUML code"
#     )

# # Streamlit App
# def main():
#     st.title("SmartSDLC: UML Generator and SDLC Advisor")
    
#     # Input form
#     with st.form("sdlc_form"):
#         description = st.text_area("Project Description", height=200, 
#                                  placeholder="Enter your software product description...")
#         diagram_type = st.selectbox("UML Diagram Type", 
#                                   ["Use Case", "Class", "Sequence", "Component", 
#                                    "Communication", "State Machine"])
#         submit = st.form_submit_button("Generate")
    
#     if submit and description and diagram_type:
#         try:
#             # Validate input
#             user_input = UserInput(description=description, diagram_type=diagram_type)
            
#             # Create agents
#             sdlc_agent = create_sdlc_agent()
#             uml_agent = create_uml_agent()
            
#             # Create tasks
#             sdlc_task = create_sdlc_task(description, sdlc_agent)
#             uml_task = create_uml_task(description, diagram_type, uml_agent)
            
#             # Create and run crew
#             crew = Crew(
#                 agents=[sdlc_agent, uml_agent],
#                 tasks=[sdlc_task, uml_task],
#                 verbose=True,
#             )
            
#             with st.spinner("Generating recommendations and UML diagram..."):
#                 results = crew.kickoff()
                
#                 # Process SDLC recommendation
#                 sdlc_result = results.tasks[0].output
#                 if sdlc_result:
#                     sdlc_data = eval(sdlc_result)  # Safe since we control the JSON
#                     st.subheader("Recommended SDLC Model")
#                     st.write(f"**Model**: {sdlc_data['model']}")
#                     st.write(f"**Explanation**: {sdlc_data['explanation']}")
                
#                 # Process UML diagram
#                 uml_result = results.tasks[1].output
#                 if uml_result:
#                     uml_data = eval(uml_result)  # Safe since we control the JSON
#                     plantuml_code = uml_data['plantuml_code']
                    
#                     st.subheader("Generated PlantUML Code")
#                     st.code(plantuml_code, language="plantuml")
                    
#                     # Render and display diagram
#                     image_url = get_plantuml_image(plantuml_code)
#                     if image_url:
#                         st.subheader("Rendered UML Diagram")
#                         st.image(image_url)
#                     else:
#                         st.error("Failed to render UML diagram")
                        
#         except Exception as e:
#             st.error(f"An error occurred: {str(e)}")
#             logger.error(f"Application error: {str(e)}")

# if __name__ == "__main__":
#     main()