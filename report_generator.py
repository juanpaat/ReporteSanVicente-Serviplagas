"""
Report generation functions for the Streamlit app and main script
"""

import os
import pandas as pd
from dotenv import load_dotenv
from io import BytesIO
from datetime import datetime

# Data processing imports
from data_preprocessing.pipeline import leer_data, procesar_preventivos, procesar_lamparas, procesar_roedores
import ssl
import urllib3

# Visualization imports
from data_visualization.preventivos import generate_order_area_plot, generate_plagas_timeseries_facet, generate_total_plagas_trend_plot
from data_visualization.roedores import generate_roedores_station_status_plot, plot_tendencia_eliminacion_mensual
from data_visualization.lamparas import plot_estado_lamparas_por_mes, plot_estado_lamparas_con_leyenda, plot_capturas_especies_por_mes, plot_tendencia_total_capturas

# Report engine
from Engine.engine import InformeHospitalGenerator

# Load environment variables
load_dotenv()


def load_api_data():
    """
    Load data from all three APIs
    
    Returns:
        tuple: (prev_data, roed_data, lamp_data)
    """
    try:
        # For local development, always use environment variables
        # Only use Streamlit secrets in cloud deployment
        prev_api = os.getenv("prev_API")
        roe_api = os.getenv("roe_API") 
        lam_api = os.getenv("lam_API")
        
        # If env vars are not set, try Streamlit secrets (only in cloud)
        if not (prev_api and roe_api and lam_api):
            try:
                # Check if we're in a Streamlit Cloud environment
                import streamlit as st
                
                # Only try secrets if we're in cloud or if a secrets file actually exists
                secrets_path = os.path.join(os.getcwd(), '.streamlit', 'secrets.toml')
                global_secrets_path = os.path.expanduser('~/.streamlit/secrets.toml')
                
                if (os.path.exists(secrets_path) or 
                    os.path.exists(global_secrets_path) or
                    os.getenv('STREAMLIT_SHARING_MODE') or 
                    os.getenv('STREAMLIT_CLOUD')):
                    
                    prev_api = prev_api or st.secrets.get("prev_API")
                    roe_api = roe_api or st.secrets.get("roe_API")
                    lam_api = lam_api or st.secrets.get("lam_API")
                    
            except (ImportError, Exception):
                # Streamlit not available, secrets failed, or no secrets file
                # This is normal for local development
                pass
        
        # Validate that we have all required APIs
        if not prev_api:
            raise ValueError("prev_API not found in environment variables or Streamlit secrets")
        if not roe_api:
            raise ValueError("roe_API not found in environment variables or Streamlit secrets")
        if not lam_api:
            raise ValueError("lam_API not found in environment variables or Streamlit secrets")
        
        # Load data from APIs with SSL handling
        try:
            prev_data = leer_data(prev_api)
            roed_data = leer_data(roe_api)
            lamp_data = leer_data(lam_api)
        except ssl.SSLError as e:
            # Handle SSL certificate issues common on macOS
            if "CERTIFICATE_VERIFY_FAILED" in str(e):
                raise Exception(
                    "SSL Certificate verification failed. This is common on macOS. "
                    "Try running: '/Applications/Python 3.x/Install Certificates.command' "
                    "or install certificates using: 'pip install --upgrade certifi'"
                )
            else:
                raise Exception(f"SSL Error connecting to APIs: {str(e)}")
        except Exception as api_error:
            raise Exception(f"Error connecting to APIs: {str(api_error)}")
        
        return prev_data, roed_data, lamp_data
        
    except Exception as e:
        raise Exception(f"Error loading API data: {str(e)}")


def process_location_data(prev_data, roed_data, lamp_data, location, mes_excluir):
    """
    Process data for a specific location
    
    Args:
        prev_data: Raw preventivos data
        roed_data: Raw roedores data  
        lamp_data: Raw lamparas data
        location: 'Medellín' or 'Rionegro'
        mes_excluir: Month to exclude from analysis
        
    Returns:
        tuple: (df_prev_full, df_roed_full, df_lamp_full)
    """
    try:
        # Filter data by location
        prev_location = prev_data[prev_data['Sede'] == location]
        roed_location = roed_data[roed_data['Sede'] == location]
        lamp_location = lamp_data[lamp_data['Sede'] == location]
        
        # Process data
        _, df_prev_full = procesar_preventivos(prev_location)
        _, df_roed_full = procesar_roedores(roed_location)
        _, df_lamp_full = procesar_lamparas(lamp_location)
        
        # Exclude specified month
        if mes_excluir:
            df_prev_full = df_prev_full[df_prev_full['Mes'] != mes_excluir]
            df_roed_full = df_roed_full[df_roed_full['Mes'] != mes_excluir]
            df_lamp_full = df_lamp_full[df_lamp_full['Mes'] != mes_excluir]
        
        return df_prev_full, df_roed_full, df_lamp_full
    
    except Exception as e:
        raise Exception(f"Error processing data for {location}: {str(e)}")


