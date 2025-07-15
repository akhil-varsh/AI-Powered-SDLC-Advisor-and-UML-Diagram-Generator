# import streamlit as st
# import streamlit.components.v1 as components

# st.title("SmartSDLC - Mermaid UML Diagram Generator")

# uml_code = st.text_area("Enter your Mermaid Code:", height=300, value="""
# sequenceDiagram
#     participant Alice
#     participant Bob
#     Alice->>Bob: Hello Bob, how are you?
#     Bob-->>Alice: I am good thanks!
# """)

# if st.button("Generate Diagram"):
#     mermaid_html = f"""
#     <div class="mermaid">
#     {uml_code}
#     </div>
#     <script type="module">
#       import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
#       mermaid.initialize({{startOnLoad:true}});
#     </script>
#     """
#     components.html(mermaid_html, height=600, scrolling=True)


# import streamlit as st
# import streamlit.components.v1 as components
# import base64
# import requests
# import os
# import io
# import logging
# import re
# import subprocess
# import sys
# import time
# from PIL import Image
# import tempfile

# # Set up logging with more detail
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# # Import local modules
# from model_api import call_model
# from crew_orchestration import run_crew_task

# # Page configuration with wide layout
# st.set_page_config(page_title="SmartSDLC", layout="wide", initial_sidebar_state="collapsed")

# # App title and description
# st.title("SmartSDLC: UML Generator & SDLC Advisor")

# # Save generated content in session state so it persists between reruns
# if 'mermaid_code' not in st.session_state:
#     st.session_state.mermaid_code = ""
# if 'sdlc_recommendation' not in st.session_state:
#     st.session_state.sdlc_recommendation = ""
# if 'generation_successful' not in st.session_state:
#     st.session_state.generation_successful = False
# if 'last_error' not in st.session_state:
#     st.session_state.last_error = None

# # Debug function to print session state
# def log_session_state():
#     logger.info(f"Generation successful: {st.session_state.generation_successful}")
#     logger.info(f"SDLC recommendation length: {len(st.session_state.sdlc_recommendation)}")
#     logger.info(f"Mermaid code length: {len(st.session_state.mermaid_code)}")
#     if st.session_state.last_error:
#         logger.error(f"Last error: {st.session_state.last_error}")

# # Check if Ollama is running
# @st.cache_data(ttl=60)
# def check_ollama_status():
#     try:
#         response = requests.get("http://localhost:11434/api/tags")
#         if response.status_code == 200:
#             models = response.json().get("models", [])
#             available_models = [model.get("name") for model in models]
#             if "qwen2.5:3b" in available_models:
#                 return True, "Qwen 2.5:3B model is available"
#             else:
#                 return False, "Qwen 2.5:3B model not found. Please run: ollama pull qwen2.5:3b"
#         return False, "Ollama is running but couldn't check models"
#     except Exception as e:
#         logger.error(f"Error checking Ollama status: {str(e)}")
#         return False, "Ollama server not detected. Please start Ollama with: ollama serve"

# # Function to save diagram as image
# def save_diagram_as_image(mermaid_code):
#     try:
#         # Generate a URL for the SVG using Mermaid Live
#         encoded_mermaid = base64.urlsafe_b64encode(mermaid_code.encode('utf-8')).decode('utf-8')
#         mermaid_live_url = f"https://mermaid.live/svg#pako:{encoded_mermaid}"
#         return mermaid_live_url
#     except Exception as e:
#         logger.error(f"Failed to save diagram as image: {str(e)}")
#         return None

# # Input parameters section
# with st.container():
#     st.header("Input Parameters")
    
#     # Check Ollama status and display results
#     ollama_ok, ollama_message = check_ollama_status()
#     if not ollama_ok:
#         st.warning(f"⚠️ {ollama_message}")
#     else:
#         st.success(f"✅ {ollama_message}")
    
