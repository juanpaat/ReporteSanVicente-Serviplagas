"""
Streamlit Web Application for Hospital Pest Control Report Generation
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import traceback
from report_generator import load_api_data, generate_report_for_locations, get_data_summary


# Page configuration
st.set_page_config(
    page_title="Hospital Pest Control Report Generator",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sidebar-content {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e6e6e6;
        margin: 0.5rem 0;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #f5c6cb;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=3600)  # Cache for 1 hour
def cached_load_api_data():
    """Load API data with caching"""
    return load_api_data()


def main():
    # Main header
    st.markdown('<h1 class="main-header">🏥 Hospital Pest Control Report Generator</h1>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'report_generated' not in st.session_state:
        st.session_state.report_generated = False
    if 'report_buffer' not in st.session_state:
        st.session_state.report_buffer = None
    if 'report_filename' not in st.session_state:
        st.session_state.report_filename = None
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.header("📋 Configuration")
        
        # Location selector
        st.subheader("🏢 Location Selection")
        location_options = ["Medellín", "Rionegro", "Both Locations"]
        selected_location = st.selectbox(
            "Select hospital location:",
            options=location_options,
            index=2,  # Default to "Both Locations"
            help="Choose which hospital location(s) to include in the report"
        )
        
        # Month exclusion
        st.subheader("📅 Data Filtering")
        exclude_month = st.text_input(
            "Month to exclude (format: 'Oct 2025'):",
            value="Oct 2025",
            help="Enter the month to exclude from the analysis in format 'Mon YYYY'"
        )
        
        # Advanced options
        with st.expander("⚙️ Advanced Options"):
            template_file = st.file_uploader(
                "Custom Word Template (optional):",
                type=['docx'],
                help="Upload a custom Word template. If not provided, the default template will be used."
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Data loading section
        st.markdown("---")
        st.subheader("📊 Data Status")
        
        if st.button("🔄 Load/Refresh Data", use_container_width=True):
            with st.spinner("Loading data from APIs..."):
                try:
                    # Clear cache and load fresh data
                    cached_load_api_data.clear()
                    prev_data, roed_data, lamp_data = cached_load_api_data()
                    st.session_state.data_loaded = True
                    st.session_state.api_data = (prev_data, roed_data, lamp_data)
                    st.success("✅ Data loaded successfully!")
                except Exception as e:
                    st.error(f"❌ Error loading data: {str(e)}")
                    st.session_state.data_loaded = False
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 Report Generation")
        
        # Load data automatically on first run
        if not st.session_state.data_loaded:
            with st.spinner("Loading initial data..."):
                try:
                    prev_data, roed_data, lamp_data = cached_load_api_data()
                    st.session_state.data_loaded = True
                    st.session_state.api_data = (prev_data, roed_data, lamp_data)
                    st.success("✅ Initial data loaded successfully!")
                except Exception as e:
                    error_msg = str(e)
                    if "your-actual-api-endpoint" in error_msg:
                        st.error("❌ **Configuration Required**: Please update the API endpoints in your `.env` file")
                        st.info("""
                        **To configure the application:**
                        
                        1. Open the `.env` file in the project directory
                        2. Replace the placeholder URLs with your actual API endpoints:
                           - `prev_API=https://your-actual-api-endpoint.com/preventivos-data`
                           - `roe_API=https://your-actual-api-endpoint.com/roedores-data`
                           - `lam_API=https://your-actual-api-endpoint.com/lamparas-data`
                        3. Refresh this page
                        """)
                    else:
                        st.error(f"❌ Error loading initial data: {error_msg}")
                        
                        with st.expander("🔍 Troubleshooting"):
                            st.markdown("""
                            **Common issues:**
                            - Check your internet connection
                            - Verify API endpoints are accessible
                            - Ensure API endpoints return data in the expected format
                            - Check if API authentication is required
                            """)
                    st.stop()
        
        # Data summary
        if st.session_state.data_loaded:
            try:
                prev_data, roed_data, lamp_data = st.session_state.api_data
                
                # Determine locations for processing
                if selected_location == "Both Locations":
                    locations_to_process = ["Medellín", "Rionegro"]
                else:
                    locations_to_process = [selected_location]
                
                # Show data summary
                with st.expander("📊 Data Summary", expanded=False):
                    summary = get_data_summary(prev_data, roed_data, lamp_data, locations_to_process)
                    
                    for location, stats in summary.items():
                        st.markdown(f"**{location}:**")
                        col_a, col_b, col_c, col_d = st.columns(4)
                        with col_a:
                            st.metric("Preventivos", stats['preventivos_records'])
                        with col_b:
                            st.metric("Roedores", stats['roedores_records'])
                        with col_c:
                            st.metric("Lámparas", stats['lamparas_records'])
                        with col_d:
                            st.metric("Total", stats['total_records'])
                        
                        if 'date_range' in stats:
                            st.caption(f"Date range: {stats['date_range']}")
                        st.markdown("---")
                
            except Exception as e:
                st.error(f"Error generating data summary: {str(e)}")
        
        # Report generation button
        if st.button("🚀 Generate Report", use_container_width=True, type="primary"):
            if not st.session_state.data_loaded:
                st.error("❌ Please load data first!")
                return
            
            # Determine locations for processing
            if selected_location == "Both Locations":
                locations_to_process = ["Medellín", "Rionegro"]
                filename_location = "Both_Locations"
            else:
                locations_to_process = [selected_location]
                filename_location = selected_location.replace('í', 'i').replace('ó', 'o')
            
            # Show progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Step 1: Process data
                status_text.text("🔄 Processing data...")
                progress_bar.progress(20)
                
                # Step 2: Generate visualizations
                status_text.text("📊 Generating visualizations...")
                progress_bar.progress(50)
                
                # Step 3: Create report
                status_text.text("📄 Creating Word document...")
                progress_bar.progress(80)
                
                # Generate report
                template_path = 'Plantilla.docx'
                if template_file is not None:
                    # Save uploaded template temporarily
                    with open('temp_template.docx', 'wb') as f:
                        f.write(template_file.getvalue())
                    template_path = 'temp_template.docx'
                
                buffer = generate_report_for_locations(
                    locations=locations_to_process,
                    mes_excluir=exclude_month,
                    template_path=template_path,
                    return_buffer=True
                )
                
                # Step 4: Finalize
                status_text.text("✅ Report generated successfully!")
                progress_bar.progress(100)
                
                # Store in session state
                st.session_state.report_generated = True
                st.session_state.report_buffer = buffer
                
                # Generate filename
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
                st.session_state.report_filename = f"Informe_{filename_location}_{timestamp}.docx"
                
                # Success message
                st.markdown(
                    '<div class="success-message">✅ <strong>Report generated successfully!</strong> Use the download button below to save the file.</div>',
                    unsafe_allow_html=True
                )
                
                # Clean up temporary template if used
                if template_file is not None:
                    try:
                        import os
                        os.remove('temp_template.docx')
                    except:
                        pass
                
            except Exception as e:
                progress_bar.progress(0)
                status_text.text("")
                error_details = traceback.format_exc()
                st.markdown(
                    f'<div class="error-message">❌ <strong>Error generating report:</strong><br>{str(e)}</div>',
                    unsafe_allow_html=True
                )
                
                # Show detailed error in expander for debugging
                with st.expander("🔍 Error Details"):
                    st.code(error_details)
                
                st.session_state.report_generated = False
    
    with col2:
        st.subheader("💾 Download")
        
        if st.session_state.report_generated and st.session_state.report_buffer:
            st.success("📄 Report ready for download!")
            
            # Download button
            st.download_button(
                label="⬇️ Download Report",
                data=st.session_state.report_buffer.getvalue(),
                file_name=st.session_state.report_filename,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
            
            # Report info
            st.info(f"**Filename:** {st.session_state.report_filename}")
            
            # Reset button
            if st.button("🔄 Generate New Report", use_container_width=True):
                st.session_state.report_generated = False
                st.session_state.report_buffer = None
                st.session_state.report_filename = None
                st.rerun()
        
        else:
            st.info("Generate a report to enable download")
        
        # Help section
        st.markdown("---")
        st.subheader("ℹ️ Help")
        with st.expander("How to use this app"):
            st.markdown("""
            **Steps to generate a report:**
            
            1. **Select Location**: Choose which hospital location(s) to include
            2. **Set Filters**: Specify which month to exclude from analysis
            3. **Load Data**: Click 'Load/Refresh Data' to get the latest information
            4. **Generate Report**: Click 'Generate Report' to create the Word document
            5. **Download**: Use the download button to save the report
            
            **Tips:**
            - The app automatically loads data when first opened
            - Use 'Both Locations' to include data from both hospitals
            - Reports include visualizations and detailed tables
            - Generated files are named with location and timestamp
            """)
        
        with st.expander("Troubleshooting"):
            st.markdown("""
            **Common issues:**
            
            - **Data loading fails**: Check your internet connection and API endpoints
            - **Report generation fails**: Ensure the Word template is valid
            - **Download doesn't work**: Try generating the report again
            
            **Data format for month exclusion:**
            - Use format like 'Oct 2025', 'Jan 2024', etc.
            - Month names should be 3-letter abbreviations
            """)


if __name__ == "__main__":
    main()