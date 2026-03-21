import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Data Analysis App", page_icon="📊", layout="wide")

# --- TITLE & DESCRIPTION ---
st.title("📊 Interactive Data Analysis App")
st.markdown("Upload your dataset and explore it with ease. This app allows you to view raw data, summary statistics, and generate interactive visualizations.")

# --- SIDEBAR: FILE UPLOAD ---
st.sidebar.header("1. Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

# --- CACHE DATA LOADING ---
@st.cache_data
def load_data(file):
    # Determine the file extension and load accordingly
    name = file.name
    if name.endswith('.csv'):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)
    return df

# --- MAIN APP LOGIC ---
if uploaded_file is not None:
    try:
        # Load the data
        df = load_data(uploaded_file)
        
        # Create tabs for better organization
        tab1, tab2, tab3 = st.tabs(["📋 Data Overview", "🛠️ Data Filtering", "📈 Visualization"])
        
        # --- TAB 1: DATA OVERVIEW ---
        with tab1:
            st.subheader("Dataset Preview")
            st.dataframe(df.head(10)) # Show first 10 rows
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Dataset Shape:**")
                st.write(f"{df.shape[0]} Rows, {df.shape[1]} Columns")
                
                st.write("**Data Types:**")
                st.dataframe(df.dtypes.astype(str), use_container_width=True)
                
            with col2:
                st.write("**Missing Values:**")
                st.dataframe(df.isnull().sum(), use_container_width=True)
                
            st.subheader("Summary Statistics")
            st.dataframe(df.describe())

        # --- TAB 2: DATA FILTERING ---
        with tab2:
            st.subheader("Filter your Data")
            # Select columns to display
            all_columns = df.columns.tolist()
            selected_columns = st.multiselect("Select columns to view:", all_columns, default=all_columns)
            
            # Simple row filter based on a single column
            filter_col = st.selectbox("Select a column to filter by:", all_columns)
            unique_values = df[filter_col].dropna().unique().tolist()
            
            # Handle too many unique values gracefully
            if len(unique_values) < 50:
                selected_values = st.multiselect(f"Select values from {filter_col}:", unique_values, default=unique_values)
                filtered_df = df[df[filter_col].isin(selected_values)]
            else:
                st.warning(f"'{filter_col}' has too many unique values to filter via dropdown. Showing unfiltered data.")
                filtered_df = df
                
            st.dataframe(filtered_df[selected_columns])
            
            # Allow user to download the filtered dataset
            csv = filtered_df[selected_columns].to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Filtered Data as CSV",
                data=csv,
                file_name='filtered_data.csv',
                mime='text/csv',
            )

        # --- TAB 3: VISUALIZATION ---
        with tab3:
            st.subheader("Build Visualizations")
            
            # Select plot type
            plot_type = st.selectbox("Choose the type of plot:", ["Scatter Plot", "Bar Chart", "Histogram", "Line Chart"])
            
            # Select axes
            col_x, col_y = st.columns(2)
            with col_x:
                x_axis = st.selectbox("X-Axis:", df.columns)
            with col_y:
                # Provide an option for 'None' for histograms
                y_axis = st.selectbox("Y-Axis (Optional for Histogram):", ["None"] + df.columns.tolist())
            
            # Generate the plot based on user selection
            if st.button("Generate Plot"):
                if plot_type == "Scatter Plot" and y_axis != "None":
                    fig = px.scatter(df, x=x_axis, y=y_axis, title=f"{y_axis} vs {x_axis}")
                    st.plotly_chart(fig, use_container_width=True)
                    
                elif plot_type == "Bar Chart" and y_axis != "None":
                    fig = px.bar(df, x=x_axis, y=y_axis, title=f"{y_axis} by {x_axis}")
                    st.plotly_chart(fig, use_container_width=True)
                    
                elif plot_type == "Line Chart" and y_axis != "None":
                    fig = px.line(df, x=x_axis, y=y_axis, title=f"{y_axis} over {x_axis}")
                    st.plotly_chart(fig, use_container_width=True)
                    
                elif plot_type == "Histogram":
                    fig = px.histogram(df, x=x_axis, title=f"Distribution of {x_axis}")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error("Please select a valid Y-Axis for this chart type.")

    except Exception as e:
        st.error(f"An error occurred: {e}")

else:
    # Message shown when no file is uploaded
    st.info("Awaiting for CSV or Excel file to be uploaded.")
    st.write("👈 Please upload a file from the sidebar to begin.")
