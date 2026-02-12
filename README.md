# 🏥 Sistema de Reportes de Control de Plagas - San Vicente Fundación

Sistema automatizado para generar reportes de control de plagas en hospitales (Medellín y Rionegro). Incluye aplicación web interactiva con dos funcionalidades principales: generación de reportes Word (con análisis LLM) y exportación de datos Excel.

## 🎯 Funcionalidades Principales

### 📈 Generación de Reportes Word
- **Interfaz interactiva**: Aplicación web fácil de usar
- **Datos en tiempo real**: Carga de 5 APIs con cache automático
- **Reportes flexibles**: Generar por sede individual
- **Filtros de fecha**: Selección de rangos personalizados
- **Análisis LLM**: Generación automática del análisis de zonas comunes con OpenAI
- **Seguimiento visual**: Barras de progreso durante generación
- **Descarga directa**: Documentos Word listos para usar
- **Manejo de errores**: Reportes de error detallados

### 📊 Exportación de Datos Excel
- **Filtros independientes**: Rangos de fechas separados del reporte
- **Procesamiento completo**: Datos de preventivos, roedores, lámparas, correctivos y zonas comunes
- **Filtrado por sede**: Datos separados automáticamente por Medellín y Rionegro
- **Múltiples formatos**: 10 descargas individuales + archivo combinado
- **Formato Excel**: Compatible con todas las versiones (.xlsx)
- **Previsualización organizada**: Ver datos por tipo y sede antes de descargar

### 🔧 Interfaz de Línea de Comandos
- **Procesamiento automatizado**: Ejecución por scripts
- **Procesamiento por lotes**: Múltiples reportes
- **Ejecución programada**: Integración con cron jobs

## 🛠️ Inicio Rápido

