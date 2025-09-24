from groq import Groq
import streamlit as st
import os
import tempfile
from crewai import Crew, Agent, Task, Process
import json
import os
import requests
# from crewai_tools import tool  # Not needed in current implementation
# import tomllib  # Not used in current implementation
from langchain_groq import ChatGroq
import pandas as pd
import datetime
import time


# create title for the streamlit app

# Page configuration
st.set_page_config(
    page_title="Autonomous Customer Interviewer",
    page_icon="🎤",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .subtitle {
        font-size: 1.2rem;
        text-align: center;
        margin-bottom: 2rem;
        color: #666;
    }
    
    .info-box {
        background-color: #f0f8ff;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin: 1rem 0;
    }
    
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #ffc107;
        margin: 1rem 0;
    }
    
    .step-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #333;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<h1 class="main-header">🎤 Autonomous Customer Interviewer</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">AI-Powered Customer Interview Generation & Analysis</p>', unsafe_allow_html=True)

# Feature overview
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div class="feature-card">
        <h3>🤖 Latest AI Models</h3>
        <p>Powered by Groq's fastest LLMs including Llama 3.3 and Llama 4</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <h3>📝 Smart Questions</h3>
        <p>Generates tailored interview questions based on your specific painpoint</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <h3>📊 Instant Analysis</h3>
        <p>Automatically analyzes interviews and extracts key insights</p>
    </div>
    """, unsafe_allow_html=True)

# Instructions
st.markdown('<div class="step-header">🚀 Getting Started</div>', unsafe_allow_html=True)

# API Key section
st.markdown("""
<div class="info-box">
    <h4>📋 Step 1: Get Your Groq API Key</h4>
    <p>To use this app, you'll need a free Groq API key:</p>
    <ol>
        <li>Visit <a href="https://console.groq.com" target="_blank">console.groq.com</a></li>
        <li>Sign up for a free account</li>
        <li>Go to API Keys section</li>
        <li>Create a new API key</li>
        <li>Copy and paste it below (starts with "gsk_")</li>
    </ol>
    <p><strong>💡 Tip:</strong> Groq offers generous free tier limits, so you can test this app at no cost!</p>
