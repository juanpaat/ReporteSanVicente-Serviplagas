import os
import pandas as pd
from dotenv import load_dotenv
from io import BytesIO
from datetime import datetime
import config as cfg
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importaciones de procesamiento de datos
from data_preprocessing.pipeline import leer_data, procesar_preventivos, procesar_lamparas, procesar_roedores, procesar_correctivos
import ssl
import urllib3

# Importaciones de visualización
from data_visualization.preventivos import generate_order_area_plot, generate_plagas_timeseries_facet, generate_total_plagas_trend_plot
from data_visualization.roedores import generate_roedores_station_status_plot, plot_tendencia_eliminacion_mensual
from data_visualization.lamparas import plot_estado_lamparas_por_mes, plot_estado_lamparas_con_leyenda, plot_capturas_especies_por_mes, plot_tendencia_total_capturas
from data_visualization.correctivos import generate_order_comparison_plot, plot_tendencia_total_eliminacion, plot_nivel_de_infestación, plot_plagas_por_especie_mes
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
        corr_api = None
        
        # Método 1: Intentar variables de entorno primero (desarrollo local)
        prev_api = os.getenv("prev_API")
        roe_api = os.getenv("roe_API") 
        lam_api = os.getenv("lam_API")
        corr_api = os.getenv("cor_API")
        
        # Método 2: Si no hay variables de entorno, intentar Streamlit secrets
        if not (prev_api and roe_api and lam_api and corr_api):
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

                    try:
                        corr_api = corr_api or st.secrets["cor_API"]
                    except KeyError:
                        pass
                    
            except (ImportError, AttributeError) as e:
                # Streamlit no disponible o secretos no configurados
                # Esto es normal en desarrollo local sin streamlit
                logger.info(f"No se pudieron cargar secretos de Streamlit: {e}")
                pass
        
        # Validar que tengamos todas las APIs requeridas
        missing_apis = []
        if not prev_api:
            missing_apis.append("prev_API")
        if not roe_api:
            missing_apis.append("roe_API")
        if not lam_api:
            missing_apis.append("lam_API")
        if not corr_api:
            missing_apis.append("cor_API")
            
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
            corr_data = leer_data(corr_api)
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
        
        return prev_data, roed_data, lamp_data, corr_data
        
    except Exception as e:
        raise Exception(f"Error cargando datos de API: {str(e)}")


def process_location_data(prev_data, roed_data, lamp_data, corr_data, location, start_date=None, end_date=None):
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
        corr_location = corr_data[corr_data['Sede'] == location]
        
        # Procesar datos
        _, df_prev_full = procesar_preventivos(prev_location)
        _, df_roed_full = procesar_roedores(roed_location)
        _, df_lamp_full = procesar_lamparas(lamp_location)
        _, df_corr_full = procesar_correctivos(corr_location)
        
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
            if 'Fecha pandas' in df_corr_full.columns:
                df_corr_full = df_corr_full[
                    (df_corr_full['Fecha pandas'] >= start_datetime) & 
                    (df_corr_full['Fecha pandas'] <= end_datetime)
                ]
        
        return df_prev_full, df_roed_full, df_lamp_full, df_corr_full
    
    except Exception as e:
        raise Exception(f"Error procesando datos para {location}: {str(e)}")


