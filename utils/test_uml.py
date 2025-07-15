import streamlit as st
import streamlit.components.v1 as components

st.title("SmartSDLC - Mermaid UML Diagram Generator")

uml_code = st.text_area("Enter your Mermaid Code:", height=300, value="""
""")

if st.button("Generate Diagram"):
    mermaid_html = f"""
    <div class="mermaid">
    {uml_code}
    </div>
    <script type="module">
      import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
      mermaid.initialize({{startOnLoad:true}});
    </script>
    """
    components.html(mermaid_html, height=600, scrolling=True)