def add_location_visualizations(informe, df_prev_full, df_roed_full, df_lamp_full, location_prefix):
    """
    Add all visualizations for a specific location to the report
    
    Args:
        informe: InformeHospitalGenerator instance
        df_prev_full: Processed preventivos data
        df_roed_full: Processed roedores data
        df_lamp_full: Processed lamparas data
        location_prefix: 'med' for Medellín, 'rio' for Rionegro
    """
    try:
        # Preventivos visualizations
        informe.agregar_resultado_completo(
            generate_order_area_plot, 
            df_prev_full,
            f'{location_prefix}_preventivos_1_plot',
            f'{location_prefix}_preventivos_1_tabla'
        )
        informe.agregar_resultado_completo(
            generate_plagas_timeseries_facet, 
            df_prev_full,
            f'{location_prefix}_preventivos_2_plot',
            f'{location_prefix}_preventivos_2_tabla'
        )
        informe.agregar_resultado_completo(
            generate_total_plagas_trend_plot, 
            df_prev_full,
            f'{location_prefix}_preventivos_3_plot',
            f'{location_prefix}_preventivos_3_tabla'
        )
        
        # Roedores visualizations
        informe.agregar_resultado_completo(
            generate_roedores_station_status_plot, 
            df_roed_full,
            f'{location_prefix}_roedores_1_plot',
            f'{location_prefix}_roedores_1_tabla'
        )
        informe.agregar_resultado_completo(
            plot_tendencia_eliminacion_mensual,
            df_roed_full,
            f'{location_prefix}_roedores_2_plot',
            f'{location_prefix}_roedores_2_tabla'
        )

        # Lámparas visualizations
        informe.agregar_resultado_completo(
            plot_estado_lamparas_por_mes,
            df_lamp_full,
            f'{location_prefix}_lamparas_1_plot',
            f'{location_prefix}_lamparas_1_tabla'
        )
        informe.agregar_resultado_completo(
            plot_estado_lamparas_con_leyenda,
            df_lamp_full,
            f'{location_prefix}_lamparas_2_plot',
            f'{location_prefix}_lamparas_2_tabla'
        )
        informe.agregar_resultado_completo(
            plot_capturas_especies_por_mes,
            df_lamp_full,
            f'{location_prefix}_lamparas_3_plot',
            f'{location_prefix}_lamparas_3_tabla'
        )
        informe.agregar_resultado_completo(
            plot_tendencia_total_capturas,
            df_lamp_full,
            f'{location_prefix}_lamparas_4_plot',
            f'{location_prefix}_lamparas_4_tabla'
        )
        
    except Exception as e:
        raise Exception(f"Error adding visualizations for {location_prefix}: {str(e)}")


def generate_report_for_locations(locations, mes_excluir='Oct 2025', template_path='Plantilla.docx', return_buffer=True):
    """
    Generate report for specified locations
    
    Args:
        locations: List of locations ['Medellín', 'Rionegro'] or single location
        mes_excluir: Month to exclude from analysis
        template_path: Path to Word template
        return_buffer: If True, return BytesIO buffer; if False, save to file
        
    Returns:
        BytesIO buffer if return_buffer=True, filename if return_buffer=False
    """
    try:
        # Ensure locations is a list
        if isinstance(locations, str):
            locations = [locations]
        
        # Load API data
        prev_data, roed_data, lamp_data = load_api_data()
        
        # Initialize report generator
        informe = InformeHospitalGenerator(template_path=template_path)
        
        # Process each location
        for location in locations:
            # Determine location prefix
            location_prefix = 'med' if location == 'Medellín' else 'rio'
            
            # Process location data
            df_prev_full, df_roed_full, df_lamp_full = process_location_data(
                prev_data, roed_data, lamp_data, location, mes_excluir
            )
            
            # Add visualizations for this location
            add_location_visualizations(
                informe, df_prev_full, df_roed_full, df_lamp_full, location_prefix
            )
        
        # Generate report
        if return_buffer:
            buffer = informe.generar_informe(return_buffer=True)
            return buffer
        else:
            # Generate filename based on locations and date
            locations_str = "_".join(locations).replace('í', 'i').replace('ó', 'o')
            timestamp = datetime.now().strftime("%Y-%m-%d")
            filename = f'Informe_{locations_str}_{timestamp}.docx'
            informe.generar_informe(output_path=filename)
            return filename
            
    except Exception as e:
        raise Exception(f"Error generating report: {str(e)}")


def get_data_summary(prev_data, roed_data, lamp_data, locations):
    """
    Get summary statistics for the data
    
    Args:
        prev_data: Raw preventivos data
        roed_data: Raw roedores data
        lamp_data: Raw lamparas data
        locations: List of locations to analyze
        
    Returns:
        dict: Summary statistics
    """
    try:
        summary = {}
        
        for location in locations:
            location_summary = {}
            
            # Filter by location
            prev_loc = prev_data[prev_data['Sede'] == location]
            roed_loc = roed_data[roed_data['Sede'] == location]
            lamp_loc = lamp_data[lamp_data['Sede'] == location]
            
            location_summary['preventivos_records'] = len(prev_loc)
            location_summary['roedores_records'] = len(roed_loc)
            location_summary['lamparas_records'] = len(lamp_loc)
            location_summary['total_records'] = len(prev_loc) + len(roed_loc) + len(lamp_loc)
            
            # Date ranges
            if len(prev_loc) > 0:
                location_summary['date_range'] = f"{prev_loc['Fecha'].min()} - {prev_loc['Fecha'].max()}"
            
            summary[location] = location_summary
        
        return summary
        
    except Exception as e:
        raise Exception(f"Error generating data summary: {str(e)}")