import pandas as pd
import config as cfg
from typing import Tuple


def ordenar_columnas_prev(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Ordena las columnas del DataFrame según el orden especificado.

    Args:
        df (pd.DataFrame): El DataFrame original.

    Returns:
        A tuple of two pd.DataFrame: The DataFrame with the main columns ordered, and the DataFrame with all columns ordered.
    """
    columnas_cantidad_de_plagas = [col for col in df.columns if col.startswith('Cantidad de hallazgos de')]
    columnas_plaguicidas = [col for col in df.columns if col.startswith('Plaguicidas/')]   

    # Orden predefinido de columnas principales
    main_columns = ([
        'ID',
        'Fecha',
        'Mes',
        'Sede',
        'Código',
        'Área',
        'Subárea', 
        'Técnicos',
        'Evidencia de plagas']
        + columnas_cantidad_de_plagas
        + ['Plaguicidas utilizados',
        'Acompañante',
        'Observaciones'])

    # Orden predefinido de columnas principales
    all_columns = ([
        'ID',
        'Fecha',
        'Fecha pandas',
        'Mes',
        'Sede',
        'Código',
        'Área',
        'Subárea', 
        'Técnicos',
        'Evidencia de plagas']
        + columnas_cantidad_de_plagas
        + ['Plaguicidas utilizados']
        + columnas_plaguicidas 
        + ['Acompañante',
        'Observaciones'])
    
    return df[main_columns], df[all_columns]


def agregar_area(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agregar una nueva columna 'Área' que combine la información de las columnas relacionadas.

    Args:
        df (pd.DataFrame): El DataFrame original.

    Returns:
        pd.DataFrame: El DataFrame con la nueva columna 'Bloque/Torre'.
    """
    bt_cols = ['Torre o Área', 'Bloque o Área']
    df.loc[:, 'Área'] = df[bt_cols].apply(lambda row: ' '.join(row.dropna().astype(str)), axis=1)
    return df


def renombrar_subareas(df: pd.DataFrame, subareas_columnas: list) -> pd.DataFrame:
    """
    Renombrar las columnas cfg.subareas_preventivos con 'Subarea: ' como prefijo.

    Args:
        df (pd.DataFrame): El DataFrame original.
        subareas_columnas (list): La lista de columnas de subáreas a renombrar.
    Returns:
        pd.DataFrame: El DataFrame con las columnas renombradas.
    """
    subareas_columnas = cfg.subareas_preventivos
    nuevo_nombre = {col: f'Subárea: {col}' for col in subareas_columnas if col in df.columns}

    df.rename(columns=nuevo_nombre, inplace=True)
    return df


def agregar_subarea(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agregar una nueva columna 'Subárea' que combine la información de las columnas que empiecen con 'Subárea: '.

    Args:
        df (pd.DataFrame): El DataFrame original.

    Returns:
        pd.DataFrame: El DataFrame con la nueva columna 'Subárea'.
    """
    subarea_cols = df.filter(regex=r'^Subárea: ').columns
    df.loc[:, 'Subárea'] = df[subarea_cols].apply(lambda row: ' - '.join(row.dropna().astype(str)), axis=1) if len(subarea_cols) > 0 else ''
    return df
