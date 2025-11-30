from groq import Groq
import streamlit as st
import os
import tempfile
import json
import requests
import tomllib
from langchain_groq import ChatGroq
import pandas as pd
import datetime



# create title for the streamlit app

st.title('Autonomous Customer Interviewer')

# create a description

st.write(f"""This app is designed to help you conduct customer interviews. It uses the Llama 3 model on Groq to generate questions, 
         execute the interview and summarize the interview. For more information, contact Dries Faems at https://www.linkedin.com/in/dries-faems-0371569/""")

groq_api_key = st.text_input('Please provide your Groq API Key. You can get a free API key at https://console.groq.com/playground', type="password")

painpoint = st.text_input('What is the painpoint, which you want to explore in the interview?')
customer_profile = st.text_input('What is the profile of the customer you want to interview?')
prior_learnings = st.text_input('What have you learned so far about the painpoint?')
    
if st.button('Start Interview'):
    
    os.environ["GROQ_API_KEY"] = groq_api_key
    client = Groq()
    GROQ_LLM = ChatGroq(model="openai/gpt-oss-20b")

    def llm_call(system_prompt: str, user_prompt: str) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        # Using LangChain Groq chat interface for a simple invoke
        result = GROQ_LLM.invoke(messages)
        # LangChain returns an AIMessage; extract content
        return getattr(result, "content", str(result))

    # Define OpenAI-style agent functions replacing CrewAI agents
    def generate_questions(painpoint: str, customer_profile: str) -> str:
        system = (
            "You are an expert at generating incisive customer interview questions. "
            "Follow best practices: seek information not confirmation; avoid selling; "
            "ask about past behavior; avoid could/would; request specific examples."
        )
        user = (
            f"Prepare a numbered list of 12-15 interview questions for a customer with profile: {customer_profile}. "
            f"Goal: understand painpoint: {painpoint}. Include probes to dig into when it occurs, hardest parts, attempted solutions, and desired improvements."
        )
        return llm_call(system, user)

    def conduct_interview(questions: str, painpoint: str, customer_profile: str) -> str:
        system = (
            "You simulate a realistic, semi-structured customer interview. "
            "Use the provided questions as a guide, add clarifying probes, and produce a readable transcript with Q: and A: lines."
        )
        user = (
            f"Customer profile: {customer_profile}. Painpoint: {painpoint}. Questions to guide the interview:\n{questions}\n"
            "Conduct the interview and produce an exhaustive transcript."
        )
        return llm_call(system, user)

    def analyze_interview(transcript: str, painpoint: str) -> str:
        system = (
            "You analyze customer interviews to extract key learnings. "
            "Focus on: when the painpoint occurs; hardest aspects; why unresolved; stakes and impact; and patterns."
        )
        user = (
            f"Analyze this interview transcript about painpoint '{painpoint}' and provide a structured summary with bullets and short sections.\n\n{transcript}"
        )
        return llm_call(system, user)

    def update_learnings(prior: str, new_learnings: str) -> str:
        system = (
            "You consolidate learnings into a single, coherent overview. "
            "Merge prior learnings with new insights, deduplicate, and present one integrated summary."
        )
        user = (
            f"Prior learnings:\n{prior}\n\nNew learnings from the latest interview:\n{new_learnings}\n\nProvide an updated, integrated overview."
        )
        return llm_call(system, user)
    
    # Sequential OpenAI-style agent pipeline
    questions_output = generate_questions(painpoint, customer_profile)
    interview_output = conduct_interview(questions_output, painpoint, customer_profile)
    analysis_output = analyze_interview(interview_output, painpoint)

    if prior_learnings == '':
        st.write(questions_output)
        st.write(interview_output)
        st.write(analysis_output)
    else:
        updated_learnings_output = update_learnings(prior_learnings, analysis_output)
        st.write(questions_output)
        st.write(interview_output)
        st.write(analysis_output)
        st.write(updated_learnings_output)

else:
    st.write('Please click the button to start the interview')
