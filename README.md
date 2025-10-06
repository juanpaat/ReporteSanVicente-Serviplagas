# Sistema de Automatización de Informes Serviplagas

## 📋 Descripción General

Este sistema automatiza la generación de informes mensuales para Serviplagas, procesando datos de tres tipos de servicios: **Preventivos**, **Roedores** y **Lámparas** para las sedes de **Medellín** y **Rionegro**. El sistema lee datos desde APIs, los procesa, genera visualizaciones y produce informes automáticos en formato Word.

## 🏗️ Estructura del Proyecto

```
Automation/
├── main.py                     # Archivo principal de ejecución
├── config.py                   # Configuración de meses en español
├── requirements.txt            # Dependencias del proyecto
├── test_template.docx          # Plantilla Word para informes
├── .env                        # Variables de entorno (URLs APIs)
├── data_preprocessing/         # Módulos de procesamiento de datos
│   ├── pipeline.py            # Funciones principales de procesamiento
│   ├── general_utils.py       # Utilidades generales
│   ├── date_utils.py          # Utilidades de fechas
│   ├── prev_utils.py          # Utilidades específicas preventivos
│   ├── lamp_utils.py          # Utilidades específicas lámparas
│   └── roed_utils.py          # Utilidades específicas roedores
├── data_visualization/         # Módulos de visualización
│   ├── preventivos.py         # Gráficos de preventivos
│   ├── lamparas.py            # Gráficos de lámparas
│   └── roedores.py            # Gráficos de roedores
└── Engine/
    └── engine.py              # Motor de generación de informes Word
```

## 🚀 Instalación y Configuración

### 1. Requisitos del Sistema
- Python 3.11 o superior
- Sistema operativo: Windows, macOS o Linux

### 2. Instalación de Dependencias

