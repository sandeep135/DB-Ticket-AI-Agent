import streamlit as st
import time
import openai
from app.agents import graph 

   

st.title("DEUTSCHE BAHN TICKET AGENT")

question = st.text_input("Enter your ticket inquiries:")

def ai_assistant(question):
    result = graph.invoke({"messages": question})     
    yield result["messages"][-1].content


if st.button("Ask"):
    if question:
        with st.spinner("I am analyzing your request.Please wait..."):
            # Placeholder for the response
            response_placeholder = st.empty()            
           
            response_generator = ai_assistant(question)
            with st.spinner("Almost there...."):
                    

                    response_placeholder.write_stream(response_generator)