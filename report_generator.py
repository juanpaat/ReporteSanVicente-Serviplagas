"""
Funciones de generación de reportes para la aplicación Streamlit y script principal
"""

import os
import pandas as pd
from dotenv import load_dotenv
from io import BytesIO
from datetime import datetime

# Importaciones de procesamiento de datos
from data_preprocessing.pipeline import leer_data, procesar_preventivos, procesar_lamparas, procesar_roedores
import ssl
import urllib3

# Importaciones de visualización
from data_visualization.preventivos import generate_order_area_plot, generate_plagas_timeseries_facet, generate_total_plagas_trend_plot
from data_visualization.roedores import generate_roedores_station_status_plot, plot_tendencia_eliminacion_mensual
from data_visualization.lamparas import plot_estado_lamparas_por_mes, plot_estado_lamparas_con_leyenda, plot_capturas_especies_por_mes, plot_tendencia_total_capturas

# Motor de reportes
from Engine.engine import InformeHospitalGenerator

# Cargar variables de entorno
load_dotenv()


def load_api_data():
    """
    Cargar datos de las tres APIs
    
    Returns:
        tuple: (prev_data, roed_data, lamp_data)
    """
    try:
        # Para desarrollo local, siempre usar variables de entorno
        # Solo usar secretos de Streamlit en despliegue en la nube
        prev_api = os.getenv("prev_API")
        roe_api = os.getenv("roe_API") 
        lam_api = os.getenv("lam_API")
        
        # Si las variables de entorno no están configuradas, intentar secretos de Streamlit (solo en la nube)
        if not (prev_api and roe_api and lam_api):
            try:
                # Verificar si estamos en un entorno Streamlit Cloud
                import streamlit as st
                
                # Solo intentar secretos si estamos en la nube o si realmente existe un archivo de secretos
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
                # Streamlit no disponible, secretos fallaron, o no hay archivo de secretos
                # Esto es normal para desarrollo local
                pass
        
        # Validar que tengamos todas las APIs requeridas
        if not prev_api:
            raise ValueError("prev_API no encontrada en variables de entorno o secretos de Streamlit")
        if not roe_api:
            raise ValueError("roe_API no encontrada en variables de entorno o secretos de Streamlit")
        if not lam_api:
            raise ValueError("lam_API no encontrada en variables de entorno o secretos de Streamlit")
        
        # Cargar datos de APIs con manejo de SSL
        try:
            prev_data = leer_data(prev_api)
            roed_data = leer_data(roe_api)
            lamp_data = leer_data(lam_api)
        except ssl.SSLError as e:
            # Manejar problemas de certificados SSL comunes en macOS
            if "CERTIFICATE_VERIFY_FAILED" in str(e):
                raise Exception(
                    "Falló la verificación del certificado SSL. Esto es común en macOS. "
                    "Intenta ejecutar: '/Applications/Python 3.x/Install Certificates.command' "
                    "o instalar certificados usando: 'pip install --upgrade certifi'"
                )
            else:
                raise Exception(f"Error SSL conectando a APIs: {str(e)}")
        except Exception as api_error:
            raise Exception(f"Error conectando a APIs: {str(api_error)}")
        
        return prev_data, roed_data, lamp_data
        
    except Exception as e:
        raise Exception(f"Error cargando datos de API: {str(e)}")


def process_location_data(prev_data, roed_data, lamp_data, location, mes_excluir):
    """
    Procesar datos para una ubicación específica
    
    Args:
        prev_data: Datos crudos de preventivos
        roed_data: Datos crudos de roedores  
        lamp_data: Datos crudos de lámparas
        location: 'Medellín' o 'Rionegro'
        mes_excluir: Mes a excluir del análisis
        
    Returns:
        tuple: (df_prev_full, df_roed_full, df_lamp_full)
    """
    try:
        # Filtrar datos por ubicación
        prev_location = prev_data[prev_data['Sede'] == location]
        roed_location = roed_data[roed_data['Sede'] == location]
        lamp_location = lamp_data[lamp_data['Sede'] == location]
        
        # Procesar datos
        _, df_prev_full = procesar_preventivos(prev_location)
        _, df_roed_full = procesar_roedores(roed_location)
        _, df_lamp_full = procesar_lamparas(lamp_location)
        
        # Excluir mes especificado
        if mes_excluir:
            df_prev_full = df_prev_full[df_prev_full['Mes'] != mes_excluir]
            df_roed_full = df_roed_full[df_roed_full['Mes'] != mes_excluir]
            df_lamp_full = df_lamp_full[df_lamp_full['Mes'] != mes_excluir]
        
        return df_prev_full, df_roed_full, df_lamp_full
    
    except Exception as e:
        raise Exception(f"Error procesando datos para {location}: {str(e)}")


