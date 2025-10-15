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
    st.markdown('<h1 class="main-header">🏥 Generador de Reportes de Control de Plagas San Vicente Fundación</h1>', unsafe_allow_html=True)
    
    # Inicializar estado de sesión
    if 'report_generated' not in st.session_state:
        st.session_state.report_generated = False
    if 'report_buffer' not in st.session_state:
        st.session_state.report_buffer = None
    if 'report_filename' not in st.session_state:
        st.session_state.report_filename = None
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'config_set' not in st.session_state:
        st.session_state.config_set = False
    if 'selected_location' not in st.session_state:
        st.session_state.selected_location = None
    if 'date_range' not in st.session_state:
        st.session_state.date_range = None
    if 'template_file' not in st.session_state:
        st.session_state.template_file = None
    
    # Configuración de barra lateral - PASO 1: Configuración de Parámetros
    with st.sidebar:
        # Logo centrado y más grande en la parte superior del sidebar
        col1, col2, col3 = st.columns([0.5, 3, 0.5])
        with col2:
            st.image("logo2021.png", use_column_width=True)
        st.markdown("---")
        
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)

        # Selector de ubicación (solo una sede)
        st.subheader("🏢 Selección de Sede")
        location_options = ["Medellín", "Rionegro"]
        selected_location = st.selectbox(
            "Seleccionar sede hospitalaria:",
            options=location_options,
            index=0 if st.session_state.selected_location is None else location_options.index(st.session_state.selected_location) if st.session_state.selected_location in location_options else 0,
            help="Elegir qué sede hospitalaria incluir en el reporte",
            disabled=st.session_state.config_set
        )
        
        # Filtro de rango de fechas
        st.subheader("📅 Rango de Fechas")
        
        # Definir rango por defecto: Septiembre 1, 2025 hasta hoy
        default_start = datetime(2025, 9, 1).date()
        default_end = datetime.now().date()
        
        # Usar valores guardados o por defecto
        if st.session_state.date_range is None:
            default_dates = (default_start, default_end)
        else:
            default_dates = st.session_state.date_range
        
        # Obtener límites de fechas si hay datos cargados
        min_date = default_start
        max_date = default_end
        
        if st.session_state.data_loaded:
            try:
                prev_data, _, _ = st.session_state.api_data
                # Filtrar por sede seleccionada
                sede_data = prev_data[prev_data['Sede'] == selected_location]
                
                if len(sede_data) > 0 and 'Fecha' in sede_data.columns:
                    # Convertir fechas a datetime
                    sede_data['Fecha_dt'] = pd.to_datetime(sede_data['Fecha'], errors='coerce')
                    api_min_date = sede_data['Fecha_dt'].min().date()
                    api_max_date = sede_data['Fecha_dt'].max().date()
                    
                    # Usar el rango más amplio entre datos de API y valores por defecto
                    min_date = min(api_min_date, default_start) if api_min_date else default_start
                    max_date = max(api_max_date, default_end) if api_max_date else default_end
                    
                    # Asegurar que las fechas por defecto estén dentro del rango permitido
                    if default_dates[0] < min_date:
                        default_dates = (min_date, default_dates[1])
                    if default_dates[1] > max_date:
                        default_dates = (default_dates[0], max_date)
                        
            except Exception as e:
                st.warning(f"⚠️ Error al obtener rango de fechas de API: {str(e)}")
                # Usar valores por defecto en caso de error
                min_date = default_start
                max_date = default_end
        
        # Selector de rango de fechas
        date_range = st.date_input(
            "Seleccionar rango de fechas para el análisis:",
            value=default_dates,
            min_value=min_date,
            max_value=max_date,
            help="Seleccionar fecha inicial y final para filtrar los datos",
            disabled=st.session_state.config_set
        )
        
        # Validar que se seleccionaron dos fechas
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
            if not st.session_state.config_set:
                st.info(f"📅 Rango seleccionado: {start_date.strftime('%Y-%m-%d')} a {end_date.strftime('%Y-%m-%d')}")
        else:
            st.warning("⚠️ Por favor selecciona una fecha inicial y una fecha final.")
            start_date, end_date = default_dates
        
        # Plantilla Word
        st.subheader("📄 Plantilla Word")
        template_file = st.file_uploader(
            "Plantilla Word Personalizada (opcional):",
            type=['docx'],
            help="Subir una plantilla Word personalizada. Si no se proporciona, se usará la plantilla por defecto.",
            disabled=st.session_state.config_set
        )
        
        # Botón de configuración
        st.markdown("---")
        if not st.session_state.config_set:
            if st.button("⚙️ Establecer Configuración", use_container_width=True, type="primary"):
                # Validar configuración
                if isinstance(date_range, tuple) and len(date_range) == 2:
                    st.session_state.config_set = True
                    st.session_state.selected_location = selected_location
                    st.session_state.date_range = date_range
                    st.session_state.template_file = template_file
                    st.rerun()
                else:
                    st.error("⚠️ Por favor selecciona un rango de fechas válido (fecha inicial y final).")
        else:
            # Mostrar configuración actual
            st.markdown("**Configuración Actual:**")
            st.write(f"🏢 **Sede:** {st.session_state.selected_location}")
            st.write(f"📅 **Fechas:** {st.session_state.date_range[0]} a {st.session_state.date_range[1]}")
            if st.session_state.template_file:
                st.write(f"📄 **Plantilla:** {st.session_state.template_file.name}")
            else:
                st.write(f"📄 **Plantilla:** Plantilla por defecto")
            
            if st.button("🔄 Nueva Configuración", use_container_width=True):
                # Resetear estado para nueva configuración
                st.session_state.config_set = False
                st.session_state.report_generated = False
                st.session_state.report_buffer = None
                st.session_state.report_filename = None
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Sección de carga de datos
        st.markdown("---")
        st.subheader("📊 Estado de Datos")
        
        if st.session_state.data_loaded:
            st.success("✅ Datos cargados")
        else:
            st.warning("⚠️ Datos no cargados")
        
        if st.button("🔄 Cargar/Actualizar Datos", use_container_width=True):
            with st.spinner("Cargando datos desde APIs..."):
                try:
                    # Limpiar cache y cargar datos frescos
                    cached_load_api_data.clear()
                    prev_data, roed_data, lamp_data = cached_load_api_data()
                    st.session_state.data_loaded = True
                    st.session_state.api_data = (prev_data, roed_data, lamp_data)
                    st.success("✅ ¡Datos cargados exitosamente!")
                    # Si había configuración establecida, resetear para que recalcule las fechas
                    if st.session_state.config_set:
                        st.session_state.config_set = False
                        st.info("🔄 Reconfigure los parámetros con los datos actualizados.")
                except Exception as e:
                    st.error(f"❌ Error cargando datos: {str(e)}")
                    st.session_state.data_loaded = False
    
    # Área de contenido principal
    # PASO 2: Cargar datos automáticamente en la primera ejecución
    if not st.session_state.data_loaded:
            st.subheader("📊 Carga de Datos")
            st.info("👈 Primero necesitas cargar los datos. Usa el botón 'Cargar/Actualizar Datos' en la barra lateral.")
            
            with st.spinner("Cargando datos iniciales..."):
                try:
                    prev_data, roed_data, lamp_data = cached_load_api_data()
                    st.session_state.data_loaded = True
                    st.session_state.api_data = (prev_data, roed_data, lamp_data)
                    st.success("✅ ¡Datos iniciales cargados exitosamente!")
                    st.rerun()
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
    
    # PASO 3: Mostrar configuración y resumen de datos
    elif not st.session_state.config_set:
            st.subheader("⚙️ Configuración del Reporte")
            st.info("👈 Configura los parámetros del reporte en la barra lateral y luego haz clic en 'Establecer Configuración'.")
            
            # Mostrar instrucciones
            st.markdown("""
            **Pasos para generar tu reporte:**
            
            1. **Selecciona la Sede** hospitalaria (Medellín o Rionegro)
            2. **Elige el Rango de Fechas** para el análisis
            3. **Sube una Plantilla Word** personalizada (opcional)
            4. **Haz clic en 'Establecer Configuración'** para confirmar
            """)
    
    # PASO 4: Mostrar resumen de datos y permitir generar reporte
    elif st.session_state.config_set:
        st.subheader("📊 Resumen de Datos")
        
        try:
            prev_data, roed_data, lamp_data = st.session_state.api_data
            selected_location = st.session_state.selected_location
            start_date, end_date = st.session_state.date_range
            
            # Determinar ubicación para procesamiento (solo una sede)
            locations_to_process = [selected_location]
            
            # Mostrar resumen de datos
            summary = get_data_summary(prev_data, roed_data, lamp_data, locations_to_process)
            
            for location, stats in summary.items():
                st.markdown(f"**📍 {location}**")
                col_a, col_b, col_c, col_d = st.columns(4)
                with col_a:
                    st.metric("🛡️ Preventivos", stats['preventivos_records'])
                with col_b:
                    st.metric("🐭 Roedores", stats['roedores_records'])
                with col_c:
                    st.metric("💡 Lámparas", stats['lamparas_records'])
                with col_d:
                    st.metric("📊 Total", stats['total_records'])
                
                if 'date_range' in stats:
                    st.caption(f"📅 Rango de fechas en datos: {stats['date_range']}")
                st.caption(f"📅 Rango de análisis: {start_date} a {end_date}")
                st.markdown("---")
            
            # Sección de generación de reportes
            st.subheader("📈 Generación de Reportes")
            
            # Botón de generación de reporte
            if st.button("🚀 Generar Reporte", use_container_width=True, type="primary"):
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
                    if st.session_state.template_file is not None:
                        # Guardar plantilla subida temporalmente
                        with open('temp_template.docx', 'wb') as f:
                            f.write(st.session_state.template_file.getvalue())
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
                        '<div class="success-message">✅ <strong>¡Reporte generado exitosamente!</strong> Usa el botón de descarga abajo para guardar el archivo.</div>',
                        unsafe_allow_html=True
                    )
                    
                    # Limpiar plantilla temporal si se usó
                    if st.session_state.template_file is not None:
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
        
        except Exception as e:
            st.error(f"❌ Error generando resumen de datos: {str(e)}")
            with st.expander("🔍 Detalles del Error"):
                st.code(traceback.format_exc())
    
    # Sección de descarga - aparece debajo del contenido principal
    st.markdown("---")
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
        st.info(f"**📄 Archivo:** {st.session_state.report_filename}")
        
        # Mostrar configuración usada
        if st.session_state.config_set:
            with st.expander("� Configuración Usada"):
                st.write(f"🏢 **Sede:** {st.session_state.selected_location}")
                st.write(f"📅 **Fechas:** {st.session_state.date_range[0]} a {st.session_state.date_range[1]}")
                if st.session_state.template_file:
                    st.write(f"📄 **Plantilla:** {st.session_state.template_file.name}")
                else:
                    st.write(f"📄 **Plantilla:** Plantilla por defecto")
        
        # Botón de reinicio para nuevo reporte
        if st.button("🔄 Generar Nuevo Reporte", use_container_width=True):
            st.session_state.report_generated = False
            st.session_state.report_buffer = None
            st.session_state.report_filename = None
            st.session_state.config_set = False
            st.rerun()
    
    else:
        if not st.session_state.data_loaded:
            st.info("📊 Carga los datos primero")
        elif not st.session_state.config_set:
            st.info("⚙️ Establece la configuración")
        else:
            st.info("🚀 Genera un reporte para habilitar la descarga")


if __name__ == "__main__":
    main()