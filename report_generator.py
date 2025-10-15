import os
import pandas as pd
from dotenv import load_dotenv
from io import BytesIO
from datetime import datetime
import config as cfg

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
    Compatible con desarrollo local (.env) y Streamlit Cloud (secrets)
    
    Returns:
        tuple: (prev_data, roed_data, lamp_data)
    """
    try:
        # Intentar obtener configuración de múltiples fuentes en orden de prioridad:
        # 1. Variables de entorno (desarrollo local con .env)
        # 2. Secretos de Streamlit (despliegue en la nube)
        
        prev_api = None
        roe_api = None
        lam_api = None
        
        # Método 1: Intentar variables de entorno primero (desarrollo local)
        prev_api = os.getenv("prev_API")
        roe_api = os.getenv("roe_API") 
        lam_api = os.getenv("lam_API")
        
        # Método 2: Si no hay variables de entorno, intentar Streamlit secrets
        if not (prev_api and roe_api and lam_api):
            try:
                import streamlit as st
                
                # Detectar si estamos en Streamlit y si hay secretos disponibles
                if hasattr(st, 'secrets'):
                    # Usar secretos de Streamlit como respaldo
                    try:
                        prev_api = prev_api or st.secrets["prev_API"]
                    except KeyError:
                        pass
                    
                    try:
                        roe_api = roe_api or st.secrets["roe_API"]
                    except KeyError:
                        pass
                    
                    try:
                        lam_api = lam_api or st.secrets["lam_API"]
                    except KeyError:
                        pass
                    
            except (ImportError, AttributeError) as e:
                # Streamlit no disponible o secretos no configurados
                # Esto es normal en desarrollo local sin streamlit
                print(f"[Info] No se pudieron cargar secretos de Streamlit: {e}")
                pass
        
        # Validar que tengamos todas las APIs requeridas
        missing_apis = []
        if not prev_api:
            missing_apis.append("prev_API")
        if not roe_api:
            missing_apis.append("roe_API")
        if not lam_api:
            missing_apis.append("lam_API")
            
        if missing_apis:
            raise ValueError(
                f"Faltan las siguientes configuraciones de API: {', '.join(missing_apis)}. "
                f"Para desarrollo local: configura estas variables en tu archivo .env. "
                f"Para Streamlit Cloud: agrega estas claves en el secrets manager."
            )
        
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


def process_location_data(prev_data, roed_data, lamp_data, location, start_date=None, end_date=None):
    """
    Procesar datos para una ubicación específica
    
    Args:
        prev_data: Datos crudos de preventivos
        roed_data: Datos crudos de roedores  
        lamp_data: Datos crudos de lámparas
        location: 'Medellín' o 'Rionegro'
        start_date: Fecha inicial para filtrar (datetime.date)
        end_date: Fecha final para filtrar (datetime.date)
        
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
        
        # Filtrar por rango de fechas si se especifica
        if start_date and end_date:
            # Convertir fechas a datetime para comparación
            start_datetime = pd.to_datetime(start_date)
            end_datetime = pd.to_datetime(end_date)
            
            # Filtrar datos por rango de fechas
            if 'Fecha pandas' in df_prev_full.columns:
                df_prev_full = df_prev_full[
                    (df_prev_full['Fecha pandas'] >= start_datetime) & 
                    (df_prev_full['Fecha pandas'] <= end_datetime)
                ]
            if 'Fecha pandas' in df_roed_full.columns:
                df_roed_full = df_roed_full[
                    (df_roed_full['Fecha pandas'] >= start_datetime) & 
                    (df_roed_full['Fecha pandas'] <= end_datetime)
                ]
            if 'Fecha pandas' in df_lamp_full.columns:
                df_lamp_full = df_lamp_full[
                    (df_lamp_full['Fecha pandas'] >= start_datetime) & 
                    (df_lamp_full['Fecha pandas'] <= end_datetime)
                ]
        
        return df_prev_full, df_roed_full, df_lamp_full
    
    except Exception as e:
        raise Exception(f"Error procesando datos para {location}: {str(e)}")