</div>
""", unsafe_allow_html=True)

# API Key input
groq_api_key = st.text_input(
    "🔑 Enter your Groq API Key:", 
    type="password",
    placeholder="gsk_...",
    help="Your API key is never stored and only used for this session"
)

if groq_api_key:
    st.success("✅ API Key provided! You can now proceed with the interview setup.")
    
    # Interview setup section
    st.markdown('<div class="step-header">📝 Step 2: Interview Setup</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        painpoint = st.text_area(
            '🎯 What is the painpoint you want to explore?',
            placeholder="e.g., Difficulty in finding the right software solution for small businesses",
            height=100,
            help="Describe the specific problem or challenge you want to understand better"
        )
    
    with col2:
        customer_pofile = st.text_area(
            '👤 What is the profile of the customer you want to interview?',
            placeholder="e.g., Small business owners, 25-45 years old, tech-savvy, using multiple software tools",
            height=100,
            help="Describe the target customer demographics, role, experience level, etc."
        )
else:
    st.markdown("""
    <div class="warning-box">
        <strong>⚠️ API Key Required</strong><br>
        Please enter your Groq API key above to continue. Don't have one? It's free to get started!
    </div>
    """, unsafe_allow_html=True)

def log_usage(action, painpoint, customer_profile, file_path='usage_log.xlsx'):
    try:
        df = pd.read_excel(file_path)
    except FileNotFoundError:
        # Create new DataFrame if file doesn't exist
        df = pd.DataFrame(columns=['Timestamp', 'User', 'Action', 'Painpoint', 'Customer_Profile'])
    
    # Create a new record as a DataFrame
    new_record = pd.DataFrame({
        'Timestamp': [datetime.datetime.now()],
        'User': ['public_user'],  # Since we removed access code requirement
        'Action': [action],
        'Painpoint': [painpoint],
        'Customer_Profile': [customer_profile]
    })

    # add new record to the DataFrame
    df = pd.concat([df, new_record], ignore_index=True)

    # Save the DataFrame back to the Excel file
    df.to_excel(file_path, index=False)

# Interview execution section
if groq_api_key and painpoint and customer_pofile:
    st.markdown('<div class="step-header">🚀 Step 3: Generate Interview</div>', unsafe_allow_html=True)
    
    # Advanced options in an expander
    with st.expander("🔧 Advanced Options"):
        debug_mode = st.checkbox("🐛 Show available models (debug mode)")
        st.info("💡 The app will automatically select the best available model for optimal performance.")
    
    if st.button('🎯 Generate Customer Interview', type="primary", use_container_width=True):
        # Log usage
        log_usage('Interview Started', painpoint, customer_pofile)
        os.environ["GROQ_API_KEY"] = groq_api_key
        
        # Show progress
        with st.spinner('🔄 Initializing AI models and generating your interview...'):
            time.sleep(1)  # Brief pause for UX
        
        try:
            client = Groq(api_key=groq_api_key)
            
            # Option to list available models for debugging
            if debug_mode:
                try:
                    models_response = client.models.list()
                    st.write("**Available models from Groq API:**")
                    available_groq_models = []
                    for model in models_response.data:
                        available_groq_models.append(model.id)
                        st.write(f"- {model.id}")
                    
                    # Show what we're trying to use
                    st.write("**Models we're trying to use:**")
                    for model in available_models:
                        st.write(f"- {model}")
                except Exception as e:
                    st.warning(f"Could not list models: {str(e)}")
            
            # Try to use the latest models, with fallback options
            # Using groq/ prefix for LiteLLM compatibility
            available_models = [
                "groq/llama-3.3-70b-versatile",     # Llama 3 8B with 8192 context  
                "groq/openai/gpt-oss-20b"
            ]
            
            model_to_use = None
            for model in available_models:
                try:
                    # Test if model is available by creating the ChatGroq instance
                    GROQ_LLM = ChatGroq(
                        api_key=groq_api_key,
                        model=model,
                        temperature=0.1
                    )
                    
                    model_to_use = model
                    st.success(f"✅ Using model: {model}")
                    break
                except Exception as e:
                    if debug_mode:
                        st.warning(f"⚠️ Model {model} not available: {str(e)}")
                    continue
            
            if model_to_use is None:
                st.error("❌ No available models found. Please check your API key and model access permissions.")
                st.info("💡 Try updating your Groq API key or contact Groq support for model access.")
                st.stop()
                
        except Exception as e:
            st.error(f"❌ Error initializing Groq client: {str(e)}")
            st.info("💡 Please check your GROQ_API_KEY.")
            st.stop()
        
        # Create agents with progress tracking
        st.info("🤖 Creating AI agents for interview generation...")
        
        interview_question_generator = Agent(
            role='Generating interview questions',
            goal=f"""Prepare a list of interview questions to ask a specific customer profile about a specific painpoint.""", 
            backstory=f"""You are a great expert in generating interview questions to better understand the painpoints for a specific customer profile. You will prepare a list of questions to ask a specific customer about the provided painpoint
            Typical examples of questions are: (i) What is the hardest part of the job_to_be_done, (ii) When did you face this hardes part for the last time, (iii) What did you do to overcome this problem, (iv) What would you like to see improved in the future?. Based on your great experience, please think about additional questions that would be relevant to ask to better understand the pain points.
            Here are some specific guidelines to take into account for executing an excellent customer interview: (1) It is about getting information instead of confirmation, (2) A customer interview is not a sales pitch,
            (3) Ask questions about the past instead of the future, (4) Phrases such as 'could you' of 'would you'should be avoided, (5) Ask for specific examples""",
            verbose=True,
            llm=GROQ_LLM,
            allow_delegation=False,
            max_iter=5,
            memory=True,
        )

        customer_interviewer = Agent(
            role='Executing customer interviews',
            goal=f"""Conduct semi-structured customer interviews starting from the questions that are prepared by the interview question generator.""",
            backstory="""You are a great expert in conducting interviews with customers to better understand the painpoitns for a specific customer.
            You rely on the questions that are generated by the interview question generator. You can probe for additional questions to get a deep understanding of the underlying 
            pain points.  Here are some specific guidelines to take into account for executing an excellent customer interview: (1) It is about getting information instead of confirmation, (2) A customer interview is not a sales pitch,
            (3) Ask questions about the past instead of the future, (4) Phrases such as 'could you' of 'would you'should be avoided, (5) Ask for specific examples.""",
            verbose=True,
            llm=GROQ_LLM,
            allow_delegation=False,
            max_iter=5,
            memory=True,
        )

        interview_analyzer = Agent(
            role='Analyzing customer interviews',
            goal=f"""Analyze the customer interviews to identify the most important observations regarding the painpoints for the specific customer.""",
            backstory="""You are a great expert in analyzing customer interviews to identify the most pressing problems that a specific customer is facing.""",
            verbose=True,
            llm=GROQ_LLM,
            allow_delegation=False,
            max_iter=5,
            memory=True,
        )
        
        # Create tasks for the agents
        st.info("📋 Setting up interview tasks...")
        
        generate_interview_questions = Task(
            description=f"""Generate interview questions to ask customers about the following painpoint: {painpoint}. Here is a description of the customer profile: {customer_pofile}""",
            expected_output='As output, you provide a list of interview questions that can be used for the customer interview.',
            agent=interview_question_generator
        )

        interview_customer = Task(
            description=f"""Interview the customer to identify painpoints about the following painpoint: {painpoint}. Here is a description of the customer profile:
            {customer_pofile}. It is important to rely on the questions generated by the interview_question_generator.""",
            expected_output="""As output, you provide an exhaustive transcript of the interview.""",
            agent=customer_interviewer
        )

        analyze_interview = Task(
            description=f"""Analyze the customer interview that is executed by the customer_interviewer.""",
            expected_output='As output, you provide an overview of the most important observations identified in the interviews.',
            agent=interview_analyzer
        )

        # Instantiate the first crew with a sequential process
        crew = Crew(
            agents=[interview_question_generator, customer_interviewer, interview_analyzer],
            tasks=[generate_interview_questions, interview_customer, analyze_interview],
            process=Process.sequential,
            full_output=True,
            share_crew=False,
        )
        
        # Execute the interview generation
        st.info("🚀 Generating your customer interview...")
        
        with st.spinner("This may take a few minutes..."):
            results = crew.kickoff()
        
        # Enhanced output presentation
        st.success("✅ Interview generated successfully!")
        
        # Debug output to see what attributes are available
        if debug_mode:
            st.write("**Task output attributes:**")
            st.write(f"- generate_interview_questions.output type: {type(generate_interview_questions.output)}")
            st.write(f"- Available attributes: {dir(generate_interview_questions.output)}")
        
        # Try different ways to access the output
        def get_task_output(task_output):
            """Helper function to safely get task output"""
            if hasattr(task_output, 'raw_output'):
                return task_output.raw_output
            elif hasattr(task_output, 'raw'):
                return task_output.raw
            elif hasattr(task_output, 'result'):
                return task_output.result
            elif hasattr(task_output, 'output'):
                return task_output.output
            else:
                return str(task_output)
        
        # Interview Questions Section
        st.markdown('<div class="step-header">📝 Generated Interview Questions</div>', unsafe_allow_html=True)
        with st.container():
            st.markdown("""
            <div class="feature-card">
                <h4>🎯 Questions to Ask Your Customers</h4>
            </div>
            """, unsafe_allow_html=True)
            try:
                questions_output = get_task_output(generate_interview_questions.output)
                st.markdown(questions_output)
            except Exception as e:
                st.error(f"Error displaying questions: {e}")
                st.write("Raw task output:", generate_interview_questions.output)
        
        # Interview Simulation Section
        st.markdown('<div class="step-header">🎤 Simulated Interview</div>', unsafe_allow_html=True)
        with st.container():
            st.markdown("""
            <div class="feature-card">
                <h4>💬 Sample Interview Transcript</h4>
                <p>Here's how the interview might unfold with your target customer:</p>
            </div>
            """, unsafe_allow_html=True)
            try:
                interview_output = get_task_output(interview_customer.output)
                st.markdown(interview_output)
            except Exception as e:
                st.error(f"Error displaying interview: {e}")
                st.write("Raw task output:", interview_customer.output)
        
        # Analysis Section
        st.markdown('<div class="step-header">📊 Interview Analysis</div>', unsafe_allow_html=True)
        with st.container():
            st.markdown("""
            <div class="feature-card">
                <h4>🔍 Key Insights & Observations</h4>
                <p>Analysis of the most important findings from the interview:</p>
            </div>
            """, unsafe_allow_html=True)
            try:
                analysis_output = get_task_output(analyze_interview.output)
                st.markdown(analysis_output)
            except Exception as e:
                st.error(f"Error displaying analysis: {e}")
                st.write("Raw task output:", analyze_interview.output)
        
        # Call to action
        st.markdown("---")
        st.markdown("""
        <div class="info-box">
            <h4>🎉 What's Next?</h4>
            <p>Use these questions and insights to conduct real customer interviews. Remember to:</p>
            <ul>
                <li>Adapt questions based on the conversation flow</li>
                <li>Listen actively and ask follow-up questions</li>
                <li>Focus on understanding, not selling</li>
                <li>Record responses for later analysis</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

elif groq_api_key and (not painpoint or not customer_pofile):
    st.warning("🔔 Please fill in both the painpoint and customer profile to continue.")
else:
    st.info("👆 Please provide your Groq API key to get started.")
