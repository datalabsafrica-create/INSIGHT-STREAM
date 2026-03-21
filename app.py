import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import google.generativeai as genai
import io

# 1. Page Config
st.set_page_config(page_title="Expert BI Analyst Pro", layout="wide", page_icon="🧠")

st.markdown("""
    <style>
    .report-text { background-color: #ffffff; padding: 30px; border-radius: 10px; border: 1px solid #e2e8f0; line-height: 1.6; color: #1e293b; }
    .audit-log { font-family: monospace; font-size: 0.85rem; background-color: #f1f5f9; padding: 10px; border-radius: 5px; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #f8fafc; border-radius: 5px 5px 0 0; padding: 10px 20px; }
    .stTabs [aria-selected="true"] { background-color: #ffffff; border-bottom: 2px solid #3b82f6; }
    </style>
    """, unsafe_allow_html=True)

st.title("🧠 Expert Business Intelligence Analyst")

# 2. Sidebar for Configuration
with st.sidebar:
    st.header("🔑 Configuration")
    api_key = st.text_input("Enter Gemini API Key", type="password", help="Get your key at aistudio.google.com")
    st.divider()
    st.header("📁 Data Source")
    uploaded_file = st.file_uploader("Upload Dataset", type=['csv', 'xlsx'])
    
    if api_key:
        genai.configure(api_key=api_key)
        st.success("AI Engine Ready")
    else:
        st.warning("AI features require an API Key.")

# --- DATA PROCESSING ENGINE ---
def run_data_audit(df_input):
    df = df_input.copy()
    audit_trail = []
    report = {"total_rows": len(df), "missing_handled": 0, "duplicates_removed": 0, "outliers_detected": 0}
    
    # Duplicate Handling
    initial_count = len(df)
    df = df.drop_duplicates()
    report["duplicates_removed"] = initial_count - len(df)
    
    # Missing Values
    for col in df.columns:
        null_count = df[col].isna().sum()
        if null_count > 0:
            report["missing_handled"] += null_count
            if df[col].dtype in ['float64', 'int64']:
                df[col] = df[col].fillna(df[col].median())
            else:
                df[col] = df[col].fillna("Unknown")
    
    # Quality Score
    total_cells = df.size
    total_issues = report["missing_handled"] + report["duplicates_removed"]
    quality_score = max(0, int((1 - (total_issues / total_cells)) * 100))
    
    return df, report, quality_score

# --- APP UI LOGIC ---
if uploaded_file:
    # Load Data
    if "df_raw" not in st.session_state:
        if uploaded_file.name.endswith('.csv'):
            st.session_state.df_raw = pd.read_csv(uploaded_file)
        else:
            st.session_state.df_raw = pd.read_excel(uploaded_file)

    df_raw = st.session_state.df_raw

    # Create Tabs
    t1, t2, t3, t4 = st.tabs(["🏠 Overview & Audit", "📈 Visualizer", "🔍 Explorer", "🧠 AI BI Report"])

    # --- TAB 1: OVERVIEW & AUDIT ---
    with t1:
        st.subheader("📊 Data Quality Audit")
        cleaned_df, summary, score = run_data_audit(df_raw)
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Quality Score", f"{score}/100")
        m2.metric("Rows Processed", summary["total_rows"])
        m3.metric("Missing Handled", summary["missing_handled"])
        m4.metric("Duplicates Removed", summary["duplicates_removed"])
        
        st.divider()
        st.subheader("Data Preview")
        st.dataframe(df_raw.head(10), use_container_width=True)

    # --- TAB 2: VISUALIZER ---
    with t2:
        st.subheader("Interactive Charts")
        num_cols = df_raw.select_dtypes(include=['number']).columns.tolist()
        if num_cols:
            c1, c2 = st.columns([1, 3])
            with c1:
                x_axis = st.selectbox("X-Axis", df_raw.columns)
                y_axis = st.selectbox("Y-Axis", num_cols)
                chart_type = st.radio("Type", ["Bar", "Line", "Scatter"])
            with c2:
                if chart_type == "Bar": fig = px.bar(df_raw, x=x_axis, y=y_axis, template="plotly_white")
                elif chart_type == "Line": fig = px.line(df_raw, x=x_axis, y=y_axis, template="plotly_white")
                else: fig = px.scatter(df_raw, x=x_axis, y=y_axis, template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)

    # --- TAB 3: EXPLORER ---
    with t3:
        st.subheader("Raw Data Explorer")
        st.dataframe(df_raw, use_container_width=True)

    # --- TAB 4: AI BI REPORT (YOUR CUSTOM PROMPT) ---
    with t4:
        st.subheader("🧠 Comprehensive AI Business Intelligence Report")
        
        if not api_key:
            st.info("Please enter your Gemini API Key in the sidebar to generate the full report.")
        else:
            if st.button("🚀 Generate Full Structured Report"):
                with st.spinner("Expert Analyst is reading the entire dataset and drafting the report..."):
                    try:
                        # Prepare data context (CSV format)
                        csv_buffer = io.StringIO()
                        df_raw.to_csv(csv_buffer, index=False)
                        csv_data = csv_buffer.getvalue()

                        # YOUR CUSTOM PROMPT
                        base_prompt = """
                        You are an expert business intelligence analyst. Read the ENTIRE dataset provided below and generate a COMPLETE report. 
                        Do not provide only a summary. Do not skip rows, columns, sheets, or important patterns. 
                        If the output is long, return it in Part 1, Part 2, Part 3, etc. so that no findings are omitted.

                        Cover:
                        - Executive summary
                        - Dataset overview
                        - Data quality findings
                        - Detailed analysis across all major columns and sheets
                        - Trends and patterns
                        - Risks and anomalies
                        - Recommendations
                        - Final conclusion

                        Be detailed, structured, and exhaustive.
                        
                        REPORT FORMAT:
                        A. Executive Summary
                        B. Dataset Overview
                        C. Data Quality Findings
                        D. Detailed Analytical Findings
                        E. Trends and Patterns
                        F. Risks and Anomalies
                        G. Recommendations
                        H. Final Conclusion
                        """
                        
                        model = genai.GenerativeModel('gemini-1.5-pro')
                        full_prompt = f"{base_prompt}\n\nDATASET:\n{csv_data}"
                        
                        response = model.generate_content(full_prompt)
                        
                        st.markdown(f"<div class='report-text'>{response.text}</div>", unsafe_allow_html=True)
                        
                        st.download_button("📥 Download Full Report (.txt)", response.text, "BI_Report.txt")
                        
                    except Exception as e:
                        st.error(f"AI Engine Error: {e}")

else:
    st.info("👋 Welcome! Please upload a dataset in the sidebar to begin.")
