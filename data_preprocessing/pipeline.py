from typing import Tuple
import pandas as pd
import config as cfg

from .date_utils import agregar_nueva_fecha, columna_mes
from .general_utils import (agregar_ceros_a_columnas,
                            crear_columna_combinada,
                            otros_a_dummy,
                            agregar_cantidades_otras)
from .lamp_utils import agregar_columna_lampara, ordenar_columnas_lamparas
from .prev_utils import ordenar_columnas_prev, agregar_area, renombrar_subareas, agregar_subarea
from .roed_utils import agregar_columna_num_estacion, ordenar_columnas_roedores, unir_columna_consumido


def leer_data(API_URL: str) -> pd.DataFrame:
    """
    Lee los datos desde la URL de la API proporcionada y devuelve un DataFrame de pandas.

    Args:
        API_URL (str): La URL de la API desde donde se leerán los datos.

    Returns:
        pd.DataFrame: Un DataFrame que contiene los datos leídos desde la API.
    """
    data = pd.read_csv(API_URL, sep=";", low_memory=False)
    return data


def agregar_acompanante(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renombrar la columna 'Servicio verificado por' a 'Acompañante'.

    Args:
        df (pd.DataFrame): El DataFrame original.

    Returns:
        pd.DataFrame: El DataFrame con la columna renombrada.
    """
    if 'Servicio verificado por' in df.columns:
        df.rename(columns={'Servicio verificado por': 'Acompañante'}, inplace=True)
    return df


def agregar_observaciones(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renombrar la columna 'OBSERVACIONES' a 'Observaciones'.

    Args:
        df (pd.DataFrame): El DataFrame original.

    Returns:
        pd.DataFrame: El DataFrame con la columna renombrada.
    """
    if 'OBSERVACIONES' in df.columns:
        df.rename(columns={'OBSERVACIONES': 'Observaciones'}, inplace=True)
        df.loc[:, 'Observaciones'] = df['Observaciones'].fillna('Sin observaciones')
    return df


def renombrar_id(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renombrar la columna 'ID' a 'Código'.

    Args:
        df (pd.DataFrame): El DataFrame original.

    Returns:
        pd.DataFrame: El DataFrame con la columna renombrada.
    """
    if '_index' in df.columns:
        df.rename(columns={'_index': 'ID'}, inplace=True)
    return df












def procesar_preventivos(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:

    """
    Procesa el DataFrame de preventivos para limpieza y transformación.
    """
    # Work with a copy to avoid SettingWithCopyWarning
    df = df.copy()
    # Fecha
    # Agregar columna 'Fecha pandas'
    df = agregar_nueva_fecha(df, 'Fecha')
    # Agregar columna 'Mes'
    df = columna_mes(df, 'Fecha pandas')
    
    # Location
    # Agregar columna 'Área'
    df = agregar_area(df)
    # Renombrar columnas de subáreas
    df = renombrar_subareas(df, cfg.subareas_preventivos)
    # Agregar columna 'Subárea'
    df = agregar_subarea(df)
    
    
    # Técnicos
    # agregar ceros a las columnas de técnicos
    df = agregar_ceros_a_columnas(df, r'^Técnicos/')
    # Agregar columna 'Técnicos'
    df = crear_columna_combinada(df= df,
                                column_pattern = r'^Técnicos/',
                                new_column_name = 'Técnicos',
                                name_separator = '/',
                                join_separator = ', ',
                                empty_value = '')


    # Plagas
    # agregar dummi de otras cantidades
    df = agregar_cantidades_otras(df = df,
                                  source_column = 'Cuales otras plagase evidenció?',
                                  quantity_column = 'Cantidad de hallazgos de ${Otras_plagas_evidenciadas}',
                                  prefix = 'Cantidad de hallazgos de',
                                  separator = ' ',
                                  drop_source= True,
                                  drop_quantity= True)
    
    # agregar ceros a las columnas de evidencia de plagas
    df = agregar_ceros_a_columnas(df, r'^Cantidad de hallazgos de ')
    # Agregar columna 'Evidencia de plagas'
    df = crear_columna_combinada(df= df,
                                 column_pattern = r'^Cantidad de hallazgos de ',
                                 new_column_name = 'Evidencia de plagas',
                                 name_separator = 'hallazgos de ',
                                 join_separator = ', ',
                                 empty_value = 'Sin evidencia')

    # Plaguicidas
    # crear dummi variables para la columna 'Cuál otro plaguicida fue utilizado?'
    df = otros_a_dummy(df = df,
                       source_column = 'Cuál otro plaguicida fue utilizado?', 
                       prefix = 'Plaguicidas',
                       separator = '/',
                       drop_source= True,
                       drop_columns=['Plaguicidas/Otro:'])
    # agregar ceros a las columnas de plaguicidas
    df = agregar_ceros_a_columnas(df, r'^Plaguicidas/')
    # Agregar plaguicidas utilizados
    df = crear_columna_combinada(df= df,
                                 column_pattern = r'^Plaguicidas/',
                                 new_column_name = 'Plaguicidas utilizados',
                                 name_separator = '/',
                                 join_separator = ' - ',
                                 empty_value = '')
    
    
    # Otras columnas
    # Renombrar columna 'Servicio verificado por' a 'Acompañante'
    df = agregar_acompanante(df)
    # Renombrar columna 'OBSERVACIONES' a 'Observaciones'
    df = agregar_observaciones(df)
    # Renombrar columna 'ID' a 'Código'
    df = renombrar_id(df)

    # ordenar columnas
    df , df_full = ordenar_columnas_prev(df)
    
    return df , df_full





def procesar_lamparas(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    # Work with a copy to avoid SettingWithCopyWarning
    df = df.copy()
    # Fecha
    # Agregar columna 'Fecha pandas'
    df = agregar_nueva_fecha(df, 'Fecha')
    # Agregar columna 'Mes'
    df = columna_mes(df, 'Fecha pandas')
        
    # Teronal/Técnicos
    #agregar ceros a todas las columnas que empiezan con 'Técnicos/'
    df = agregar_ceros_a_columnas(df, r'^Técnicos/')
    # Agregar columna 'Técnicos'
    df = crear_columna_combinada(df= df,
                                 column_pattern = r'^Técnicos/',
                                new_column_name = 'Técnicos',
                                name_separator = '/',
                                join_separator = ', ',
                                empty_value = '')

    # Lámpara
    # Agregar columna 'Lámpara'
    df = agregar_columna_lampara(df)
    # agregar ceros a las columnas que empiezan con 'Estado de la lámpara/'
    df = agregar_ceros_a_columnas(df, r'^Estado de la lámpara/')
    # Agregar columna 'Estado de la lámpara'
    df = crear_columna_combinada(df= df,
                                 column_pattern = r'^Estado de la lámpara/',
                                 new_column_name = 'Estado de la lámpara',
                                 name_separator = '/',
                                 join_separator = ' - ',
                                 empty_value = '')


       

    # Especies encontradas
    # agregar ceros a las columnas que empiezan con 'Cantidad de'
    df = agregar_ceros_a_columnas(df, r'^Cantidad de ')
    # agregar dummi de otras cantidades
    df = agregar_cantidades_otras(df = df,
                                  source_column = 'Cual otra especie encontró?',
                                  quantity_column = 'Cantidad de ${Otra_especie_encontrada}',
                                  prefix = 'Cantidad de',
                                  separator = ' ',
                                  drop_source= True,
                                  drop_quantity= True)
    # Agregar columna 'Especies encontradas'
    df = crear_columna_combinada(df= df,
                                 column_pattern = r'^Especies encontradas/',
                                new_column_name = 'Especies encontradas',
                                name_separator = '/',
                                join_separator = ', ',
                                empty_value = 'Sin evidencia')

    # Otras columnas
    # Renombrar columna 'ID' a 'Código'
    df = renombrar_id(df)
    # Renombrar columna 'Observaciones' a 'Observaciones'
    df = agregar_observaciones(df)
    

    # ordenar columnas
    df , df_full = ordenar_columnas_lamparas(df)

    return df , df_full






def procesar_roedores(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    # Work with a copy to avoid SettingWithCopyWarning
    df = df.copy()
    # Fecha
    # Agregar columna 'Fecha pandas'
    df = agregar_nueva_fecha(df, 'Fecha')
    # Agregar columna 'Mes'
    df = columna_mes(df, 'Fecha pandas')
        
    # Técnicos
    #agregar ceros a todas las columnas que empiezan con 'Técnicos/'
    df = agregar_ceros_a_columnas(df, r'^Técnicos/')
    # Agregar columna 'Técnicos'
    df = crear_columna_combinada(df= df,
                                 column_pattern = r'^Técnicos/',
                                new_column_name = 'Técnicos',
                                name_separator = '/',
                                join_separator = ', ',
                                empty_value = '')

    # Estación
    # Agregar columna 'Número de estación'
    df = agregar_columna_num_estacion(df)
    # agregar ceros a las columnas que empiezan con 'Estado de la estación/'
    df = agregar_ceros_a_columnas(df, r'^Estado de la estación/')
    # Unir las columnas 'Estado de la estación/Consumido' y 'Estado de la estación/Cambio de cebo por consumo'
    df = unir_columna_consumido(df)
    # Agregar columna 'Estado de la estación'
    df = crear_columna_combinada(df= df,
                                 column_pattern = r'^Estado de la estación/',
                                 new_column_name = 'Estado de la estación',
                                 name_separator = '/',
                                 join_separator = ' - ',
                                 empty_value = '')

       

    # Plaguicidas
    # crear dummi variables para la columna 'Cual otro plaguicida aplicó?'
    df = otros_a_dummy(df = df,
                       source_column = 'Cual otro plaguicida aplicó?', 
                       prefix = 'Plaguicida',
                       separator = '/',
                       drop_source= True,
                       drop_columns=['Plaguicida/Otro'])
    # agregar ceros a las columnas de plaguicidas
    df = agregar_ceros_a_columnas(df, r'^Plaguicida/')
    # Agregar plaguicidas utilizados
    df = crear_columna_combinada(df= df,
                                 column_pattern = r'^Plaguicida/',
                                 new_column_name = 'Plaguicidas utilizados',
                                 name_separator = '/',
                                 join_separator = ' - ',
                                 empty_value = '')

    # Otras columnas
    # Renombrar columna 'ID' a 'Código'
    df = renombrar_id(df)
    # Renombrar columna 'Observaciones' a 'Observaciones'
    df = agregar_observaciones(df)
    

    # ordenar columnas
    df , df_full = ordenar_columnas_roedores(df)

    return df , df_full