def add_location_visualizations(informe, df_prev_full, df_roed_full, df_lamp_full, df_corr_full):
    """
    Agregar todas las visualizaciones al reporte
    
    Args:
        informe: Instancia de InformeHospitalGenerator
        df_prev_full: Datos procesados de preventivos
        df_roed_full: Datos procesados de roedores
        df_lamp_full: Datos procesados de lámparas
        df_corr_full: Datos procesados de correctivos
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
        # Visualizaciones de correctivos
        informe.agregar_resultado_completo(
            generate_order_comparison_plot,
            df_corr_full,
            'correctivo_1_plot',
            'correctivo_1_tabla'
        )
        informe.agregar_resultado_completo(
            plot_tendencia_total_eliminacion,
            df_corr_full,
            'correctivo_2_plot',
            'correctivo_2_tabla'
        )
        informe.agregar_resultado_completo(
            plot_nivel_de_infestación,
            df_corr_full,
            'correctivo_3_plot',
            'correctivo_3_tabla'
        )
        informe.agregar_resultado_completo(
            plot_plagas_por_especie_mes,
            df_corr_full,
            'correctivo_4_plot',
            'correctivo_4_tabla'
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
        logger.warning(f"Error en calculate_areas_from_raw_data: {e}")
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
        porcentaje_realizados = 0.0
        fecha_elaboracion = datetime.now().strftime('%d/%m/%Y')  # Default value
        
        if len(sede_data) > 0:
            try:
                from data_preprocessing.pipeline import procesar_preventivos
                from data_visualization.preventivos import generate_order_area_plot
                
                # Procesar datos
                logger.info(f"Procesando {len(sede_data)} registros para {sede}")
                _, df_processed = procesar_preventivos(sede_data)
                
                if df_processed is not None and len(df_processed) > 0:
                    logger.info(f"Datos procesados: {len(df_processed)} registros")
                    logger.info(f"Columnas disponibles: {df_processed.columns.tolist()}")
                    
                    # mes_de_analisis: obtener el mes del 'Fecha pandas' máximo
                    try:
                        if 'Fecha pandas' in df_processed.columns:
                            # Remove NaT values before getting max
                            valid_dates = df_processed['Fecha pandas'].dropna()
                            logger.info(f"Fechas válidas encontradas: {len(valid_dates)}")
                            
                            if len(valid_dates) == 0:
                                raise ValueError("No hay fechas válidas en los datos procesados")
                            
                            max_date = valid_dates.max()
                            logger.info(f"Fecha máxima encontrada: {max_date}")
                            
                            # Verify max_date is not NaT
                            if pd.isna(max_date):
                                raise ValueError("La fecha máxima es NaT (Not a Time)")
                            
                            # Calcular el último día del mes de la fecha máxima
                            import calendar
                            last_day = calendar.monthrange(max_date.year, max_date.month)[1]
                            last_date_of_month = max_date.replace(day=last_day)
                            fecha_elaboracion = last_date_of_month.strftime('%d/%m/%Y')
                            logger.info(f"fecha_de_elaboracion calculada: {fecha_elaboracion}")
                            
                            # Get the row with max date
                            max_date_row = df_processed.loc[df_processed['Fecha pandas'] == max_date].iloc[0]
                            
                            if 'Mes' in max_date_row:
                                mes_analisis = max_date_row['Mes']
                                try:
                                    ano_analisis = max_date.year
                                except:
                                    ano_analisis = datetime.now().year
                                logger.info(f"mes_de_analisis: {mes_analisis}, año: {ano_analisis}")
                            else:
                                mes_analisis = "No disponible"
                                logger.info("Columna 'Mes' no encontrada en los datos")
                            
                            # numero_de_realizados: contar subáreas únicas del último mes
                            # Filtrar df_processed para obtener solo los registros del último mes
                            last_month_data = df_processed[
                                (df_processed['Fecha pandas'].dt.year == max_date.year) & 
                                (df_processed['Fecha pandas'].dt.month == max_date.month)
                            ]
                            logger.info(f"Registros del último mes: {len(last_month_data)}")
                            # Contar subáreas únicas (igual que en preventivos_1_plot)
                            if 'Subárea' in last_month_data.columns:
                                numero_realizados = last_month_data['Subárea'].nunique()
                            else:
                                numero_realizados = len(last_month_data)
                            logger.info(f"numero_de_realizados: {numero_realizados}")
                        else:
                            mes_analisis = "No disponible"
                            numero_realizados = 0
                            logger.info("Columna 'Fecha pandas' no encontrada")
                    except Exception as date_error:
                        logger.error(f"Error calculando mes_de_analisis y numero_realizados: {date_error}")
                        import traceback
                        print(traceback.format_exc())
                        mes_analisis = "No disponible"
                        numero_realizados = 0
                        # Mantener fecha_elaboracion con valor por defecto
                    
                    # numero_de_solicitados: usar generate_order_area_plot para obtener 'Cantidad de órdenes' del último mes
                    try:
                        summary_df, _ = generate_order_area_plot(df_processed)
                        logger.info(f"Summary DF generado con {len(summary_df)} filas")
                        if len(summary_df) > 0 and 'Cantidad de órdenes' in summary_df.columns and mes_analisis != "No disponible":
                            # Filtrar solo el último mes
                            last_month_summary = summary_df[summary_df['Mes'] == mes_analisis]
                            if len(last_month_summary) > 0:
                                numero_solicitados = int(last_month_summary['Cantidad de órdenes'].iloc[0])
                            else:
                                numero_solicitados = 0
                        else:
                            numero_solicitados = 0
                        logger.info(f"numero_de_solicitados: {numero_solicitados}")
                    except Exception as plot_error:
                        logger.error(f"Error calculando numero_de_solicitados: {plot_error}")
                        import traceback
                        print(traceback.format_exc())
                        numero_solicitados = 0
                    
                    # porcentaje_de_realizados: número de meses únicos en el dataset / 12
                    try:
                        if 'Mes' in df_processed.columns:
                            # Remove null/NaN values before counting unique months
                            valid_months = df_processed['Mes'].dropna()
                            logger.info(f"Meses válidos encontrados: {len(valid_months)}")
                            if len(valid_months) > 0:
                                numero_meses = valid_months.nunique()
                                porcentaje_realizados = round(numero_meses / 12 * 100, 2)
                                logger.info(f"Meses únicos: {numero_meses}, porcentaje: {porcentaje_realizados}%")
                            else:
                                logger.warning("No hay meses válidos en los datos")
                                porcentaje_realizados = 0.0
                        else:
                            logger.info("Columna 'Mes' no encontrada para calcular porcentaje")
                            porcentaje_realizados = 0.0
                    except Exception as perc_error:
                        logger.error(f"Error calculando porcentaje_de_realizados: {perc_error}")
                        import traceback
                        print(traceback.format_exc())
                        porcentaje_realizados = 0.0
                else:
                    logger.warning("df_processed está vacío o es None")
                    
            except Exception as e:
                logger.error(f"Error en procesamiento para variables adicionales: {e}")
                import traceback
                print(traceback.format_exc())
                # Usar valores por defecto
        
        # Determinar descripción de áreas según la sede
        if sede == 'Medellín':
            numero_de_bloques = 'los 17 bloques'
        elif sede == 'Rionegro':
            numero_de_bloques = 'las 4 torres'
        else:
            numero_de_bloques = 'las áreas'  # Valor por defecto
        
        # Determinar análisis de roedores según la sede
        if sede == 'Medellín':
            analisis_roedores = """ -	Primera visita 13 de diciembre: bioindicador, deterioro, estación desaparecida y consumo. Estación # (3 y 35).\n
            
 -	Segunda visita 27 de diciembre: bioindicador, deterioro, estación desaparecida y consumo. Estación # (37 y 44).\n
 
 En el mes de diciembre se presenta consumo en cuatro estaciones en las dos visitas (3, 35, 27 y 44), se mantiene; en recorridos preventivos y zona común, no se presentan episodios con roedores en correctivos salvo reporte de avistamientos los cuales se ceban, dos roedores atrapados, uno vivo y otro muerto en trampa de medicina física y rehabilitación y dos madrigueras activas. Las estaciones 3, 4 y 5 están bloqueadas por remodelación de área.\n
 
 Los días de las visitas se dieron el 13 y el 27 de diciembre.  No se repite el consumo; Se halla bioindicador en 13 estaciones, todas por hormigas consumiendo el cebo; 2, 7, 8, 9, 9, 10, 11, 11, 13, 37, 38, 43 y 43; hormigas de fuego especialmente, rojas y cachonas, consumiendo el cebo en las cajas. La estación # 36 estaba desaparecida, se reemplaza al final del mes. Se presenta deterioro en 2 estaciones por condiciones climatológicas: 30 y 34, estas dos también presentaban deterioro en el mes pasado. 
