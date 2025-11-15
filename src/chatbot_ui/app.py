import streamlit as st
import requests
from src.chatbot_ui.core.config import config


with st.sidebar:
    st.title("Chatbot Settigns")

    #Dropdown for Model Selection
    provider = st.selectbox("Provider", ["OpenAI", "Google", "Groq"])
    if provider == "OpenAI":
        model_name = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o"])
    elif provider == "Google":
        model_name = st.selectbox("Model", ["gemini-2.0-flash"])
    else:
        model_name = st.selectbox("Model", ["llama-3.1-8b-instant"])
    
    st.session_state.provider = provider
    st.session_state.model_name = model_name

def api_call(method, url, **kwargs):
    def _show_error_popup(message):
        """Show Error Message as PopUp in the Top-Right Corner"""
        st.session_state["error_popup"] = {
            "visible": True,
            "message": message,    
        }
    try:
        response = getattr(requests, method)(url, **kwargs)
        try:
            response_data = response.json()
        except requests.exceptions.JSONDecodeError:
            response_data = {"message": "Invalid response format from server"}
        if response.ok:
            return True, response_data
        return False, response_data
    except requests.exceptions.ConnectionError as e:
        _show_error_popup(f"Connection error, please check your network connection")
        return False, {"message": "Connection Error"}
    except requests.exceptions.Timeout as e:
        _show_error_popup(f"Timeout error, please try again later")
        return False, {"message": "Timeout Error"}
    except requests.exceptions.HTTPError as e:
        _show_error_popup(f"HTTP error, please check your request")
        return False, {"message": "HTTP Error"}
    except requests.exceptions.Exception as e:
        _show_error_popup(f"An unexpected error occurred")
        return False, {"message": "Unexpected Error"}
    

if "messages" not in st.session_state:
    st.session_state.messages = [
        {'role': 'assistant', 
        'content': 'Hello! How can I assist you today?'}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Hello! How can I assist you today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        #output = run_llm(client, st.session_state.messages)
        success, output = api_call("post", f"{config.API_URL}:{config.API_PORT}/chat", json={
            "provider": st.session_state.provider,
            "model_name": st.session_state.model_name,
            "messages": st.session_state.messages})
        answer = output["message"]
        if success:
            st.write(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})