def add_location_visualizations(informe, df_prev_full, df_roed_full, df_lamp_full):
    """
    Agregar todas las visualizaciones al reporte
    
    Args:
        informe: Instancia de InformeHospitalGenerator
        df_prev_full: Datos procesados de preventivos
        df_roed_full: Datos procesados de roedores
        df_lamp_full: Datos procesados de lámparas
    """
    try:
        # Visualizaciones de preventivos
        informe.agregar_resultado_completo(
            generate_order_area_plot, 
            df_prev_full,
            'preventivos_1_plot',
            'preventivos_1_tabla'
        )
        informe.agregar_resultado_completo(
            generate_plagas_timeseries_facet, 
            df_prev_full,
            'preventivos_2_plot',
            'preventivos_2_tabla'
        )
        informe.agregar_resultado_completo(
            generate_total_plagas_trend_plot, 
            df_prev_full,
            'preventivos_3_plot',
            'preventivos_3_tabla'
        )
        
        # Visualizaciones de roedores
        informe.agregar_resultado_completo(
            generate_roedores_station_status_plot, 
            df_roed_full,
            'roedores_1_plot',
            'roedores_1_tabla'
        )
        informe.agregar_resultado_completo(
            plot_tendencia_eliminacion_mensual,
            df_roed_full,
            'roedores_2_plot',
            'roedores_2_tabla'
        )

        # Visualizaciones de lámparas
        informe.agregar_resultado_completo(
            plot_estado_lamparas_por_mes,
            df_lamp_full,
            'lamparas_1_plot',
            'lamparas_1_tabla'
        )
        informe.agregar_resultado_completo(
            plot_estado_lamparas_con_leyenda,
            df_lamp_full,
            'lamparas_2_plot',
            'lamparas_2_tabla'
        )
        informe.agregar_resultado_completo(
            plot_capturas_especies_por_mes,
            df_lamp_full,
            'lamparas_3_plot',
            'lamparas_3_tabla'
        )
        informe.agregar_resultado_completo(
            plot_tendencia_total_capturas,
            df_lamp_full,
            'lamparas_4_plot',
            'lamparas_4_tabla'
        )
        
    except Exception as e:
        raise Exception(f"Error agregando visualizaciones: {str(e)}")


def calculate_areas_from_raw_data(data):
    """
    Calcular áreas controladas directamente desde los datos crudos
    
    Args:
        data: DataFrame con datos de preventivos filtrados
        
    Returns:
        str: String con áreas separadas por comas
    """
    try:
        if len(data) == 0:
            return 'Sin datos disponibles'
            
        # Buscar columnas de área/torre/bloque
        bt_cols = ['Torre o Área', 'Bloque o Área']
        available_cols = [col for col in bt_cols if col in data.columns]
        
        if not available_cols:
            return 'Columnas de área no encontradas'
        
        # Combinar las columnas disponibles
        areas_list = []
        for _, row in data.iterrows():
            area_parts = []
            for col in available_cols:
                if pd.notna(row[col]) and str(row[col]).strip():
                    area_parts.append(str(row[col]).strip())
            
            if area_parts:
                areas_list.append(' '.join(area_parts))
        
        # Obtener áreas únicas y ordenadas
        unique_areas = sorted(set(areas_list))
        unique_areas = [area for area in unique_areas if area and area != 'nan']
        
        return ', '.join(unique_areas) if unique_areas else 'Áreas no especificadas'
        
    except Exception as e:
        print(f"[Warning] Error en calculate_areas_from_raw_data: {e}")
        return 'Error al procesar áreas'


