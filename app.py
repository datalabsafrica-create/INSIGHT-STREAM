import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="Data Quality Analyst Pro", layout="wide", page_icon="🛡️")

st.markdown("""
    <style>
    .report-card { background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0; margin-bottom: 20px; }
    .metric-box { text-align: center; padding: 10px; border-right: 1px solid #eee; }
    .audit-log { font-family: monospace; font-size: 0.85rem; background-color: #f1f5f9; padding: 10px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Senior Data Quality Analyst")
st.markdown("Systematic Data Profiling, Cleaning, and Validation Engine.")

# 2. File Upload
uploaded_file = st.file_uploader("📥 Upload Dataset (CSV or Excel)", type=['csv', 'xlsx'])

# --- CORE ANALYTICS ENGINE ---
def process_data_quality(df_input):
    df = df_input.copy()
    audit_trail = []
    report = {"total_rows": len(df), "missing_handled": 0, "duplicates_removed": 0, "outliers_detected": 0}
    
    # Step 1: Duplicate Handling
    initial_count = len(df)
    df = df.drop_duplicates()
    removed = initial_count - len(df)
    if removed > 0:
        audit_trail.append(f"Step 5: Removed {removed} exact duplicate rows.")
        report["duplicates_removed"] = removed

    # Initialize Quality Flag
    df['dq_flag'] = 'clean'

    # Step 2: Missing Values & Data Type Validation
    for col in df.columns:
        if col == 'dq_flag': continue
        
        null_count = df[col].isna().sum()
        if null_count > 0:
            report["missing_handled"] += null_count
            if df[col].dtype in ['float64', 'int64']:
                fill_val = df[col].median()
                df[col] = df[col].fillna(fill_val)
                audit_trail.append(f"Step 2: Filled {null_count} missing values in '{col}' using Median ({fill_val}).")
            else:
                df[col] = df[col].fillna("Unknown")
                audit_trail.append(f"Step 2: Filled {null_count} missing values in '{col}' with 'Unknown'.")
            df.loc[df[col].isna(), 'dq_flag'] = 'needs_review'

    # Step 3: Standardization & Formatting
    for col in df.columns:
        if df[col].dtype == 'object':
            # Text Standardization
            df[col] = df[col].astype(str).str.strip().str.title()
            
            # Attempt Date Standardization
            if "date" in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d')
                    audit_trail.append(f"Step 3: Standardized dates in '{col}' to YYYY-MM-DD.")
                except:
                    pass

    # Step 4: Outlier Detection (IQR Method)
    for col in df.select_dtypes(include=[np.number]).columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
        if not outliers.empty:
            report["outliers_detected"] += len(outliers)
            df.loc[outliers.index, 'dq_flag'] = 'needs_review'
            audit_trail.append(f"Step 6: Flagged {len(outliers)} outliers in '{col}' (Values outside {lower_bound:.2f} - {upper_bound:.2f}).")

    # Step 5: Quality Scoring
    # Score = (1 - (total_errors / total_cells)) * 100
    total_cells = df.size
    total_issues = report["missing_handled"] + report["outliers_detected"] + report["duplicates_removed"]
    quality_score = max(0, int((1 - (total_issues / total_cells)) * 100))
    
    return df, audit_trail, report, quality_score

# --- APP UI LOGIC ---
if uploaded_file:
    if "df_raw" not in st.session_state:
        if uploaded_file.name.endswith('.csv'):
            st.session_state.df_raw = pd.read_csv(uploaded_file)
        else:
            st.session_state.df_raw = pd.read_excel(uploaded_file)

    if st.button("🚀 Run Full Data Quality Audit"):
        with st.spinner("Analyzing data quality..."):
            cleaned_df, audit, summary, score = process_data_quality(st.session_state.df_raw)
            st.session_state.cleaned_df = cleaned_df
            st.session_state.audit = audit
            st.session_state.summary = summary
            st.session_state.score = score
            st.session_state.audit_complete = True

    if st.session_state.get("audit_complete"):
        # 1. Summary Report Dashboard
        st.divider()
        st.header("📋 Audit Summary Report")
        
        col_s1, col_s2, col_s3, col_s4, col_s5 = st.columns(5)
        col_s1.metric("Quality Score", f"{st.session_state.score}/100")
        col_s2.metric("Rows Processed", st.session_state.summary["total_rows"])
        col_s3.metric("Missing Handled", st.session_state.summary["missing_handled"])
        col_s4.metric("Duplicates Removed", st.session_state.summary["duplicates_removed"])
        col_s5.metric("Outliers Flagged", st.session_state.summary["outliers_detected"])

        # 2. Tabs for Detailed Output
        t1, t2, t3, t4 = st.tabs(["✨ Cleaned Dataset", "📜 Audit Trail", "🚩 Flagged Records", "💡 Recommendations"])

        with t1:
            st.subheader("Final Cleaned Data")
            st.dataframe(st.session_state.cleaned_df, use_container_width=True)
            st.download_button("📥 Download Cleaned Dataset", st.session_state.cleaned_df.to_csv(index=False), "cleaned_data.csv")

        with t2:
            st.subheader("Step-by-Step Audit Log")
            for line in st.session_state.audit:
                st.markdown(f"<div class='audit-log'>{line}</div>", unsafe_allow_html=True)

        with t3:
            st.subheader("Records Requiring Manual Review")
            flagged = st.session_state.cleaned_df[st.session_state.cleaned_df['dq_flag'] != 'clean']
            if not flagged.empty:
                st.warning(f"Found {len(flagged)} records that need human verification.")
                st.dataframe(flagged, use_container_width=True)
            else:
                st.success("No critical errors or outliers found!")

        with t4:
            st.subheader("Strategic Recommendations")
            st.info("""
            1. **Validation at Entry**: Implement dropdowns for categorical fields to prevent 'HR' vs 'Human Resources' inconsistencies.
            2. **Mandatory Fields**: Set database constraints for columns with high missing rates.
            3. **Outlier Monitoring**: Review the flagged records in Tab 3 to determine if they represent fraud or valid extreme business cases.
            4. **Date Formatting**: Ensure source systems export dates in ISO-8601 format to avoid ambiguity.
            """)

else:
    st.info("Please upload a dataset to begin the Senior Data Quality Audit.")
