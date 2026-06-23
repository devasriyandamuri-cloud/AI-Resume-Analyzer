
import streamlit as st
import PyPDF2 as pdf
import google.generativeai as genai
import matplotlib.pyplot as plt
import re
import os

# ఇది .env ఫైల్ లేదా స్ట్రీమ్‌లిట్ సీక్రెట్స్ నుండి కీని సేఫ్ గా తీసుకుంటుంది
GENAI_API_KEY = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", "")
genai.configure(api_key=GENAI_API_KEY)

def get_gemini_response(input_text, pdf_content, prompt):
    # Ee model name 'gemini-2.5-flash' anni kotha python versions lo support chestundi
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    response = model.generate_content([input_text, pdf_content, prompt])
    return response.text

def extract_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        text += str(reader.pages[page].extract_text())
    return text

def parse_match_percentage(text):
    match = re.search(r'(\d+)%', text)
    if match:
        return int(match.group(1))
    return 50  

# ==========================================
# 2. APP LAYOUT (DASHBOARD)
# ==========================================
st.set_page_config(page_title="AI Resume Analyzer", layout="wide")
st.title("🤖 AI Resume & Job Description Analyzer")
st.subheader("Evaluate your profile for Software Engineering Internships")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📋 Step 1: Paste Job Description")
    jd_input = st.text_area("Paste target job specifications here:", height=250, placeholder="Looking for an engineering intern with Python...")

with col2:
    st.markdown("### 📄 Step 2: Upload Resume")
    uploaded_file = st.file_uploader("Upload your resume (PDF only):", type=["pdf"])

st.markdown("---")

# ==========================================
# 3. INTERACTIVE ANALYSIS & PIE CHART
# ==========================================
if uploaded_file is not None and jd_input != "":
    resume_text = extract_pdf_text(uploaded_file)
    
    st.markdown("### 🧠 Step 3: Core Evaluation Dashboard")
    btn_analyze = st.button("🚀 Analyze Alignment Metrics", use_container_width=True)
    
    if btn_analyze:
        with st.spinner("Calculating match statistics and processing files..."):
            
            prompt_analysis = f"Analyze this resume against the job description. First line MUST strictly follow this exact format: 'MATCH PERCENTAGE: XX%'. Then give bullet points of strengths and weaknesses."
            ai_analysis_result = get_gemini_response(jd_input, resume_text, prompt_analysis)
            
            res_col1, res_col2 = st.columns([2, 1])
            
            with res_col1:
                st.markdown("#### 📊 Evaluation Summary")
                st.write(ai_analysis_result)
                
            with res_col2:
                st.markdown("#### 🎯 Score Breakdown")
                score = parse_match_percentage(ai_analysis_result)
                gap = 100 - score
                
                fig, ax = plt.subplots(figsize=(4, 4))
                ax.pie([score, gap], labels=['Match', 'Gap'], autopct='%1.1f%%', startangle=90, colors=['#2ecc71', '#e74c3c'], textprops={'fontsize': 12})
                ax.axis('equal')
                st.pyplot(fig)

    # ==========================================
   # ==========================================
    # 4. SIDEBAR CONVERSATIONAL CHATBOT
    # ==========================================
    with st.sidebar:
        st.title("💬 Resume Assistant Chat")
        st.markdown("Ask contextual questions regarding how to adjust your projects or skills.")
        
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        user_query = st.chat_input("Ask about adding key achievements...")
        if user_query:
            with st.chat_message("user"):
                st.markdown(user_query)
            st.session_state.messages.append({"role": "user", "content": user_query})
            
            with st.chat_message("assistant"):
                chatbot_context_prompt = f"The user's resume says: {resume_text}. The job description states: {jd_input}. Act as a helpful career mentor and answer this specific question: {user_query}"
                bot_response = get_gemini_response("", "", chatbot_context_prompt)
                st.markdown(bot_response)
            st.session_state.messages.append({"role": "assistant", "content": bot_response})
