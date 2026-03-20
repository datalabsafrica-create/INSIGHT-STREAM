import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import os

# 1. Setup the Page
st.set_page_config(page_title="InsightStream AI", layout="wide")
st.title("🚀 InsightStream AI")
st.markdown("Upload your data and let AI find the hidden stories.")

# 2. Sidebar for API Key
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    if api_key:
        genai.configure(api_key=api_key)

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

    # 5. Interactive Charts
    st.subheader("📊 Data Visualization")
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if numeric_cols:
        selected_col = st.selectbox("Select a column to visualize", numeric_cols)
        fig = px.histogram(df, x=selected_col, title=f"Distribution of {selected_col}", 
                           color_discrete_sequence=['#3b82f6'])
        st.plotly_chart(fig, use_container_width=True)
    
    # 6. AI Insights (The "Magic" part)
    if api_key:
        st.subheader("🤖 AI Data Assistant")
        user_question = st.text_input("Ask a question about your data:")
        
        if user_question:
            model = genai.GenerativeModel('gemini-1.5-flash')
            # Give the AI a "snippet" of the data to look at
            data_summary = df.describe().to_string()
            prompt = f"Here is a summary of my data:\n{data_summary}\n\nQuestion: {user_question}"
            
            with st.spinner("AI is thinking..."):
                response = model.generate_content(prompt)
                st.write(response.text)
    else:
        st.info("💡 Enter an API key in the sidebar to unlock AI insights!")

    # 7. Data Explorer
    st.subheader("🔍 Raw Data Explorer")
    st.dataframe(df)

else:
    st.info("Please upload a file to get started.")
