import os
os.system("pip install groq")

import streamlit as st
from groq import Groq

# Initialize Groq client
client = Groq(api_key="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")

# Bot name
BOT_NAME = "Tabib"

# Developer name
DEVELOPER_NAME = "Rao Zain"

# Medical questioning pattern
MEDICAL_QUESTIONS = [
    "Where exactly is the problem located? (e.g., left temple, lower back)",
    "How would you describe it? (e.g., throbbing pain, sharp pain, dull ache)",
    "How long have you had this symptom?",
    "Are you experiencing any other symptoms along with this?"
]

# Symptom keywords list
SYMPTOM_KEYWORDS = [
    'fever', 'headache', 'pain', 'ache', 'nausea', 'dizziness',
    'cough', 'sore throat', 'rash', 'fatigue', 'vomiting',
    'diarrhea', 'shortness of breath', 'chest pain'
]

# Developer-related trigger phrases
DEVELOPER_QUESTIONS = [
    "who is your developer",
    "what is your developer name",
    "who created you",
    "who made you",
    "developer name",
    "your creator",
    "who designed you"
]

# Function to check if message asks about developer
def is_developer_question(text):
    text_lower = text.lower()
    return any(phrase in text_lower for phrase in DEVELOPER_QUESTIONS)

# Function to check for symptom keywords
def contains_symptom(text):
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in SYMPTOM_KEYWORDS)

# Function to query Groq if not a developer question
def query_groq(prompt, context=None):
    try:
        messages = [
            {
                "role": "system",
                "content": f"""You are {BOT_NAME}, a medical assistant. Follow these rules:
1. Provide general medical information about symptoms only
2. Always recommend consulting a doctor
3. Use simple language a patient can understand"""
            }
        ]
        if context:
            messages.append({"role": "assistant", "content": context})

        messages.append({"role": "user", "content": prompt})

        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama3-8b-8192",
            temperature=0.3,
            max_tokens=1024
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

# Streamlit App UI config
st.set_page_config(page_title="Tabib - Medical Assistant", page_icon="🩺")
st.title("🩺 Tabib - Medical Assistant")

# Session state initialization
if "in_question_flow" not in st.session_state:
    st.session_state.in_question_flow = False
    st.session_state.current_question = 0
    st.session_state.answers = []

# User input field
user_input = st.text_input("Your message", "")

if st.button("Send") and user_input:

    # Check if user asked about the developer
    if is_developer_question(user_input):
        st.markdown(f"**{BOT_NAME}:** My developer name is {DEVELOPER_NAME}.")

    # Greeting handler
    elif user_input.lower() in ["hi", "hello"]:
        st.session_state.in_question_flow = False
        st.session_state.current_question = 0
        st.session_state.answers = []
        st.markdown(f"**{BOT_NAME}:** Hello! I'm {BOT_NAME}, your medical assistant. Please describe your symptoms (e.g., 'I have a fever').")

    # Check for symptom-related messages
    elif not st.session_state.in_question_flow and contains_symptom(user_input):
        st.session_state.in_question_flow = True
        st.session_state.current_question = 0
        st.session_state.answers = [user_input]
        st.markdown(f"**{BOT_NAME}:** {MEDICAL_QUESTIONS[0]}")

    # Continue medical questioning flow
    elif st.session_state.in_question_flow:
        st.session_state.answers.append(user_input)
        if st.session_state.current_question < len(MEDICAL_QUESTIONS) - 1:
            st.session_state.current_question += 1
            next_q = MEDICAL_QUESTIONS[st.session_state.current_question]
            st.markdown(f"**{BOT_NAME}:** {next_q}")
        else:
            context = f"""Patient reported:
- Main symptom: {st.session_state.answers[0]}
- Location: {st.session_state.answers[1]}
- Description: {st.session_state.answers[2]}
- Duration: {st.session_state.answers[3]}
- Other symptoms: {st.session_state.answers[4] if len(st.session_state.answers) > 4 else 'None'}"""

            response = query_groq("Based on these symptoms, what could this indicate?", context)
            st.markdown(f"**{BOT_NAME}:** {response}")

            # Reset state after completing the questioning
            st.session_state.in_question_flow = False
            st.session_state.current_question = 0
            st.session_state.answers = []

    else:
        st.markdown(f"**{BOT_NAME}:** Please describe your symptoms (e.g., 'I have a fever') or type 'hi' to begin.")
        
