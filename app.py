import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai

# 1. Setup the Page
st.set_page_config(page_title="InsightStream AI", layout="wide")
st.title("🚀 InsightStream AI")

# 2. Setup API Key (Check Secrets first, then Sidebar)
# If you put it in Streamlit Secrets, it will find it here.
api_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("Enter Gemini API Key", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        # Test if the key works by listing models (optional but good for debugging)
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.sidebar.error(f"🔑 API Key Error: {e}")
else:
    st.sidebar.warning("⚠️ Please enter an API key to use AI features.")

# 3. File Uploader
uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=['csv', 'xlsx'])

if uploaded_file is not None:
    # Load Data
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # 4. Show Data Summary
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Rows", len(df))
    col2.metric("Total Columns", len(df.columns))
    col3.metric("Missing Values", df.isna().sum().sum())

    # 5. AI Assistant Section
    st.divider()
    st.subheader("🤖 AI Data Assistant")
    
    if not api_key:
        st.info("Please enter your Gemini API Key in the sidebar to ask questions.")
    else:
        user_question = st.text_input("Ask a question about your data (e.g., 'What are the main trends?'):")
        
        if user_question:
            with st.spinner("AI is analyzing your data..."):
                try:
                    # We give the AI the first 5 rows and the summary stats
                    data_context = f"""
                    Data Summary:
                    {df.describe().to_string()}
                    
                    First 5 rows of data:
                    {df.head().to_string()}
                    """
                    
                    prompt = f"You are a data analyst. Based on this data:\n{data_context}\n\nUser Question: {user_question}"
                    
                    response = model.generate_content(prompt)
                    
                    if response.text:
                        st.markdown("### 💡 AI Response")
                        st.write(response.text)
                    else:
                        st.warning("The AI returned an empty response. Try rephrasing your question.")
                        
                except Exception as e:
                    st.error(f"❌ AI Error: {e}")
                    st.info("Tip: Make sure your API key is correct and you have internet access.")

    # 6. Data Explorer
    st.divider()
    st.subheader("🔍 Raw Data Explorer")
    st.dataframe(df)

else:
    st.info("Please upload a file to get started.")
