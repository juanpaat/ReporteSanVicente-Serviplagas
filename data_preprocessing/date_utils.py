import pandas as pd
from config import meses_esp

def agregar_nueva_fecha(df: pd.DataFrame, fecha_col: str = 'Fecha') -> pd.DataFrame:
    """
    Agregar una nueva columna 'Fecha pandas' que tenga el formato de fecha de pandas.
    Args:
        df (pd.DataFrame): El DataFrame original.
        fecha_col (str): El nombre de la columna que contiene las fechas en formato string.
    Returns:
        pd.DataFrame: El DataFrame con la nueva columna 'Fecha pandas'.
    """
    df.loc[:, 'Fecha pandas'] = pd.to_datetime(df[fecha_col], errors='coerce')
    
    # Convertir a datetime primero
    fecha_dt = pd.to_datetime(df['Fecha'])

    # Crear la columna 'Fecha' en el formato 'YYYY-MMM-DD' en español
    df.loc[:, 'Fecha'] = (fecha_dt.dt.year.astype(str) + '-' + 
                   fecha_dt.dt.strftime('%b').map(meses_esp) + '-' + 
                   fecha_dt.dt.day.astype(str).str.zfill(2))

    return df


def columna_mes(df: pd.DataFrame, fecha_col: str = 'Fecha pandas') -> pd.DataFrame:
    """
    Agregar una nueva columna 'Mes' que tenga el formato 'MMM YYYY' en español (ejemplo: 'Ene 2025').
    Args:
        df (pd.DataFrame): El DataFrame original.
        fecha_col (str): El nombre de la columna que contiene las fechas en formato datetime.
    Returns:
        pd.DataFrame: El DataFrame con la nueva columna 'Mes'.
    """

    # Crear columna con formato en inglés primero
    df.loc[:, 'Mes'] = df[fecha_col].dt.strftime('%b')
    # Reemplazar abreviaciones en inglés por español
    df.loc[:, 'Mes'] = df['Mes'].map(meses_esp)
    # agregar año al mes
    df.loc[:, 'Mes'] = df['Mes'] + ' ' + df[fecha_col].dt.year.astype(str)
    return df
