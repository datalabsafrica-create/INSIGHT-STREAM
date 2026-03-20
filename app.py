import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Setup the Page
st.set_page_config(page_title="InsightStream Data Pro", layout="wide")
st.title("📊 InsightStream Data Pro")
st.markdown("Upload your data to visualize trends and explore your records instantly.")

# 2. File Uploader
uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=['csv', 'xlsx'])

if uploaded_file is not None:
    # Load Data
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # 3. Show Data Summary Metrics
        st.divider()
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Rows", len(df))
        col2.metric("Total Columns", len(df.columns))
        col3.metric("Missing Values", df.isna().sum().sum())

        # 4. Interactive Charts Section
        st.subheader("📈 Interactive Visualizations")
        
        # Get numeric and categorical columns for selection
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        all_cols = df.columns.tolist()

        if numeric_cols:
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                x_axis = st.selectbox("Select X-axis", all_cols)
                y_axis = st.selectbox("Select Y-axis (Numeric)", numeric_cols)
                chart_type = st.radio("Chart Type", ["Bar", "Line", "Scatter"], horizontal=True)

            with chart_col2:
                if chart_type == "Bar":
                    fig = px.bar(df, x=x_axis, y=y_axis, title=f"{y_axis} by {x_axis}", color_discrete_sequence=['#3b82f6'])
                elif chart_type == "Line":
                    fig = px.line(df, x=x_axis, y=y_axis, title=f"{y_axis} Trend over {x_axis}")
                else:
                    fig = px.scatter(df, x=x_axis, y=y_axis, title=f"{y_axis} vs {x_axis}", color_discrete_sequence=['#ef4444'])
                
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No numeric columns found to create charts.")

        # 5. Data Explorer (Search and Filter)
        st.divider()
        st.subheader("🔍 Data Explorer")
        
        # Simple search box
        search_term = st.text_input("Search in data:")
        if search_term:
            # Filter rows that contain the search term in any column
            mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)
            filtered_df = df[mask]
            st.write(f"Found {len(filtered_df)} matches:")
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.dataframe(df, use_container_width=True)

        # 6. Download Button
        st.download_button(
            label="📥 Download Data as CSV",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name='exported_data.csv',
            mime='text/csv',
        )

    except Exception as e:
        st.error(f"Error loading file: {e}")

else:
    # Welcome screen
    st.info("👋 Welcome! Please upload a CSV or Excel file to begin your analysis.")
    
    # Example of what the app does
    st.image("https://picsum.photos/seed/data/1200/400?blur=2", caption="Visualize your data instantly")
