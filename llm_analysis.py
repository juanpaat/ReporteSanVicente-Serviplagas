"""
Modulo de analisis LLM para generacion de reportes de control de plagas.
Utiliza la API de OpenAI para generar analisis de zonas comunes.
"""

import os
import logging
import pandas as pd
from openai import OpenAI
from config import meses_esp

logger = logging.getLogger(__name__)


def get_openai_api_key() -> str:
    """
    Obtener la API key de OpenAI desde variables de entorno o Streamlit secrets.

    Prioridad:
        1. Variable de entorno OPENAI_API_KEY (.env para desarrollo local)
        2. Streamlit secrets (para despliegue en la nube)

    Returns:
        str: La API key de OpenAI

    Raises:
        ValueError: Si no se encuentra la API key en ninguna fuente
    """
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        try:
            import streamlit as st
            if hasattr(st, 'secrets'):
                api_key = st.secrets.get("OPENAI_API_KEY")
        except (ImportError, AttributeError):
            pass

    if not api_key:
        raise ValueError(
            "No se encontro la API key de OpenAI. "
            "Para desarrollo local: agrega OPENAI_API_KEY en tu archivo .env. "
            "Para Streamlit Cloud: agrega OPENAI_API_KEY en el secrets manager."
        )

    return api_key


def filtrar_ultimo_mes(df) -> tuple:
    """
    Filtra el DataFrame para quedarse solo con los datos del ultimo mes.
    Usa la misma logica que las funciones de visualizacion (latest_month_spanish).

    Args:
        df: DataFrame con columna 'Mes' en formato 'Dic 2025'

    Returns:
        tuple: (DataFrame filtrado, str nombre del mes en espanol ej 'Dic 2025')
    """
    if df is None or len(df) == 0 or 'Mes' not in df.columns:
        return df, "No disponible"

    df = df.copy()
    meses_eng = {v: k for k, v in meses_esp.items()}

    def spanish_month_to_datetime(mes_str):
        if not isinstance(mes_str, str):
            return pd.NaT
        for spanish, english in meses_eng.items():
            if spanish in mes_str:
                english_mes = mes_str.replace(spanish, english)
                return pd.to_datetime(english_mes, format='%b %Y')
        return pd.NaT

    df['Mes_dt'] = df['Mes'].apply(spanish_month_to_datetime)

    if df['Mes_dt'].isna().all():
        logger.warning("No se encontraron fechas validas en la columna 'Mes'")
        return df.drop(columns=['Mes_dt']), "No disponible"

    latest_month = df.loc[df['Mes_dt'].notna(), 'Mes_dt'].max()
    latest_month_spanish = df.loc[df['Mes_dt'] == latest_month, 'Mes'].iloc[0]

    filtered = df[df['Mes'] == latest_month_spanish].copy()
    filtered = filtered.drop(columns=['Mes_dt'])

    return filtered, latest_month_spanish