#     # Form for user input
#     with st.form("input_form"):
#         # User inputs
#         product_description = st.text_area("Describe your software product:", 
#                                         height=120,
#                                         help="Provide details about your software product, its features, constraints, and requirements.")
        
#         # Create a row with multiple columns
#         col1, col2, col3 = st.columns([2, 1, 1])
        
#         # UML diagram type selection
#         with col1:
#             diagram_types = ["Use Case", "Class", "Sequence", "Component", "Communication", "State Machine"]
#             selected_diagram = st.selectbox("UML Diagram Type:", diagram_types)
        
#         # Model parameters
#         with col2:
#             temperature = st.slider("Temperature", min_value=0.1, max_value=1.0, value=0.7, step=0.1,
#                                 help="Higher = more creative, Lower = more deterministic")
#         with col3:
#             max_tokens = st.slider("Max Tokens", min_value=500, max_value=4000, value=2000, step=100,
#                                 help="Maximum output length")
        
#         # Form submission button
#         submit_button = st.form_submit_button("Generate")
    
#     # Process form submission
#     if submit_button and product_description:
#         if not ollama_ok:
#             st.error("Cannot generate without Ollama running with Qwen 2.5:3B model")
#         else:
#             try:
#                 with st.spinner("Working on your request... This may take a minute."):
#                     # Run the crew task to get both SDLC recommendation and Mermaid code
#                     result = run_crew_task(
#                         product_description, 
#                         selected_diagram,
#                         temperature=temperature,
#                         max_tokens=max_tokens
#                     )
                    
#                     if result and isinstance(result, dict) and 'sdlc_recommendation' in result and 'mermaid_code' in result:
#                         # Log the results for debugging
#                         logger.info(f"Got results from crew task: SDLC ({len(result['sdlc_recommendation'])} chars), Mermaid ({len(result['mermaid_code'])} chars)")
                        
#                         # Save the Mermaid code for the editor and session state
#                         current_dir = os.path.dirname(os.path.abspath(__file__))
#                         with open(os.path.join(current_dir, "latest_mermaid.txt"), "w") as f:
#                             f.write(result['mermaid_code'])
                        
#                         # Update session state
#                         st.session_state.mermaid_code = result['mermaid_code']
#                         st.session_state.sdlc_recommendation = result['sdlc_recommendation']
#                         st.session_state.generation_successful = True
#                         st.session_state.last_error = None
                        
#                         # Display success message
#                         st.success("✅ Generation successful! Diagram and SDLC recommendation ready.")
                        
#                         # Log session state for debugging
#                         log_session_state()
#                     else:
#                         error_msg = "Failed to generate results. The model did not return the expected output format."
#                         st.error(f"{error_msg} Please try again.")
#                         logger.error(f"{error_msg} Result: {result}")
#                         st.session_state.last_error = error_msg
#                         if result:
#                             st.write("Partial results received:")
#                             st.write(result)
#             except Exception as e:
#                 error_msg = f"An error occurred: {str(e)}"
#                 st.error(error_msg)
#                 st.write("Make sure the Ollama server is running with the Qwen 2.5:3B model loaded.")
#                 logger.exception("Error in form submission handler")
#                 st.session_state.last_error = error_msg

# # Output section with tabs for SDLC and UML
# if st.session_state.generation_successful:
#     # Create two columns for SDLC and UML
#     col1, col2 = st.columns(2)
    
#     # SDLC Recommendation
#     with col1:
#         st.header("SDLC Recommendation")
#         if st.session_state.sdlc_recommendation:
#             st.info(st.session_state.sdlc_recommendation)
#         else:
#             st.warning("No SDLC recommendation was generated.")
    
