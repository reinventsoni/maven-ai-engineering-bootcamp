from sys import exception
import streamlit as st
from openai import OpenAI
from google import genai
from groq import Groq
import requests

from core.config import config

# Let's create a side bar with a dropdown for the model list and providers
with st.sidebar:
    st.title("Choose your LLM Provider, Model and Settings")
    # Dropdown for model
    provider = st.selectbox("Provider", ["OpenAI", "Google", "Groq"])
    if provider == "OpenAI":
        model_name = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o"])
    elif provider == "Groq":
        model_name = st.selectbox("Model", ["llama-3.3-70b-versatile"])
    else:
        model_name = st.selectbox("Model", ["gemini-2.0-flash"])
    
    # Max Tokens Numeric Input - Common for all Providers and Models
    temperature = st.slider("Choose Temperature (0.0 - 2.0)", min_value=0.0, max_value=2.0, value=0.5, step=0.1)
    max_output_tokens = st.number_input("Maximum Tokens (100 - 1000)", min_value=100, max_value=1000, value=150, step=10)
    
    # Save Provider and Model name to the session state
    st.session_state.provider = provider
    st.session_state.model_name = model_name
    st.session_state.temperature = temperature
    st.session_state.max_output_tokens = max_output_tokens

def api_call(method, url, **kwargs):
    def _show_error_popup(message):
        """Show Error Message as a Popup in the top-right corner"""
        st.session_state["error_popup"] = {
            "visible":True,
            "message":message
        }
    try:
        response = getattr(requests, method)(url, **kwargs)
        try:
            response_data = response.json()
        except requests.exceptions.JSONDecodeError:
            response_data = {"message": "Invalid JSON response from the API"}
        
        if response.ok:
            return True, response_data
        return False, response_data

    except requests.exceptions.ConnectionError:
        _show_error_popup("Connection Error. Please check your network connection")
        return False, {"message": "Connection Error"}
    except requests.exceptions.Timeout:
        _show_error_popup("Request Timeout. Please try again later")
        return False, {"message": "Request Timeout"}
    except Exception as e:
        _show_error_popup(f"An error occurred: {str(e)}")
        return False, {"message": str(e)}
  


if "messages" not in st.session_state:
    st.session_state.messages = [
    {
        "role": "assistant",
        "content": "Hello! How can I help you today?"
    }]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
    
if prompt := st.chat_input("Hello! How can I assist you today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        output = api_call("post", f"{config.API_URL}/chat", json={"provider": st.session_state.provider, "model_name": st.session_state.model_name, "messages": st.session_state.messages, "temperature": st.session_state.temperature, "max_output_tokens": st.session_state.max_output_tokens})
        response_data = output[1]
        answer = response_data["message"]
        st.write(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})