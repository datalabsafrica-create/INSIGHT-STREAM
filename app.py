import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Config & Styling
st.set_page_config(page_title="DataPro Dashboard", layout="wide", page_icon="📊")

# Custom CSS for a cleaner look
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_content_code=True)

st.title("📊 DataPro Dashboard")

# 2. Sidebar for File Upload & Global Settings
with st.sidebar:
    st.header("📁 Data Source")
    uploaded_file = st.file_uploader("Upload CSV or Excel", type=['csv', 'xlsx'])
    
    if uploaded_file:
        st.success("File uploaded!")
        st.divider()
        st.header("🛠️ Data Cleaning")
        if st.button("🧼 Remove Missing Values"):
            st.session_state.clean_data = True
        if st.button("🔄 Reset Data"):
            st.session_state.clean_data = False

# 3. Main App Logic
if uploaded_file:
    # Load Data
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    
    # Apply Cleaning if requested
    if st.session_state.get('clean_data'):
        df = df.dropna()

    # Create Tabs
    tab1, tab2, tab3 = st.tabs(["🏠 Overview", "📈 Visualizer", "🔍 Explorer"])

    # --- TAB 1: OVERVIEW ---
    with tab1:
        st.subheader("Key Metrics")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Rows", len(df))
        m2.metric("Columns", len(df.columns))
        m3.metric("Numeric Columns", len(df.select_dtypes(include=['number']).columns))
        m4.metric("Missing Cells", df.isna().sum().sum())
        
        st.divider()
        st.subheader("Column Types")
        st.write(df.dtypes.to_frame().T)

    # --- TAB 2: VISUALIZER ---
    with tab2:
        st.subheader("Chart Configuration")
        all_cols = df.columns.tolist()
        num_cols = df.select_dtypes(include=['number']).columns.tolist()

        c1, c2, c3 = st.columns(3)
        with c1: x_axis = st.selectbox("X-Axis", all_cols)
        with c2: y_axis = st.selectbox("Y-Axis", num_cols)
        with c3: chart_type = st.selectbox("Style", ["Bar", "Line", "Scatter", "Box", "Histogram"])

        color_by = st.selectbox("Color/Group By (Optional)", ["None"] + all_cols)
        
        color_val = None if color_by == "None" else color_by

        if chart_type == "Bar":
            fig = px.bar(df, x=x_axis, y=y_axis, color=color_val, barmode="group", template="plotly_white")
        elif chart_type == "Line":
            fig = px.line(df, x=x_axis, y=y_axis, color=color_val, template="plotly_white")
        elif chart_type == "Scatter":
            fig = px.scatter(df, x=x_axis, y=y_axis, color=color_val, template="plotly_white")
        elif chart_type == "Box":
            fig = px.box(df, x=x_axis, y=y_axis, color=color_val, template="plotly_white")
        else:
            fig = px.histogram(df, x=x_axis, y=y_axis, color=color_val, template="plotly_white")

        st.plotly_chart(fig, use_container_width=True)

    # --- TAB 3: EXPLORER ---
    with tab3:
        st.subheader("Search & Filter")
        search = st.text_input("Type to search any value...")
        
        if search:
            df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
        
        st.dataframe(df, use_container_width=True)
        
        st.download_button("📥 Download Current View", df.to_csv(index=False), "data.csv", "text/csv")

else:
    st.info("Please upload a file in the sidebar to get started.")