def generar_analisis_zonas_comunes(df_zonas_comunes, sede, mes_analisis) -> str:
    """
    Genera un analisis de zonas comunes usando OpenAI.
    Filtra los datos al ultimo mes antes de enviarlos al LLM.

    Args:
        df_zonas_comunes: DataFrame procesado de zonas comunes (filtrado por sede)
        sede: Nombre de la sede ('Medellin' o 'Rionegro')
        mes_analisis: Mes del analisis (ej: 'Dic 2025')

    Returns:
        str: Texto del analisis generado por el LLM
    """
    api_key = get_openai_api_key()
    client = OpenAI(api_key=api_key)

    # Filtrar al ultimo mes (misma logica que los graficos)
    df_ultimo_mes, mes_nombre = filtrar_ultimo_mes(df_zonas_comunes)
    if mes_nombre != "No disponible":
        mes_analisis = mes_nombre

    # Formatear los datos del DataFrame como texto para el prompt
    if df_ultimo_mes is None or len(df_ultimo_mes) == 0:
        datos_texto = "No se encontraron datos de zonas comunes para el periodo seleccionado."
    else:
        datos_texto = df_ultimo_mes.to_string(index=False)

    # --- SYSTEM MESSAGE ---
    system_message = (
        "Eres un ingeniero sanitario experto en control integrado de plagas en entornos hospitalarios "
        "en Colombia. Redactas la seccion de zonas comunes del informe tecnico mensual de control de "
        "plagas para la Fundacion Hospitalaria San Vicente.\n\n"
        "ESTRUCTURA OBLIGATORIA del analisis:\n"
        "1. Un parrafo introductorio que indique que se realiza el control integrado de plagas en todas "
        "las instalaciones del hospital en zonas comunes, mencionando los metodos usados (nebulizacion, "
        "aspersion, control larvicida, cebado) y las areas controladas (superficies, cajas residuales, "
        "alcantarillas, patios, arboles, paredes, carcamos, zanjas, sotanos, perimetro comun).\n"
        "2. Luego, secciones separadas por tipo de plaga encontrada. Cada seccion debe tener un "
        "encabezado en MAYUSCULAS con el nombre de la plaga seguido de dos puntos (ej: ROEDORES:, "
        "VOLADORES:, CUCARACHA AMERICANA:, HORMIGAS:, HORMIGUEROS:, DESNIDE:, etc.).\n"
        "3. Dentro de cada seccion, incluir: hallazgos especificos (cantidades, especies, ubicaciones "
        "exactas), fechas de los controles, metodos de control aplicados, y conclusion del estado.\n"
        "4. Si un tipo de plaga no aparece en los datos, NO incluyas su seccion.\n"
        "5. Escribe solo las secciones para las cuales hay evidencia en los datos.\n\n"
        "FORMATO:\n"
        "- No uses formato markdown, asteriscos ni negritas.\n"
        "- Escribe en parrafos corridos dentro de cada seccion.\n"
        "- Los encabezados de seccion van en MAYUSCULAS seguidos de dos puntos y salto de linea.\n"
        "- Redacta de manera formal, tecnica y en espanol.\n"
        "- Usa las fechas exactas que aparecen en los datos.\n"
        "- Menciona cantidades, especies y ubicaciones especificas tal como aparecen en los datos."
    )

    # --- USER PROMPT ---
    user_prompt = (
        f"Genera el analisis de zonas comunes para la sede {sede} correspondiente al periodo "
        f"{mes_analisis}.\n\n"
        f"Datos de inspecciones de zonas comunes (ultimo mes):\n"
        f"{datos_texto}\n\n"
        f"Redacta el analisis siguiendo la estructura indicada: parrafo introductorio y luego "
        f"secciones por tipo de plaga en MAYUSCULAS."
    )

    # --- EXAMPLE (few-shot) ---
    example_user = (
        "Genera el analisis de zonas comunes para la sede Medellin correspondiente al periodo "
        "Dic 2025.\n\n"
        "Datos de inspecciones de zonas comunes (ultimo mes):\n"
        "     Fecha      Mes       Sede      Tecnicos                  Evidencia de plagas    Que especie                         Cantidad  Ubicacion exacta\n"
        "2025-Dic-02  Dic 2025  Medellin  Tecnico A, Tecnico B      Roedores               Norvegicus                           9         Oficina, techos, compostaje, parqueadero bloque 11\n"
        "2025-Dic-05  Dic 2025  Medellin  Tecnico A                 Hormigas               Fantasma, Dulcera                    0         Zona verde, bloque 8, bloque 5, bloque 11 y 12\n"
        "2025-Dic-10  Dic 2025  Medellin  Tecnico B                 Palomas                Paloma muerta                        4         Bloque 7, bloque 8, bloque 17\n"
        "2025-Dic-11  Dic 2025  Medellin  Tecnico A                 Hormigas               Mandibula                            0         Hormigueros frente bloque 18 y 16\n"
        "2025-Dic-15  Dic 2025  Medellin  Tecnico A, Tecnico B      Voladores              Mosquitos fruteros, Culex, Aedes     0         Zonas verdes, bloques 5, 7, compostaje\n"
        "2025-Dic-16  Dic 2025  Medellin  Tecnico A                 Roedores               Norvegicus viva                      2         Rehabilitacion, oficina Serviplagas\n"
        "2025-Dic-22  Dic 2025  Medellin  Tecnico B                 Roedores               Norvegicus muerta                    4         Compostaje, parqueadero bloque 11, oficina, techos\n"
        "2025-Dic-28  Dic 2025  Medellin  Tecnico A                 Cucarachas             Americana                           18         Manholes zona externa bloques 12 y 13\n"
        "2025-Dic-28  Dic 2025  Medellin  Tecnico A                 Voladores              Culex pipiens, Calliphoridae          0         Bloques 5, compostaje, 7, 5 techos\n"
        "2025-Dic-29  Dic 2025  Medellin  Tecnico B                 Sin evidencia                                                         \n\n"
        "Redacta el analisis siguiendo la estructura indicada: parrafo introductorio y luego "
        "secciones por tipo de plaga en MAYUSCULAS."
    )

    example_response = (
        "Se realiza el control integrado de plaga dentro de todas las instalaciones del hospital "
        "San Vicente de Paul Medellin en zonas comunes con el objetivo de prevenir y controlar la "
        "presencia de plagas que puedan afectar la salud de los pacientes del hospital y el bienestar "
        "del personal y visitantes.\n"
        "Se usa el mecanismo de nebulizacion, la aspersion, el control larvicida y el cebado. Se "
        "controlan todas las areas comunes de la institucion buscando refugio de sujetos plagas en "
        "superficies, cajas residuales, alcantarillas, patios, arboles, paredes, carcamos, zanjas, "
        "sotanos, en todo el perimetro comun.\n"
        "A continuacion, el analisis:\n"
        "ROEDORES:\n"
        "En el mes de diciembre se presenta consumo en cuatro estaciones en las dos visitas # 3, 35, "
        "27 y 44, se mantiene grado de infestacion bajo de acuerdo a las tablas; en recorridos "
        "preventivos y zona comun no se presentan episodios y en correctivos se presenta 1 episodio "
        "con excretas de roedor y 1 episodio con dos roedores atrapados en trampa, uno vivo y otro "
        "muerto. Se dan por aumento de las lluvias en la zona.\n"
        "En total son 11 noruegas, 9 muertas por envenenamiento y 2 vivas (eliminadas). 1 viva en "
        "oficina de Serviplagas, 1 viva en rehabilitacion, 4 muertas oficina, techos, 4 muertas en "
        "compostaje y parqueadero de bloque 11. Fechas de controles 2, 11, 16, 22 y 29 de diciembre.\n"
        "VOLADORES:\n"
        "Durante el mes se realizaron actividades de control de plagas en zonas verdes y parqueaderos "
        "incluyendo la nebulizacion en zonas verdes parqueaderos en toda area posible del hospital "
        "incluyendo el compostaje para controlar la poblacion de insectos voladores y otros artropodos; "
        "se realizo un monitoreo regular para detectar la presencia de plagas y evaluar la efectividad "
        "de las medidas de control. Se eliminan principalmente mosquitos fruteros en zonas verdes "
        "alrededor de los bloques en general debido a las condiciones de recursos en ambiente para "
        "ellos, como flores, arboles, frutas, zonas verdes, etc. Cantidad indeterminada, imposible "
        "contabilizar en vuelo. Se nebuliza para bajar poblaciones, se apoya del control fisico con "
        "lamparas en 34 accesos criticos. Tambien se eliminan zancudos comunes y Aedes aeghipty. Para "
        "este mes reportamos zancudos culex pipiens, quinquefasciatos y oscas calliphordae como las "
        "especies mas vistas, especialmente en los bloques 5, compostaje, 7 facturacion, y 5 techos, "
        "esto debido a las constantes lluvias.\n"
        "CUCARACHA AMERICANA:\n"
        "Durante el control a los manholes, se evidencio cucaracha americana, aproximadamente unas 15 "
        "a 20, una reduccion importante de cucarachas de este tipo en los Manholes de zona externa "
        "entre los bloques 12 y 13, por presentar condiciones ideales para sobrevivir humedad, calidez "
        "y materia organica, los manholes al interior de la institucion se encontraron muy limpios "
        "debido al control constante. Se controlaron en su totalidad por el metodo de nebulizacion. "
        "Fecha del control 28 de diciembre.\n"
        "HORMIGAS:\n"
        "Se evidencia y controlan hormigas, especies detectadas este mes: hormiga fantasma o dulcera, "
        "alrededor de la zona verde, imposible cuantificar; en pisos y paredes del bloque 8, trabajo "
        "social bloque 5 y atencion al usuario bloque 11 y 12 y en hormigueros activos buscando "
        "alimentos. Visitas a estas zonas el 5 el 11 y el 18 de diciembre.\n"
        "HORMIGUEROS:\n"
        "Se evidencia y aplica plaguicida en 2 hormigueros, 2 de mandibula. Ubicados al frente del "
        "bloque 18 y 16. Visitas a estas zonas el 17 y 28 de diciembre.\n"
        "DESNIDE:\n"
        "Durante el mes de diciembre se identifican 4 palomas muertas por inanicion o por depredador, "
        "2 de ellas en el bloque 7, 1 en el bloque 8 y la otra en el bloque 17. No se hallan nidos "
        "con huevos o pichones, se tumban 3 nidos en bloque 17. Fecha del Desnide 10, 18 y 28 de "
        "diciembre."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": example_user},
                {"role": "assistant", "content": example_response},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=2000,
        )

        resultado = response.choices[0].message.content.strip()
        logger.info(f"Analisis LLM generado exitosamente ({len(resultado)} caracteres)")
        return resultado

    except Exception as e:
        logger.error(f"Error generando analisis LLM: {e}")
        return f"No se pudo generar el analisis automatico de zonas comunes: {e}"