Se realizaron en total 2 visitas a las estaciones portacebos y porta adhesivos del Hospital Universitario para el mes de diciembre.
"""
        elif sede == 'Rionegro':
            analisis_roedores = """Se hacen en total DOS visitas, el 05 y 20 de diciembre; Durante el mes no se presenta consumo en las estaciones. Se evidencia deterioro en 4 cajas, se reduce con relación al mes pasado; en las estaciones 25, 29, 31 y 33 en la primera visita, esto debido a las condiciones atmosféricas del mes. Ni en preventivos, ni en correctivos ocurren hallazgos relacionados con roedores salvo el consumo presentado el cual es esporádico, casi nunca se presenta. 

            Se hace limpieza a las 46 estaciones. Todas las estaciones se encuentran en buen estado.
"""
        else:
            analisis_roedores = 'Aqui va el analisis de los roedores'  # Valor por defecto
        
        # Determinar análisis de preventivos según la sede
        if sede == 'Medellín':
            analisis_preventivos = 'Aqui va el analisis de los preventivos Medellín'
        elif sede == 'Rionegro':
            analisis_preventivos = """En diciembre no se evidencian plagas en los controles preventivos.
CUCARACHAS: No se hallan cucarachas alemanas, tampoco americanas. 

VOLADORES: Nuevamente no presencia de moscas y zancudos lo cual sigue siento signo positivo y resulta crucial mantener medidas preventivas, como el control de áreas propensas a agua estancada y residuos para evitar futuros brotes.
ROEDORES: Sin indicadores de ratas ni ratones, la gestión de residuos y alimentos debe continuar siendo optimizada para evitar atraer a estos roedores en el futuro.
HORMIGAS: El combate semanal nuevamente da sus frutos, pero no se contabiliza en preventivos ya que no se presentaron hormigas al interior del hospital.
OTRAS PLAGAS: No se reportan otras plagas en los controles preventivos del mes."""
        else:
            analisis_preventivos = 'Aqui va el analisis de los preventivos'  # Valor por defecto
        
        # Determinar análisis de lámparas según la sede
        if sede == 'Medellín':
            analisis_lamparas = 'Aqui va el analisis de las lamparas Medellín'
        elif sede == 'Rionegro':
            analisis_lamparas = """Distribución de estados observados