def add_location_visualizations(informe, df_prev_full, df_roed_full, df_lamp_full, location_prefix):
    """
    Agregar todas las visualizaciones para una ubicación específica al reporte
    
    Args:
        informe: Instancia de InformeHospitalGenerator
        df_prev_full: Datos procesados de preventivos
        df_roed_full: Datos procesados de roedores
        df_lamp_full: Datos procesados de lámparas
        location_prefix: 'med' para Medellín, 'rio' para Rionegro
    """
    try:
        # Visualizaciones de preventivos
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
        
        # Visualizaciones de roedores
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

        # Visualizaciones de lámparas
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
        raise Exception(f"Error agregando visualizaciones para {location_prefix}: {str(e)}")


def generate_report_for_locations(locations, mes_excluir='Oct 2025', template_path='Plantilla.docx', return_buffer=True):
    """
    Generar reporte para ubicaciones especificadas
    
    Args:
        locations: Lista de ubicaciones ['Medellín', 'Rionegro'] o ubicación única
        mes_excluir: Mes a excluir del análisis
        template_path: Ruta a la plantilla Word
        return_buffer: Si es True, retorna buffer BytesIO; si es False, guarda a archivo
        
    Returns:
        Buffer BytesIO si return_buffer=True, nombre de archivo si return_buffer=False
    """
    try:
        # Asegurar que locations sea una lista
        if isinstance(locations, str):
            locations = [locations]
        
        # Cargar datos de API
        prev_data, roed_data, lamp_data = load_api_data()
        
        # Inicializar generador de reportes
        informe = InformeHospitalGenerator(template_path=template_path)
        
        # Procesar cada ubicación
        for location in locations:
            # Determinar prefijo de ubicación
            location_prefix = 'med' if location == 'Medellín' else 'rio'
            
            # Procesar datos de ubicación
            df_prev_full, df_roed_full, df_lamp_full = process_location_data(
                prev_data, roed_data, lamp_data, location, mes_excluir
            )
            
            # Agregar visualizaciones para esta ubicación
            add_location_visualizations(
                informe, df_prev_full, df_roed_full, df_lamp_full, location_prefix
            )
        
        # Generar reporte
        if return_buffer:
            buffer = informe.generar_informe(return_buffer=True)
            return buffer
        else:
            # Generar nombre de archivo basado en ubicaciones y fecha
            locations_str = "_".join(locations).replace('í', 'i').replace('ó', 'o')
            timestamp = datetime.now().strftime("%Y-%m-%d")
            filename = f'Informe_{locations_str}_{timestamp}.docx'
            informe.generar_informe(output_path=filename)
            return filename
            
    except Exception as e:
        raise Exception(f"Error generando reporte: {str(e)}")


def get_data_summary(prev_data, roed_data, lamp_data, locations):
    """
    Obtener estadísticas de resumen para los datos
    
    Args:
        prev_data: Datos crudos de preventivos
        roed_data: Datos crudos de roedores
        lamp_data: Datos crudos de lámparas
        locations: Lista de ubicaciones a analizar
        
    Returns:
        dict: Estadísticas de resumen
    """
    try:
        summary = {}
        
        for location in locations:
            location_summary = {}
            
            # Filtrar por ubicación
            prev_loc = prev_data[prev_data['Sede'] == location]
            roed_loc = roed_data[roed_data['Sede'] == location]
            lamp_loc = lamp_data[lamp_data['Sede'] == location]
            
            location_summary['preventivos_records'] = len(prev_loc)
            location_summary['roedores_records'] = len(roed_loc)
            location_summary['lamparas_records'] = len(lamp_loc)
            location_summary['total_records'] = len(prev_loc) + len(roed_loc) + len(lamp_loc)
            
            # Rangos de fechas
            if len(prev_loc) > 0:
                location_summary['date_range'] = f"{prev_loc['Fecha'].min()} - {prev_loc['Fecha'].max()}"
            
            summary[location] = location_summary
        
        return summary
        
    except Exception as e:
        raise Exception(f"Error generando resumen de datos: {str(e)}")