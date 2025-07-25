import os
import streamlit as st
from langchain.chat_models import ChatOpenAI

# Load OpenAI API key from environment
openai_api_key = os.getenv("OPENAI_API_KEY")

# Set up the chatbot
llm = ChatOpenAI(api_key=openai_api_key, temperature=0)

st.title("Resume Chatbot")

user_input = st.text_input("Ask something about your resume:")

if user_input:
    response = llm.invoke(user_input)
    st.write(response.content)