def calculate_report_variables(prev_data, sede, start_date, end_date):
    """
    Calcular variables específicas para el reporte Word
    
    Args:
        prev_data: Datos de preventivos
        sede: Sede seleccionada ('Medellín' o 'Rionegro')
        start_date: Fecha inicial del filtro
        end_date: Fecha final del filtro
        
    Returns:
        dict: Diccionario con variables para el reporte
    """
    try:
        # Filtrar datos por sede
        sede_data = prev_data[prev_data['Sede'] == sede].copy()
        
        # Filtrar por rango de fechas en los datos originales primero
        if start_date and end_date and 'Fecha' in sede_data.columns:
            # Convertir fechas a datetime
            sede_data.loc[:,'Fecha_temp'] = pd.to_datetime(sede_data['Fecha'], errors='coerce')
            start_datetime = pd.to_datetime(start_date)
            end_datetime = pd.to_datetime(end_date)
            
            sede_data = sede_data[
                (sede_data['Fecha_temp'] >= start_datetime) & 
                (sede_data['Fecha_temp'] <= end_datetime)
            ]
            sede_data = sede_data.drop('Fecha_temp', axis=1)
        
        # Calcular áreas controladas ANTES de procesar (desde datos originales)
        areas_controladas = calculate_areas_from_raw_data(sede_data)
        
        # Calcular variables específicas
        numero_solicitados = 0
        numero_realizados = 0
        mes_analisis = "No disponible"
        ano_analisis = datetime.now().year
        
        if len(sede_data) > 0:
            try:
                from data_preprocessing.pipeline import procesar_preventivos
                from data_visualization.preventivos import generate_order_area_plot
                
                # Procesar datos
                _, df_processed = procesar_preventivos(sede_data)
                
                if df_processed is not None and len(df_processed) > 0:
                    # numero_de_realizados: longitud del DataFrame procesado después del filtrado
                    numero_realizados = len(df_processed)
                    
                    # numero_de_solicitados: usar generate_order_area_plot para obtener 'Cantidad de órdenes'
                    try:
                        summary_df, _ = generate_order_area_plot(df_processed)
                        if len(summary_df) > 0 and 'Cantidad de órdenes' in summary_df.columns:
                            numero_solicitados = summary_df['Cantidad de órdenes'].sum()
                        else:
                            numero_solicitados = 0
                    except Exception as plot_error:
                        print(f"[Warning] Error calculando numero_de_solicitados: {plot_error}")
                        numero_solicitados = 0
                    
                    # mes_de_analisis: obtener el mes del 'Fecha pandas' máximo
                    try:
                        if 'Fecha pandas' in df_processed.columns:
                            max_date_row = df_processed.loc[df_processed['Fecha pandas'].idxmax()]
                            if 'Mes' in max_date_row:
                                mes_analisis = max_date_row['Mes']
                                # Extraer año del mes de análisis o de la fecha pandas
                                try:
                                    max_date = df_processed['Fecha pandas'].max()
                                    ano_analisis = max_date.year
                                except:
                                    ano_analisis = datetime.now().year
                            else:
                                mes_analisis = "No disponible"
                        else:
                            mes_analisis = "No disponible"
                    except Exception as date_error:
                        print(f"[Warning] Error calculando mes_de_analisis: {date_error}")
                        mes_analisis = "No disponible"
                    
            except Exception as e:
                print(f"[Warning] Error en procesamiento para variables adicionales: {e}")
                # Usar valores por defecto
        
        # Variables del reporte
        report_variables = {
            'fecha_de_elaboracion': datetime.now().strftime('%d/%m/%Y'),
            'dirección': cfg.direcciones.get(sede, '{{direccion_no_encontrada}}'),
            'sede': sede,
            'numero_de_solicitados': str(numero_solicitados),
            'numero_de_realizados': str(numero_realizados),
            'mes_de_analisis': mes_analisis,
            'ano_de_analisis': str(ano_analisis),
            'areas_controladas': areas_controladas
        }
        
        return report_variables
        
    except Exception as e:
        print(f"[Warning] Error calculando variables del reporte: {e}")
        # Valores por defecto en caso de error
        return {
            'fecha_de_elaboracion': datetime.now().strftime('%d/%m/%Y'),
            'dirección': cfg.direcciones.get(sede, '{{direccion_no_encontrada}}'),
            'sede': sede,
            'numero_de_solicitados': '0',
            'numero_de_realizados': '0',
            'mes_de_analisis': 'No disponible',
            'ano_de_analisis': str(datetime.now().year),
            'areas_controladas': 'Error al obtener áreas controladas'
        }


def generate_report_for_locations(locations, start_date=None, end_date=None, template_path='Plantilla.docx', return_buffer=True):
    """
    Generar reporte para ubicaciones especificadas
    
    Args:
        locations: Lista de ubicaciones ['Medellín', 'Rionegro'] o ubicación única
        start_date: Fecha inicial para filtrar (datetime.date)
        end_date: Fecha final para filtrar (datetime.date)
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
        
        # Calcular variables para el reporte
        report_data = calculate_report_variables(prev_data, locations[0], start_date, end_date)
        
        # Inicializar generador de reportes con variables adicionales
        informe = InformeHospitalGenerator(template_path=template_path)
        
        # Agregar variables del reporte al contexto
        for key, value in report_data.items():
            informe.context[key] = value
        
        # Procesar cada ubicación
        for location in locations:
            # Procesar datos de ubicación
            df_prev_full, df_roed_full, df_lamp_full = process_location_data(
                prev_data, roed_data, lamp_data, location, start_date, end_date
            )
            
            # Agregar visualizaciones
            add_location_visualizations(
                informe, df_prev_full, df_roed_full, df_lamp_full
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