```bash
# Clonar o descargar el proyecto
cd Automation

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configuración de Variables de Entorno

Crear un archivo `.env` en la raíz del proyecto con las URLs de las APIs:

```env
prev_API=https://api.ejemplo.com/preventivos
roe_API=https://api.ejemplo.com/roedores
lam_API=https://api.ejemplo.com/lamparas
```

### 4. Plantilla Word

Asegúrate de tener el archivo `Plantilla.docx` con los marcadores necesarios:
- `{{med_preventivos_1_plot}}`, `{{med_preventivos_1_tabla}}`
- `{{med_roedores_1_plot}}`, `{{med_roedores_1_tabla}}`
- `{{med_lamparas_1_plot}}`, `{{med_lamparas_1_tabla}}`
- Y sus equivalentes para Rionegro (`rio_*`)

## 📊 Funcionalidades Principales

### 1. Procesamiento de Datos

El sistema procesa tres tipos de datos:

#### **Preventivos**
- Limpia y estandariza fechas en español
- Combina información de áreas y subáreas
- Procesa información de técnicos y plaguicidas
- Agrupa evidencia de plagas por cantidad

#### **Roedores**
- Procesa números de estación (Medellín/Rionegro)
- Maneja estados de estaciones y consumo de cebo
- Agrupa plaguicidas utilizados
- Genera estadísticas de eliminación

#### **Lámparas**
- Combina información de lámparas por sede
- Procesa estados de lámparas y tubos
- Registra especies capturadas
- Calcula tendencias de capturas

### 2. Visualizaciones Generadas

#### **Preventivos**
- Gráfico de órdenes por área y mes
- Series temporales de plagas por facetas
- Tendencias totales de plagas

#### **Roedores**
- Estado de estaciones por mes
- Tendencias de eliminación mensual

#### **Lámparas**
- Estado de lámparas por mes
- Capturas de especies por mes
- Tendencias totales de capturas
- Gráficos con leyenda detallada

### 3. Generación de Informes

El sistema utiliza `docxtpl` para generar informes Word profesionales que incluyen:
- Gráficos en alta resolución (300 DPI)
- Tablas nativas de Word con formato profesional
- Datos procesados y filtrados automáticamente
- Separación por sede (Medellín/Rionegro)

## 🔧 Uso del Sistema

### Ejecución Básica

```bash
python main.py
```

### Personalización

#### Cambiar Mes a Excluir
En `main.py`, modifica la variable:
```python
mes_excluir = 'Oct 2025'  # Cambiar según necesidad
```

#### Modificar Nombre del Informe
En `main.py`, cambia la línea final:
```python
informe.generar_informe('NOMBRE_PERSONALIZADO.docx')
```

## 📁 Archivos de Configuración

### `config.py`
Contiene la traducción de meses de inglés a español:
```python
meses_esp = {
    'Jan': 'Ene', 'Feb': 'Feb', 'Mar': 'Mar',
    'Apr': 'Abr', 'May': 'May', 'Jun': 'Jun',
    # ... etc
}
```

### `requirements.txt`
Lista las dependencias necesarias:
- `pandas==2.3.2` - Análisis de datos
- `matplotlib==3.10.6` - Visualizaciones
- `seaborn==0.13.2` - Gráficos estadísticos
- `numpy==2.3.3` - Operaciones numéricas
- `docxtpl==0.20.1` - Plantillas Word
- `python-docx==1.2.0` - Manipulación documentos Word
- `python-dotenv==1.1.1` - Variables de entorno

## 🛠️ Detalles Técnicos

### Procesamiento de Datos

#### Pipeline Principal
1. **Lectura**: Datos CSV desde APIs con separador `;`
2. **Filtrado**: Por sede (Medellín/Rionegro)
3. **Procesamiento**: Limpieza, transformación y estandarización
4. **Exclusión**: Datos del mes actual para evitar datos incompletos

#### Transformaciones Principales
- **Fechas**: Conversión a formato pandas y español
- **Columnas combinadas**: Unión inteligente de múltiples columnas
- **Valores faltantes**: Tratamiento automático con valores por defecto
- **Tipos de datos**: Conversión y validación automática

### Visualizaciones

#### Estilo Visual
- Paleta de colores consistente
- Tamaño de fuente legible
- Rotación automática de etiquetas
- Formato de números con separadores de miles
- Títulos y etiquetas en español

#### Formatos de Salida
- **Resolución**: 300 DPI para impresión profesional
- **Tamaño**: 6.5 pulgadas de ancho estándar
- **Formato**: PNG con fondo transparente
- **Optimización**: Recorte automático de espacios

### Motor de Informes

#### Características
- **Plantillas**: Uso de marcadores `{{variable}}`
- **Tablas nativas**: Integración directa con Word
- **Limpieza automática**: Eliminación de archivos temporales
- **Manejo de errores**: Mensajes descriptivos y fallbacks

#### Estilos de Tabla
- **Predeterminado**: 'Table Grid' (neutral)
- **Fuente**: 6pt para optimizar espacio
- **Formato números**: Separadores de miles automáticos
- **Encabezados**: Texto en negrita

## 🔍 Solución de Problemas

### Errores Comunes

#### 1. Error de conexión API
```
Verificar URLs en archivo .env
Confirmar acceso a internet
Validar permisos de API
```

#### 2. Error en plantilla Word
```
Revisar marcadores {{variable}} en plantilla
Confirmar sintaxis correcta
Verificar existencia del archivo template
```

#### 3. Error de dependencias
```bash
pip install --upgrade -r requirements.txt
```

#### 4. Warnings de pandas
El sistema está optimizado para evitar warnings usando `.loc[]` en todas las asignaciones.

### Logs del Sistema

El sistema genera logs informativos:
- ✅ **Éxito**: Operaciones completadas
- ❌ **Error**: Problemas encontrados
- 🔍 **Debug**: Información de contexto

## 📈 Personalización Avanzada

### Agregar Nuevos Gráficos

1. Crear función en módulo de visualización correspondiente:
```python
def nueva_visualizacion(df: pd.DataFrame) -> tuple[pd.DataFrame, plt.Figure]:
    # Lógica del gráfico
    return resultado_df, figura
```

2. Agregar al main.py:
```python
informe.agregar_resultado_completo(nueva_visualizacion, 
                                 df_datos,
                                 'nuevo_plot',
                                 'nueva_tabla')
```

3. Actualizar plantilla Word con marcadores `{{nuevo_plot}}` y `{{nueva_tabla}}`

### Modificar Procesamiento

Las funciones de procesamiento están modularizadas:
- `general_utils.py`: Funciones reutilizables
- `*_utils.py`: Funciones específicas por tipo de servicio

### Cambiar Estilos

Modificar constantes en módulos de visualización:
- Colores de gráficos
- Tamaños de fuente
- Estilos de tabla Word
- Resolución de imágenes

## 📝 Mantenimiento

### Actualizaciones Periódicas
- Revisar compatibilidad de dependencias
- Actualizar URLs de APIs si cambian
- Verificar formatos de datos de entrada
- Mantener plantillas Word actualizadas

### Respaldos Recomendados
- Archivo `.env` con URLs
- Plantillas Word personalizadas
- Configuraciones específicas del cliente

## 👥 Soporte

Para problemas técnicos:
1. Revisar logs de ejecución
2. Verificar configuración de `.env`
3. Confirmar integridad de datos de entrada
4. Validar plantilla Word y marcadores

---

**Nota**: Este sistema está diseñado para uso interno de Serviplagas y requiere acceso autorizado a las APIs de datos.