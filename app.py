import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import google.generativeai as genai
import io

# 1. Page Config
st.set_page_config(page_title="Expert BI Analyst Pro", layout="wide", page_icon="🧠")

# Custom CSS for High-Visibility Error Highlighting
st.markdown("""
    <style>
    .report-text { background-color: #ffffff; padding: 30px; border-radius: 10px; border: 1px solid #e2e8f0; line-height: 1.6; color: #1e293b; }
    .error-highlight { color: #ef4444; font-weight: bold; background-color: #fee2e2; padding: 2px 4px; border-radius: 3px; }
    .audit-log { font-family: monospace; font-size: 0.85rem; background-color: #f1f5f9; padding: 10px; border-radius: 5px; border-left: 4px solid #ef4444; margin-bottom: 5px; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

st.title("🧠 Expert Business Intelligence Analyst")

# 2. Sidebar for Configuration & Upload
with st.sidebar:
    st.header("🔑 AI Setup")
    api_key = st.text_input("Enter Gemini API Key", type="password", help="Get your key at aistudio.google.com")
    if api_key:
        genai.configure(api_key=api_key)
        st.success("AI Engine Ready")
    
    st.divider()
    st.header("📁 Step 1: Data Upload")
    uploaded_file = st.file_uploader("Upload CSV or Excel file", type=['csv', 'xlsx'])
    
    if uploaded_file:
        st.info(f"File: {uploaded_file.name}")

# --- DATA PROCESSING ENGINE ---
def run_data_audit(df_input):
    df = df_input.copy()
    audit_trail = []
    report = {"total_rows": len(df), "missing_handled": 0, "duplicates_removed": 0, "outliers_detected": 0}
    
    # Initialize Quality Flag
    df['dq_flag'] = 'clean'

    # 1. Duplicate Handling
    initial_count = len(df)
    df = df.drop_duplicates()
    report["duplicates_removed"] = initial_count - len(df)
    if report["duplicates_removed"] > 0:
        audit_trail.append(f"⚠️ Removed {report['duplicates_removed']} exact duplicate rows.")
    
    # 2. Missing Values & Type Validation
    for col in df.columns:
        if col == 'dq_flag': continue
        null_count = df[col].isna().sum()
        if null_count > 0:
            report["missing_handled"] += null_count
            df.loc[df[col].isna(), 'dq_flag'] = 'error'
            if df[col].dtype in ['float64', 'int64']:
                df[col] = df[col].fillna(df[col].median())
                audit_trail.append(f"⚠️ Filled {null_count} missing values in '{col}' with Median.")
            else:
                df[col] = df[col].fillna("Unknown")
                audit_trail.append(f"⚠️ Filled {null_count} missing values in '{col}' with 'Unknown'.")
    
    # 3. Outlier Detection (IQR)
    for col in df.select_dtypes(include=[np.number]).columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        outliers = df[(df[col] < lower) | (df[col] > upper)]
        if not outliers.empty:
            report["outliers_detected"] += len(outliers)
            df.loc[outliers.index, 'dq_flag'] = 'needs_review'
            audit_trail.append(f"🚩 Flagged {len(outliers)} outliers in '{col}'.")
    
    # Quality Score
    total_cells = df.size
    total_issues = report["missing_handled"] + report["duplicates_removed"] + report["outliers_detected"]
    quality_score = max(0, int((1 - (total_issues / total_cells)) * 100))
    
    return df, audit_trail, report, quality_score

# --- APP UI LOGIC ---
if uploaded_file:
    # Load Data
    if "df_raw" not in st.session_state:
        if uploaded_file.name.endswith('.csv'):
            st.session_state.df_raw = pd.read_csv(uploaded_file)
        else:
            st.session_state.df_raw = pd.read_excel(uploaded_file)
        # Run initial audit
        cleaned_df, audit, summary, score = run_data_audit(st.session_state.df_raw)
        st.session_state.cleaned_df = cleaned_df
        st.session_state.audit = audit
        st.session_state.summary = summary
        st.session_state.score = score

    # Create Tabs
    t1, t2, t3, t4 = st.tabs(["🏠 Audit Summary", "🧹 Cleaned Data", "📈 Visualizer", "🧠 AI BI Report"])

    # --- TAB 1: AUDIT SUMMARY ---
    with t1:
        st.subheader("📋 Data Quality Audit")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Quality Score", f"{st.session_state.score}/100")
        m2.metric("Missing Handled", st.session_state.summary["missing_handled"])
        m3.metric("Duplicates Removed", st.session_state.summary["duplicates_removed"])
        m4.metric("Outliers Flagged", st.session_state.summary["outliers_detected"])
        
        st.divider()
        st.subheader("📜 Step-by-Step Audit Log")
        for line in st.session_state.audit:
            st.markdown(f"<div class='audit-log'>{line}</div>", unsafe_allow_html=True)
        
        # Download Audit Log
        audit_text = "\n".join(st.session_state.audit)
        st.download_button("📥 Download Audit Log (.txt)", audit_text, "audit_log.txt")

    # --- TAB 2: CLEANED DATA ---
    with t2:
        st.subheader("✨ Cleaned Dataset Explorer")
        st.info("Rows highlighted in 🔴 red contain errors. Rows in 🟡 yellow are suspicious outliers.")
        
        # Highlighting function for the dataframe
        def highlight_rows(row):
            if row.dq_flag == 'error': return ['background-color: #fee2e2'] * len(row)
            if row.dq_flag == 'needs_review': return ['background-color: #fef3c7'] * len(row)
            return [''] * len(row)

        st.dataframe(st.session_state.cleaned_df.style.apply(highlight_rows, axis=1), use_container_width=True)
        
        st.download_button(
            label="📥 Download FULL Cleaned Dataset (CSV)",
            data=st.session_state.cleaned_df.to_csv(index=False).encode('utf-8'),
            file_name='cleaned_data_report.csv',
            mime='text/csv'
        )

    # --- TAB 3: VISUALIZER ---
    with t3:
        st.subheader("Interactive Trends")
        num_cols = st.session_state.cleaned_df.select_dtypes(include=['number']).columns.tolist()
        if num_cols:
            c1, c2 = st.columns([1, 3])
            with c1:
                x_axis = st.selectbox("X-Axis", st.session_state.cleaned_df.columns)
                y_axis = st.selectbox("Y-Axis", num_cols)
                chart_type = st.radio("Chart Type", ["Bar", "Line", "Scatter"])
            with c2:
                if chart_type == "Bar": fig = px.bar(st.session_state.cleaned_df, x=x_axis, y=y_axis, template="plotly_white")
                elif chart_type == "Line": fig = px.line(st.session_state.cleaned_df, x=x_axis, y=y_axis, template="plotly_white")
                else: fig = px.scatter(st.session_state.cleaned_df, x=x_axis, y=y_axis, template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)

    # --- TAB 4: AI BI REPORT ---
    with t4:
        st.subheader("🧠 Comprehensive AI Business Intelligence Report")
        if not api_key:
            st.info("Please enter your Gemini API Key in the sidebar to generate the full report.")
        else:
            if st.button("🚀 Generate Full Structured Report"):
                with st.spinner("Expert Analyst is analyzing all records..."):
                    try:
                        csv_data = st.session_state.cleaned_df.to_csv(index=False)
                        
                        # MODIFIED PROMPT TO HIGHLIGHT ERRORS
                        prompt = f"""
                        You are an expert business intelligence analyst. Read the ENTIRE dataset and generate a COMPLETE report.
                        
                        CRITICAL: In Section C (Data Quality), you MUST highlight every error, anomaly, or inconsistency using the prefix ⚠️ [ERROR] or 🚩 [ANOMALY]. 
                        Be specific about which columns or categories are messy.

                        REPORT FORMAT:
                        A. Executive Summary
                        B. Dataset Overview
                        C. Data Quality Findings (HIGHLIGHT ERRORS HERE)
                        D. Detailed Analytical Findings
                        E. Trends and Patterns
                        F. Risks and Anomalies
                        G. Recommendations
                        H. Final Conclusion

                        DATASET:
                        {csv_data}
                        """
                        
                        model = genai.GenerativeModel('gemini-1.5-pro')
                        response = model.generate_content(prompt)
                        st.session_state.ai_report = response.text
                        
                    except Exception as e:
                        st.error(f"AI Error: {e}")

            if "ai_report" in st.session_state:
                st.markdown(f"<div class='report-text'>{st.session_state.ai_report}</div>", unsafe_allow_html=True)
                st.download_button(
                    label="📥 Download FULL AI BI Report (.txt)",
                    data=st.session_state.ai_report,
                    file_name='Expert_BI_Report.txt',
                    mime='text/plain'
                )

else:
    st.info("👋 Welcome! Please upload a dataset in the sidebar to begin.")