### 1. Instalación
```bash
# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configuración

#### Desarrollo Local
Crea un archivo `.env` con tus endpoints de API y credenciales:
```env
prev_API=https://tu-endpoint/preventivos
roe_API=https://tu-endpoint/roedores
lam_API=https://tu-endpoint/lamparas
cor_API=https://tu-endpoint/correctivos
zcomun_API=https://tu-endpoint/zonas-comunes
OPENAI_API_KEY=sk-tu-api-key-aqui
```

#### Despliegue en Streamlit Cloud
1. **Subir a GitHub**: Sube tu código a un repositorio
2. **Desplegar en Streamlit Cloud**:
   - Ve a [share.streamlit.io](https://share.streamlit.io)
   - Conecta tu repositorio de GitHub
   - Despliega usando `app.py` como archivo principal
3. **Configurar Secretos**: En los ajustes de tu app, agrega en "Secrets management":
   ```toml
   prev_API = "https://tu-endpoint/preventivos"
   roe_API = "https://tu-endpoint/roedores"
   lam_API = "https://tu-endpoint/lamparas"
   cor_API = "https://tu-endpoint/correctivos"
   zcomun_API = "https://tu-endpoint/zonas-comunes"
   OPENAI_API_KEY = "sk-tu-api-key-aqui"
   ```

**Nota**: Nunca subas el archivo `.env` al repositorio.

### 3. Uso

**Aplicación Web (Recomendado):**
```bash
streamlit run app.py
# Luego abre http://localhost:8501
```

**Línea de Comandos:**
```bash
python main.py
```

## 📁 Estructura del Proyecto

```
ReporteSanVicente-Serviplagas/
├── app.py                     # Aplicación web Streamlit
├── main.py                    # Script de línea de comandos
├── report_generator.py        # Generación de reportes
├── llm_analysis.py            # Análisis de zonas comunes con OpenAI
├── config.py                  # Configuración y constantes
├── Plantilla.docx             # Plantilla Word
├── .env                       # Endpoints API y credenciales (crear este archivo)
│
├── data_preprocessing/        # Módulos de procesamiento de datos
├── data_visualization/        # Generación de gráficos
└── Engine/                    # Motor de generación de documentos Word
```

## 🎯 Procesamiento de Datos

### Tipos de Datos Soportados
- **Preventivos**: Tratamientos preventivos, evidencia de plagas, uso de plaguicidas
- **Roedores**: Estaciones de roedores, consumo de cebo, tendencias de eliminación
- **Lámparas**: Trampas de luz, captura de especies, monitoreo de estado
- **Correctivos**: Órdenes de mantenimiento, eliminación de plagas, niveles de infestación
- **Zonas Comunes**: Inspecciones de áreas comunes, evidencia de plagas por tipo y ubicación

### Características del Procesamiento
- Integración con 5 APIs de KoBoToolbox
- Filtrado por ubicación (Medellín/Rionegro)
- Gestión de fechas y filtros temporales
- Validación de datos y manejo de errores
- Soporte UTF-8 para caracteres en español

## 🤖 Análisis LLM (Zonas Comunes)

El sistema genera automáticamente el análisis técnico de zonas comunes usando la API de OpenAI:

- **Filtrado por último mes**: Solo se envían al LLM los datos del mes más reciente (misma lógica que los gráficos)
- **Estructura del análisis**: Párrafo introductorio + secciones por tipo de plaga (ROEDORES, VOLADORES, CUCARACHAS, HORMIGAS, etc.)
- **Few-shot prompting**: Incluye un ejemplo de entrada y salida para guiar la generación
- **Integración en reporte**: El texto generado se inserta en el marcador `{{zonas_comunes}}` de la plantilla Word

## 🎮 Uso de la Aplicación Web

### Tab 1: 📈 Generación de Reportes
1. **Seleccionar Sede**: Medellín o Rionegro
2. **Elegir Fechas**: Rango para el análisis
3. **Establecer Configuración**: Confirmar parámetros (usa plantilla por defecto)
4. **Generar Reporte**: Crear documento Word profesional (incluye análisis LLM de zonas comunes)
5. **Descargar**: Archivo Word con gráficos, tablas y análisis

### Tab 2: 📊 Exportar Datos
1. **Seleccionar Fechas**: Rango independiente del reporte
2. **Cargar y Procesar**: Obtener y procesar datos de las 5 APIs
3. **Ver Métricas**: Cantidad de registros por tipo y sede
4. **Descargar Excel**:
   - Individual: 10 opciones (5 tipos × 2 sedes)
     - Preventivos Medellín/Rionegro
     - Roedores Medellín/Rionegro
     - Lámparas Medellín/Rionegro
     - Correctivos Medellín/Rionegro
     - Zonas Comunes Medellín/Rionegro
   - Combinado: Archivo con hasta 10 hojas Excel
5. **Previsualizar**: Ver muestra de datos organizados por sede y tipo

## 📊 Visualizaciones y Reportes

### Gráficos Generados
- **Tratamientos Preventivos**: Gráficos de área, series temporales, análisis de tendencias, niveles de infestación
- **Control de Roedores**: Estado de estaciones, tendencias de eliminación
- **Trampas de Luz**: Monitoreo de estado, análisis de captura de especies, tendencias de capturas
- **Correctivos**: Comparación de órdenes, tendencias de eliminación, niveles de infestación, plagas por especie

### Características de los Gráficos
- Alta resolución (300 DPI)
- Estilo profesional con colores consistentes
- Etiquetas en español
- Formato automático de números

### Características de Documentos Word
- Diseño profesional con gráficos y tablas embebidas
- Tablas nativas de Word con formato apropiado
- Análisis de zonas comunes generado por LLM
- Generación en memoria para descargas web
- Reemplazo automático de variables de plantilla

## 🔧 Dependencias Principales

- `pandas==2.3.2` - Manipulación de datos
- `matplotlib==3.10.6` - Visualizaciones
- `seaborn==0.13.2` - Gráficos estadísticos
- `streamlit>=1.28.0` - Aplicación web
- `docxtpl==0.20.1` - Plantillas Word
- `python-docx==1.2.0` - Manipulación de documentos
- `requests>=2.31.0` - Comunicación API
- `xlsxwriter>=3.0.0` - Exportación Excel
- `python-dotenv==1.1.1` - Variables de entorno
- `openai>=1.0.0` - Análisis LLM con OpenAI

## 🆘 Solución de Problemas

### Problemas Comunes

**Conexión API Falló**
- Verificar que `.env` contenga URLs correctas para las 5 APIs
- Revisar conexión a internet
- Confirmar disponibilidad del servidor API

**Error en Análisis LLM**
- Verificar que `OPENAI_API_KEY` esté configurada en `.env` o Streamlit secrets
- Confirmar que la API key sea válida y tenga créditos disponibles
- El reporte se genera igualmente con un mensaje de error en la sección de zonas comunes

**Errores de Plantilla**
- Asegurar que `Plantilla.docx` existe en la raíz del proyecto
- Verificar que todos los marcadores requeridos estén presentes (incluyendo `{{zonas_comunes}}`)
- Revisar permisos de archivo

**Problemas de Memoria**
- Procesar una ubicación a la vez para datasets grandes
- Cerrar aplicaciones innecesarias
- Considerar aumentar memoria del sistema

### Mensajes de Error Comunes

**"Error loading API data"**
- Revisar endpoints API y conectividad de red
- Verificar formato de respuesta API

**"Error generating report"**
- Validar integridad de plantilla Word
- Revisar detalles de error en logs de aplicación

**"Error procesando datos"**
- Verificar que los datos tengan el formato esperado
- Revisar rango de fechas seleccionado

**"No se encontro la API key de OpenAI"**
- Agregar `OPENAI_API_KEY` en `.env` (local) o Streamlit secrets (nube)

## 💡 Consejos de Uso

### Para Mejores Resultados
1. **Rangos de Fechas**: Usar rangos de hasta 3 meses para mejor rendimiento
2. **Conexión Internet**: Asegurar conexión estable antes de procesar
3. **Navegador**: Usar Chrome o Firefox para mejor compatibilidad
4. **Descargas**: Los archivos se guardan en la carpeta de descargas del navegador

### Flujo de Trabajo Recomendado
1. **Primero**: Usar tab "Exportar Datos" para revisar datos disponibles por sede
2. **Segundo**: Generar reportes Word con datos confirmados para una sede específica
3. **Análisis**: Usar archivos Excel individuales por tipo y sede para análisis detallados
4. **Comparación**: Usar archivo combinado para análisis comparativos entre sedes
5. **Presentación**: Usar reportes Word para presentaciones formales

## 🚀 Desarrollo

### Agregar Nuevas Visualizaciones
1. Crear función en módulo `data_visualization/` apropiado
2. Agregar llamada a función en `report_generator.py`
3. Actualizar plantilla Word con nuevos marcadores

### Modificar Procesamiento de Datos
1. Actualizar funciones en módulos `data_preprocessing/`
2. Probar con interfaces web y CLI
3. Verificar compatibilidad de salida

### Modificar Análisis LLM
1. Editar prompts y ejemplo en `llm_analysis.py`
2. Ajustar `system_message`, `user_prompt` o `example_response` según necesidades
3. Probar con datos reales para validar calidad del análisis

## 📄 Información del Sistema

**Software propietario para reportes de control de plagas hospitalario de Serviplagas**

### Estado Actual
- ✅ **Aplicación Web**: Completamente funcional
- ✅ **Generación de Reportes**: Documentos Word profesionales por sede
- ✅ **Análisis LLM**: Zonas comunes con OpenAI (gpt-4o-mini)
- ✅ **Exportación de Datos**: Archivos Excel individuales y combinados
- ✅ **Procesamiento Completo**: 5 tipos de datos (preventivos, roedores, lámparas, correctivos, zonas comunes)
- ✅ **Filtrado por Sede**: Separación automática Medellín/Rionegro
- ✅ **Filtros de Fecha**: Independientes y flexibles
- ✅ **Interfaz de Usuario**: Intuitiva y fácil de usar

---

**🏥 Sistema de Reportes de Control de Plagas San Vicente Fundación**

*Generación automatizada de informes profesionales y exportación de datos para servicios de control de plagas en hospitales*
