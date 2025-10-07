"""
Aplicación Web Streamlit para Generación de Reportes de Control de Plagas Hospitalario
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import traceback
from report_generator import load_api_data, generate_report_for_locations, get_data_summary


# Configuración de página
st.set_page_config(
    page_title="Generador Reporte San Vicente",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para mejor estilización
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


@st.cache_data(ttl=3600)  # Cache por 1 hora
def cached_load_api_data():
    """Cargar datos de API con cache"""
    return load_api_data()


def main():
    # Encabezado principal
    st.markdown('<h1 class="main-header">🏥 Generador de Reportes de Control de Plagas Hospitalario</h1>', unsafe_allow_html=True)
    
    # Inicializar estado de sesión
    if 'report_generated' not in st.session_state:
        st.session_state.report_generated = False
    if 'report_buffer' not in st.session_state:
        st.session_state.report_buffer = None
    if 'report_filename' not in st.session_state:
        st.session_state.report_filename = None
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    
    # Configuración de barra lateral
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.header("📋 Configuración")
        
        # Selector de ubicación (solo una sede)
        st.subheader("🏢 Selección de Sede")
        location_options = ["Medellín", "Rionegro"]
        selected_location = st.selectbox(
            "Seleccionar sede hospitalaria:",
            options=location_options,
            index=0,  # Por defecto "Medellín"
            help="Elegir qué sede hospitalaria incluir en el reporte"
        )
        
        # Filtro de rango de fechas
        st.subheader("📅 Rango de Fechas")
        
        # Obtener fechas disponibles para el selector
        if st.session_state.data_loaded:
            try:
                prev_data, _, _ = st.session_state.api_data
                # Filtrar por sede seleccionada
                sede_data = prev_data[prev_data['Sede'] == selected_location]
                
                if len(sede_data) > 0 and 'Fecha' in sede_data.columns:
                    # Convertir fechas a datetime
                    sede_data['Fecha_dt'] = pd.to_datetime(sede_data['Fecha'], errors='coerce')
                    min_date = sede_data['Fecha_dt'].min().date()
                    max_date = sede_data['Fecha_dt'].max().date()
                    
                    # Selector de rango de fechas
                    date_range = st.date_input(
                        "Seleccionar rango de fechas para el análisis:",
                        value=(min_date, max_date),
                        min_value=min_date,
                        max_value=max_date,
                        help="Seleccionar fecha inicial y final para filtrar los datos"
                    )
                    
                    # Validar que se seleccionaron dos fechas
                    if isinstance(date_range, tuple) and len(date_range) == 2:
                        start_date, end_date = date_range
                        st.info(f"📅 Rango seleccionado: {start_date.strftime('%Y-%m-%d')} a {end_date.strftime('%Y-%m-%d')}")
                    else:
                        st.warning("⚠️ Por favor selecciona una fecha inicial y una fecha final.")
                        start_date, end_date = min_date, max_date
                else:
                    st.warning("⚠️ No se encontraron datos de fecha para la sede seleccionada.")
                    start_date = end_date = datetime.now().date()
                    
            except Exception as e:
                st.warning(f"⚠️ Error al obtener rango de fechas: {str(e)}")
                start_date = end_date = datetime.now().date()
        else:
            # Valores por defecto cuando no hay datos cargados
            default_end = datetime.now().date()
            default_start = default_end - timedelta(days=365)  # 1 año atrás
            
            date_range = st.date_input(
                "Seleccionar rango de fechas para el análisis:",
                value=(default_start, default_end),
                help="Seleccionar fecha inicial y final para filtrar los datos"
            )
            
            if isinstance(date_range, tuple) and len(date_range) == 2:
                start_date, end_date = date_range
            else:
                start_date, end_date = default_start, default_end
        
        # Opciones avanzadas
        with st.expander("⚙️ Opciones Avanzadas"):
            template_file = st.file_uploader(
                "Plantilla Word Personalizada (opcional):",
                type=['docx'],
                help="Subir una plantilla Word personalizada. Si no se proporciona, se usará la plantilla por defecto."
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Sección de carga de datos
        st.markdown("---")
        st.subheader("📊 Estado de Datos")
        
        if st.button("🔄 Cargar/Actualizar Datos", use_container_width=True):
            with st.spinner("Cargando datos desde APIs..."):
                try:
                    # Limpiar cache y cargar datos frescos
                    cached_load_api_data.clear()
                    prev_data, roed_data, lamp_data = cached_load_api_data()
                    st.session_state.data_loaded = True
                    st.session_state.api_data = (prev_data, roed_data, lamp_data)
                    st.success("✅ ¡Datos cargados exitosamente!")
                except Exception as e:
                    st.error(f"❌ Error cargando datos: {str(e)}")
                    st.session_state.data_loaded = False
    
    # Área de contenido principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 Generación de Reportes")
        
        # Cargar datos automáticamente en la primera ejecución
        if not st.session_state.data_loaded:
            with st.spinner("Cargando datos iniciales..."):
                try:
                    prev_data, roed_data, lamp_data = cached_load_api_data()
                    st.session_state.data_loaded = True
                    st.session_state.api_data = (prev_data, roed_data, lamp_data)
                    st.success("✅ ¡Datos iniciales cargados exitosamente!")
                except Exception as e:
                    error_msg = str(e)
                    if "your-actual-api-endpoint" in error_msg:
                        st.error("❌ **Configuración Requerida**: Por favor actualiza los endpoints de API en tu archivo `.env`")
                        st.info("""
                        **Para configurar la aplicación:**
                        
                        1. Abre el archivo `.env` en el directorio del proyecto
                        2. Reemplaza las URLs de prueba con tus endpoints reales de API:
                           - `prev_API=https://tu-endpoint-real.com/datos-preventivos`
                           - `roe_API=https://tu-endpoint-real.com/datos-roedores`
                           - `lam_API=https://tu-endpoint-real.com/datos-lamparas`
                        3. Actualiza esta página
                        """)
                    else:
                        st.error(f"❌ Error cargando datos iniciales: {error_msg}")
                        
                        with st.expander("🔍 Solución de Problemas"):
                            st.markdown("""
                            **Problemas comunes:**
                            - Verifica tu conexión a internet
                            - Confirma que los endpoints de API sean accesibles
                            - Asegúrate que los endpoints de API retornen datos en el formato esperado
                            - Verifica si se requiere autenticación para las APIs
                            """)
                    st.stop()
        
        # Resumen de datos
        if st.session_state.data_loaded:
            try:
                prev_data, roed_data, lamp_data = st.session_state.api_data
                
                # Determinar ubicación para procesamiento (solo una sede)
                locations_to_process = [selected_location]
                
                # Mostrar resumen de datos
                with st.expander("📊 Resumen de Datos", expanded=False):
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
                            st.caption(f"Rango de fechas: {stats['date_range']}")
                        st.markdown("---")
                
            except Exception as e:
                st.error(f"Error generando resumen de datos: {str(e)}")
        
        # Botón de generación de reporte
        if st.button("🚀 Generar Reporte", use_container_width=True, type="primary"):
            if not st.session_state.data_loaded:
                st.error("❌ ¡Por favor carga los datos primero!")
                return
            
            # Determinar ubicación para procesamiento (solo una sede)
            locations_to_process = [selected_location]
            filename_location = selected_location.replace('í', 'i').replace('ó', 'o')
            
            # Mostrar progreso
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Paso 1: Procesar datos
                status_text.text("🔄 Procesando datos...")
                progress_bar.progress(20)
                
                # Paso 2: Generar visualizaciones
                status_text.text("📊 Generando visualizaciones...")
                progress_bar.progress(50)
                
                # Paso 3: Crear reporte
                status_text.text("📄 Creando documento Word...")
                progress_bar.progress(80)
                
                # Generar reporte
                template_path = 'Plantilla.docx'
                if template_file is not None:
                    # Guardar plantilla subida temporalmente
                    with open('temp_template.docx', 'wb') as f:
                        f.write(template_file.getvalue())
                    template_path = 'temp_template.docx'
                
                buffer = generate_report_for_locations(
                    locations=locations_to_process,
                    start_date=start_date,
                    end_date=end_date,
                    template_path=template_path,
                    return_buffer=True
                )
                
                # Paso 4: Finalizar
                status_text.text("✅ ¡Reporte generado exitosamente!")
                progress_bar.progress(100)
                
                # Almacenar en estado de sesión
                st.session_state.report_generated = True
                st.session_state.report_buffer = buffer
                
                # Generar nombre de archivo
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
                st.session_state.report_filename = f"Informe_{filename_location}_{timestamp}.docx"
                
                # Mensaje de éxito
                st.markdown(
                    '<div class="success-message">✅ <strong>¡Reporte generado exitosamente!</strong> Usa el botón de descarga a continuación para guardar el archivo.</div>',
                    unsafe_allow_html=True
                )
                
                # Limpiar plantilla temporal si se usó
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
                    f'<div class="error-message">❌ <strong>Error generando reporte:</strong><br>{str(e)}</div>',
                    unsafe_allow_html=True
                )
                
                # Mostrar error detallado en expansor para depuración
                with st.expander("🔍 Detalles del Error"):
                    st.code(error_details)
                
                st.session_state.report_generated = False
    
    with col2:
        st.subheader("💾 Descarga")
        
        if st.session_state.report_generated and st.session_state.report_buffer:
            st.success("📄 ¡Reporte listo para descarga!")
            
            # Botón de descarga
            st.download_button(
                label="⬇️ Descargar Reporte",
                data=st.session_state.report_buffer.getvalue(),
                file_name=st.session_state.report_filename,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
            
            # Información del reporte
            st.info(f"**Nombre del archivo:** {st.session_state.report_filename}")
            
            # Botón de reinicio
            if st.button("🔄 Generar Nuevo Reporte", use_container_width=True):
                st.session_state.report_generated = False
                st.session_state.report_buffer = None
                st.session_state.report_filename = None
                st.rerun()
        
        else:
            st.info("Genera un reporte para habilitar la descarga")
        
        # Sección de ayuda
        st.markdown("---")
        st.subheader("ℹ️ Ayuda")
        with st.expander("Cómo usar esta aplicación"):
            st.markdown("""
            **Pasos para generar un reporte:**
            
            1. **Seleccionar Sede**: Elegir qué sede hospitalaria incluir (Medellín o Rionegro)
            2. **Configurar Rango de Fechas**: Seleccionar fecha inicial y final para el análisis
            3. **Cargar Datos**: Hacer clic en 'Cargar/Actualizar Datos' para obtener la información más reciente
            4. **Generar Reporte**: Hacer clic en 'Generar Reporte' para crear el documento Word
            5. **Descargar**: Usar el botón de descarga para guardar el reporte
            
            **Consejos:**
            - La aplicación carga datos automáticamente al abrirse por primera vez
            - Solo se puede seleccionar una sede a la vez
            - El rango de fechas se ajusta automáticamente según los datos disponibles
            - Los reportes incluyen visualizaciones y tablas detalladas
            - Los archivos generados se nombran con sede y marca de tiempo
            """)
        
        with st.expander("Solución de Problemas"):
            st.markdown("""
            **Problemas comunes:**
            
            - **Falla la carga de datos**: Verificar conexión a internet y endpoints de API
            - **Falla la generación de reporte**: Asegurar que la plantilla Word sea válida
            - **La descarga no funciona**: Intentar generar el reporte nuevamente
            
            **Rango de fechas:**
            - Seleccionar tanto fecha inicial como fecha final
            - El rango se ajusta automáticamente según los datos disponibles para cada sede
            - Los datos fuera del rango seleccionado se excluyen del análisis
            """)


if __name__ == "__main__":
    main()