•	Buena potencia: 07 estaciones

•	Lámina saturada: 0 estaciones

•	Bombillo averiado: 1 estaciones (fueron reemplazados bombillos fundidos

•	Faltante: 0 estación.

•	Obstruida, desconectada, deteriorada o apagada: sin registros

Interpretación técnica

El análisis evidencia que el total de las estaciones (7 unidades) se encuentran en óptimas condiciones de funcionamiento, lo que demuestra una buena conservación y mantenimiento del sistema lumínico en general. Sin embargo, no se observa un número equivalente de láminas saturadas, lo que indica una baja actividad de insectos voladores.
Conclusión
El estado general de las estaciones lumínicas durante diciembre 2025 es positivo y funcional, con el 100 % de las unidades operativas y una gestión preventiva activa.
El resultado confirma que el programa inicia el nuevo ciclo con buen nivel de operatividad técnica, evidenciando seguimiento, control y pronta respuesta a las novedades detectadas.
"""
        else:
            analisis_lamparas = 'Aqui va el analisis de las lamparas'  # Valor por defecto
        
        # Variables del reporte
        report_variables = {
            'fecha_de_elaboracion': fecha_elaboracion,
            'dirección': cfg.direcciones.get(sede, '{{direccion_no_encontrada}}'),
            'sede': sede,
            'numero_de_solicitados': str(numero_solicitados),
            'numero_de_realizados': str(numero_realizados),
            'mes_de_analisis': mes_analisis,
            'ano_de_analisis': str(ano_analisis),
            'areas_controladas': areas_controladas,
            'porcentaje_de_realizados': str(porcentaje_realizados),
            'numero_de_bloques': numero_de_bloques,
            'analisis_roedores': analisis_roedores,
            'analisis_preventivos': analisis_preventivos,
            'analisis_lamparas': analisis_lamparas
        }
        
        # Log final values for debugging
        logger.info("===== VARIABLES FINALES DEL REPORTE =====")
        for key, value in report_variables.items():
            logger.info(f"{key}: {value}")
        logger.info("==========================================")
        
        return report_variables
        
    except Exception as e:
        logger.error(f"Error calculando variables del reporte: {e}")
        import traceback
        print(traceback.format_exc())
        
        # Determinar descripción de áreas según la sede (para valores por defecto)
        if sede == 'Medellín':
            numero_de_bloques = 'los 17 bloques'
        elif sede == 'Rionegro':
            numero_de_bloques = 'las 4 torres'
        else:
            numero_de_bloques = 'las áreas'
        
        # Determinar análisis de roedores según la sede (para valores por defecto)
        if sede == 'Medellín':
            analisis_roedores = 'Aqui va el analisis de los roedores Medellín'
        elif sede == 'Rionegro':
            analisis_roedores = 'Aqui va el analisis de los roedores Rionegro'
        else:
            analisis_roedores = 'Aqui va el analisis de los roedores'
        
        # Determinar análisis de preventivos según la sede (para valores por defecto)
        if sede == 'Medellín':
            analisis_preventivos = 'Aqui va el analisis de los preventivos Medellín'
        elif sede == 'Rionegro':
            analisis_preventivos = 'Aqui va el analisis de los preventivos Rionegro'
        else:
            analisis_preventivos = 'Aqui va el analisis de los preventivos'
        
        # Determinar análisis de lámparas según la sede (para valores por defecto)
        if sede == 'Medellín':
            analisis_lamparas = 'Aqui va el analisis de las lamparas Medellín'
        elif sede == 'Rionegro':
            analisis_lamparas = 'Aqui va el analisis de las lamparas Rionegro'
        else:
            analisis_lamparas = 'Aqui va el analisis de las lamparas'
        
        # Valores por defecto en caso de error
        default_vars = {
            'fecha_de_elaboracion': datetime.now().strftime('%d/%m/%Y'),
            'dirección': cfg.direcciones.get(sede, '{{direccion_no_encontrada}}'),
            'sede': sede,
            'numero_de_solicitados': '0',
            'numero_de_realizados': '0',
            'mes_de_analisis': 'No disponible',
            'ano_de_analisis': str(datetime.now().year),
            'areas_controladas': 'Error al obtener áreas controladas',
            'porcentaje_de_realizados': '0.0',
            'numero_de_bloques': numero_de_bloques,
            'analisis_roedores': analisis_roedores,
            'analisis_preventivos': analisis_preventivos,
            'analisis_lamparas': analisis_lamparas
        }
        logger.info("===== USANDO VALORES POR DEFECTO (ERROR) =====")
        for key, value in default_vars.items():
            logger.info(f"{key}: {value}")
        logger.info("=================================================")
        return default_vars


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
        prev_data, roed_data, lamp_data, corr_data = load_api_data()
        
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
            df_prev_full, df_roed_full, df_lamp_full, df_corr_full = process_location_data(
                prev_data, roed_data, lamp_data, corr_data, location, start_date, end_date
            )
            
            # Agregar visualizaciones
            add_location_visualizations(
                informe, df_prev_full, df_roed_full, df_lamp_full, df_corr_full
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


def get_data_summary(prev_data, roed_data, lamp_data, corr_data,  locations):
    """
    Obtener estadísticas de resumen para los datos
    
    Args:
        prev_data: Datos crudos de preventivos
        roed_data: Datos crudos de roedores
        lamp_data: Datos crudos de lámparas
        corr_data: Datos crudos de correctivos
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
            corr_loc = corr_data[corr_data['Sede'] == location]
            
            location_summary['preventivos_records'] = len(prev_loc)
            location_summary['roedores_records'] = len(roed_loc)
            location_summary['lamparas_records'] = len(lamp_loc)
            location_summary['correctivos_records'] = len(corr_loc)
            location_summary['total_records'] = len(prev_loc) + len(roed_loc) + len(lamp_loc) + len(corr_loc)
            
            # Rangos de fechas
            if len(prev_loc) > 0:
                location_summary['date_range'] = f"{prev_loc['Fecha'].min()} - {prev_loc['Fecha'].max()}"
            
            summary[location] = location_summary
        
        return summary
        
    except Exception as e:
        raise Exception(f"Error generando resumen de datos: {str(e)}")