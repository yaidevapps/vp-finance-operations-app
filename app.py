import streamlit as st
import requests
import json
import os
from typing import Optional

class LangflowClient:
    def __init__(self, base_url: str, application_token: str):
        self.base_url = base_url
        self.application_token = application_token
        
    def run_flow(
        self,
        message: str,
        endpoint: str,
        output_type: str = "chat",
        input_type: str = "chat",
        tweaks: Optional[dict] = None
    ) -> dict:
        """Run a flow with a given message and optional tweaks."""
        api_url = f"{self.base_url}/lf/cd71f509-33bf-4839-9b28-c8ecef44c7ee/api/v1/run/{endpoint}"
        
        payload = {
            "input_value": message,
            "output_type": output_type,
            "input_type": input_type,
        }
        
        if tweaks:
            payload["tweaks"] = tweaks
            
        headers = {
            "Authorization": f"Bearer {self.application_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(api_url, json=payload, headers=headers)
        return response.json()

# Page config
st.set_page_config(page_title="Datastax Langflow Chat", page_icon="💬")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar with app information
with st.sidebar:
    st.title("💬 Datastax Langflow Chat")
    st.markdown("""
    This is a chat application powered by Datastax Langflow.
    
    Enter your message in the chat input below to start the conversation!
    """)

# Main chat interface
st.title("💬 Mark's V.P. of Finance & Operations Assistant")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to discuss?"):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Get API response
    client = LangflowClient(
        base_url="https://api.langflow.astra.datastax.com",
        application_token=st.secrets["DATASTAX_TOKEN"]
    )
    
    tweaks = {
        "ChatInput-c1hCe": {},
        "ChatOutput-LYW8u": {},
        "Prompt-pVgGQ": {},
        "GoogleGenerativeAIModel-oCqMu": {},
        "Memory-TKh6U": {}
    }
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.run_flow(
                    message=prompt,
                    endpoint="mark_cristalli",
                    tweaks=tweaks
                )
                
                # Extract the message from the response
                if response and "outputs" in response:
                    flow_outputs = response["outputs"][0]
                    first_component_outputs = flow_outputs["outputs"][0]
                    output = first_component_outputs["outputs"]["message"]["message"]["text"]
                    st.markdown(output)
                    st.session_state.messages.append({"role": "assistant", "content": output})
                else:
                    st.error("Invalid response format from the API")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")