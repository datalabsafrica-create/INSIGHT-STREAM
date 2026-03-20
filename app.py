import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Config & Styling
st.set_page_config(page_title="DataPro Dashboard", layout="wide", page_icon="📊")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 DataPro Dashboard")

# 2. Main Page File Upload
st.header("📁 Step 1: Upload your Data")
uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=['csv', 'xlsx'])

# 3. Main App Logic
if uploaded_file:
    # Load Data (Initial Load)
    if "df_original" not in st.session_state:
        try:
            if uploaded_file.name.endswith('.csv'):
                st.session_state.df_original = pd.read_csv(uploaded_file)
            else:
                st.session_state.df_original = pd.read_excel(uploaded_file)
            st.session_state.df_cleaned = st.session_state.df_original.copy()
        except Exception as e:
            st.error(f"Error loading file: {e}")
            st.stop()

    # Use the cleaned version for everything
    df = st.session_state.df_cleaned

    st.divider()
    st.header("📈 Step 2: Clean, Explore & Visualize")

    # Create Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🏠 Overview", "🧹 Data Cleaning", "📈 Visualizer", "🔍 Explorer"])

    # --- TAB 1: OVERVIEW ---
    with tab1:
        st.subheader("Current Data Summary")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Rows", len(df))
        m2.metric("Columns", len(df.columns))
        m3.metric("Numeric Columns", len(df.select_dtypes(include=['number']).columns))
        m4.metric("Missing Cells", df.isna().sum().sum())
        
        st.divider()
        st.subheader("Data Preview")
        st.dataframe(df.head(10), use_container_width=True)

    # --- TAB 2: DATA CLEANING ---
    with tab2:
        st.subheader("Cleaning Tools")
        
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            st.write("### 🧼 Basic Cleaning")
            if st.button("🚫 Remove Duplicate Rows"):
                st.session_state.df_cleaned = df.drop_duplicates()
                st.success("Duplicates removed!")
                st.rerun()
            
            if st.button("🗑️ Drop Rows with Missing Values"):
                st.session_state.df_cleaned = df.dropna()
                st.success("Rows with missing values dropped!")
                st.rerun()

            if st.button("🔄 Reset to Original Data"):
                st.session_state.df_cleaned = st.session_state.df_original.copy()
                st.info("Data reset to original upload.")
                st.rerun()

        with col_c2:
            st.write("### ✂️ Column Management")
            cols_to_drop = st.multiselect("Select columns to remove:", df.columns.tolist())
            if st.button("❌ Drop Selected Columns") and cols_to_drop:
                st.session_state.df_cleaned = df.drop(columns=cols_to_drop)
                st.success(f"Dropped: {', '.join(cols_to_drop)}")
                st.rerun()

        st.divider()
        st.write("### 🧪 Advanced Operations")
        adv_col1, adv_col2 = st.columns(2)
        
        with adv_col1:
            target_col = st.selectbox("Select column to fill missing values:", ["None"] + df.columns.tolist())
            fill_method = st.radio("Fill with:", ["Mean (Average)", "Median (Middle)", "Zero"])
            
            if st.button("🪄 Fill Missing Values") and target_col != "None":
                if df[target_col].dtype in ['float64', 'int64']:
                    if fill_method == "Mean (Average)":
                        st.session_state.df_cleaned[target_col] = df[target_col].fillna(df[target_col].mean())
                    elif fill_method == "Median (Middle)":
                        st.session_state.df_cleaned[target_col] = df[target_col].fillna(df[target_col].median())
                    else:
                        st.session_state.df_cleaned[target_col] = df[target_col].fillna(0)
                    st.success(f"Filled missing values in {target_col}")
                    st.rerun()
                else:
                    st.error("Filling with Mean/Median only works for numeric columns.")

    # --- TAB 3: VISUALIZER ---
    with tab3:
        st.subheader("Chart Configuration")
        all_cols = df.columns.tolist()
        num_cols = df.select_dtypes(include=['number']).columns.tolist()

        if num_cols:
            c1, c2, c3 = st.columns(3)
            with c1: x_axis = st.selectbox("X-Axis", all_cols, key="viz_x")
            with c2: y_axis = st.selectbox("Y-Axis", num_cols, key="viz_y")
            with c3: chart_type = st.selectbox("Style", ["Bar", "Line", "Scatter", "Box", "Histogram"], key="viz_type")

            color_by = st.selectbox("Color/Group By (Optional)", ["None"] + all_cols, key="viz_color")
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
        else:
            st.warning("No numeric columns found to create charts.")

    # --- TAB 4: EXPLORER ---
    with tab4:
        st.subheader("Search & Filter")
        search = st.text_input("Type to search any value...")
        
        display_df = df.copy()
        if search:
            display_df = display_df[display_df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
        
        st.dataframe(display_df, use_container_width=True)
        st.download_button("📥 Download Cleaned Data", display_df.to_csv(index=False), "cleaned_data.csv", "text/csv")

else:
    # Clear session state if file is removed
    if "df_original" in st.session_state:
        del st.session_state.df_original
        del st.session_state.df_cleaned
    st.info("👋 Welcome! Please upload a CSV or Excel file above to begin your analysis.")
