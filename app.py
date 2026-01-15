import streamlit as st
import docx  # For GREENWICH.docx
from groq import Groq
import os

# --- 1. PAGE CONFIG & STYLE ---
st.set_page_config(page_title="Greenwich Navigator", page_icon="🏫", layout="centered")

st.markdown("""
    <style>
    .main-title { font-size: 3rem !important; font-weight: 800 !important; color: #00472F; text-align: center; }
    .sub-text { text-align: center; color: #DAA520; font-size: 1.1rem; font-weight: 600; letter-spacing: 2px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. KNOWLEDGE ENGINE (DOCX ONLY) ---
DOCX_FILE = "GREENWICH.docx"

@st.cache_data
def load_greenwich_data():
    if not os.path.exists(DOCX_FILE):
        return None
    
    doc = docx.Document(DOCX_FILE)
    full_text = []
    for para in doc.paragraphs:
        if para.text.strip():  # Only add non-empty lines
            full_text.append(para.text)
    
    return "\n".join(full_text)

knowledge_base = load_greenwich_data()

# --- 3. GROQ CLIENT ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 4. MAIN INTERFACE ---
st.markdown('<p class="main-title">Greenwich Navigator</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">Official Word-Doc Based Advisor</p>', unsafe_allow_html=True)

if not knowledge_base:
    st.error(f"❌ File `{DOCX_FILE}` not found. Please upload it to your project folder.")
    st.stop()

# Initialize Chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I have loaded the **GREEENWICH.docx** manual. How can I help you with policies today?"}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Input & Logic
if prompt := st.chat_input("Ask me anything from the Greenwich doc..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_box = st.empty()
        full_response = ""
        
        try:
            stream = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": f"You are the Greenwich Navigator. Use ONLY this text to answer: {knowledge_base[:20000]}. Be formal and precise."},
                    {"role": "user", "content": prompt}
                ],
                stream=True, 
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    response_box.markdown(full_response + "▌")
            
            response_box.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Error: {e}")
