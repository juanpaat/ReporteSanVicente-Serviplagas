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
    page_title="Generador de Reportes de Control de Plagas Hospitalario",
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
        
        # Selector de ubicación
        st.subheader("🏢 Selección de Ubicación")
        location_options = ["Medellín", "Rionegro", "Ambas Ubicaciones"]
        selected_location = st.selectbox(
            "Seleccionar ubicación hospitalaria:",
            options=location_options,
            index=2,  # Por defecto "Ambas Ubicaciones"
            help="Elegir qué ubicación(es) hospitalaria(s) incluir en el reporte"
        )
        
        # Exclusión de mes
        st.subheader("📅 Filtrado de Datos")
        exclude_month = st.text_input(
            "Mes a excluir (formato: 'Oct 2025'):",
            value="Oct 2025",
            help="Ingresar el mes a excluir del análisis en formato 'Mon YYYY'"
        )
        
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
                
                # Determinar ubicaciones para procesamiento
                if selected_location == "Ambas Ubicaciones":
                    locations_to_process = ["Medellín", "Rionegro"]
                else:
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
            
            # Determinar ubicaciones para procesamiento
            if selected_location == "Ambas Ubicaciones":
                locations_to_process = ["Medellín", "Rionegro"]
                filename_location = "Ambas_Ubicaciones"
            else:
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
                    mes_excluir=exclude_month,
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
            
            1. **Seleccionar Ubicación**: Elegir qué ubicación(es) hospitalaria(s) incluir
            2. **Configurar Filtros**: Especificar qué mes excluir del análisis
            3. **Cargar Datos**: Hacer clic en 'Cargar/Actualizar Datos' para obtener la información más reciente
            4. **Generar Reporte**: Hacer clic en 'Generar Reporte' para crear el documento Word
            5. **Descargar**: Usar el botón de descarga para guardar el reporte
            
            **Consejos:**
            - La aplicación carga datos automáticamente al abrirse por primera vez
            - Usar 'Ambas Ubicaciones' para incluir datos de ambos hospitales
            - Los reportes incluyen visualizaciones y tablas detalladas
            - Los archivos generados se nombran con ubicación y marca de tiempo
            """)
        
        with st.expander("Solución de Problemas"):
            st.markdown("""
            **Problemas comunes:**
            
            - **Falla la carga de datos**: Verificar conexión a internet y endpoints de API
            - **Falla la generación de reporte**: Asegurar que la plantilla Word sea válida
            - **La descarga no funciona**: Intentar generar el reporte nuevamente
            
            **Formato de datos para exclusión de mes:**
            - Usar formato como 'Oct 2025', 'Jan 2024', etc.
            - Los nombres de mes deben ser abreviaciones de 3 letras
            """)


if __name__ == "__main__":
    main()