#     # UML Diagram
#     with col2:
#         st.header("Generated UML Diagram")
#         if st.session_state.mermaid_code:
#             # Render the diagram
#             mermaid_html = f"""
#             <div class="mermaid">
#             {st.session_state.mermaid_code}
#             </div>
#             <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
#             <script>
#               mermaid.initialize({{
#                 startOnLoad: true,
#                 theme: 'default',
#                 securityLevel: 'loose',
#                 fontFamily: 'monospace'
#               }});
#             </script>
#             """
#             components.html(mermaid_html, height=400, scrolling=True)
#         else:
#             st.warning("No UML diagram was generated.")
# else:
#     # Instructions when first loading
#     st.info("Fill in the form and click 'Generate' to start.")
    
#     # Example section (collapsible)
#     with st.expander("See Example"):
#         st.markdown("""
#         **Example Product Description:**
        
#         A mobile application that allows users to track their daily water intake, set reminders for drinking water, 
#         and view statistics about their hydration habits. The app should support user registration, multiple profiles, 
#         and sharing achievements on social media. It should also provide recommendations based on user activity levels 
#         and local weather conditions.
        
#         **Appropriate UML Diagram:** Class Diagram
#         """)

# # Mermaid code editor section (below outputs)
# if st.session_state.generation_successful and st.session_state.mermaid_code:
#     st.header("UML Diagram Editor")
    
#     edited_code = st.text_area("Edit Mermaid Code:", height=200, value=st.session_state.mermaid_code, key="mermaid_editor")
    
#     # Create a row of buttons
#     col1, col2, col3, col4 = st.columns(4)
    
#     # Update diagram button - Fixed rerun method
#     if col1.button("Update Diagram"):
#         st.session_state.mermaid_code = edited_code
#         st.rerun()  # Using st.rerun() instead of experimental_rerun()
    
#     # Copy button
#     if col2.button("Copy to Clipboard"):
#         st.success("Code copied to clipboard!")
#         # Fix: Pre-process the string outside the f-string to avoid backslash in expression
#         escaped_code = edited_code.replace('`', r'\`')
#         st.markdown(f"""
#         <script>
#             navigator.clipboard.writeText(`{escaped_code}`)
#                 .then(() => console.log('Copied to clipboard'))
#                 .catch(err => console.error('Failed to copy: ', err));
#         </script>
#         """, unsafe_allow_html=True)
    
#     # Download button
#     if col3.button("Download SVG"):
#         download_url = save_diagram_as_image(edited_code)
#         if download_url:
#             st.markdown(f"[Download SVG]({download_url})")
#             st.success("SVG is ready for download!")
    
#     # Open in Mermaid Live Editor
#     if col4.button("Open in Mermaid Live"):
#         encoded_mermaid = base64.urlsafe_b64encode(edited_code.encode('utf-8')).decode('utf-8')
#         mermaid_live_url = f"https://mermaid.live/edit#pako:{encoded_mermaid}"
#         st.markdown(f"[Open in Mermaid Live Editor]({mermaid_live_url})")
#         st.write("Link opened in a new tab.")

# # Debug section
# with st.expander("Debug Information", expanded=False):
#     st.write("Session state:")
#     st.write(f"- Generation successful: {st.session_state.generation_successful}")
#     st.write(f"- SDLC recommendation length: {len(st.session_state.sdlc_recommendation)}")
#     st.write(f"- Mermaid code length: {len(st.session_state.mermaid_code)}")
#     if st.session_state.last_error:
#         st.write(f"- Last error: {st.session_state.last_error}")
    
#     if st.button("Clear Session State"):
#         for key in ['mermaid_code', 'sdlc_recommendation', 'generation_successful', 'last_error']:
#             if key in st.session_state:
#                 del st.session_state[key]
#         st.success("Session state cleared! Please refresh the page.")
        
#     # Display raw content of session state
#     if st.checkbox("Show Raw Content"):
#         st.write("Raw SDLC Recommendation:")
#         st.code(st.session_state.sdlc_recommendation)
#         st.write("Raw Mermaid Code:")
#         st.code(st.session_state.mermaid_code)

# # Footer
# st.markdown("---")
# st.markdown("SmartSDLC - Powered by Qwen 2.5:3B, CrewAI and Mermaid")