import pandas as pd
from typing import Tuple


def ordenar_columnas_correc(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Ordena las columnas del DataFrame según el orden especificado.

    Args:
        df (pd.DataFrame): El DataFrame original.

    Returns:
        A tuple of two pd.DataFrame: The DataFrame with the main columns ordered, and the DataFrame with all columns ordered.
    """
    columnas_cantidad_de_plagas = [col for col in df.columns if col.startswith('Cantidad de hallazgos de')]

    # Orden predefinido de columnas principales
    main_columns = ([
        #'Código',
        'Fecha',
        'Mes',
        'Sede',
        'Ubicación',
        'Nombre',
        'Solicitado por',
        'Técnicos',
        'Evidencia de plagas',
        'Descripción del trabajo realizado'])

    # Orden predefinido de columnas principales
    all_columns = ([
        'Fecha',
        'Fecha pandas',
        'Mes',
        'Orden de Mantenimiento',
        'Sede',
        'Ubicación',
        'Nombre',
        'Solicitado por',
        'Técnicos',
        'Evidencia de plagas']
        + columnas_cantidad_de_plagas
        + ['Descripción del trabajo realizado'])
    
    return df[main_columns], df[all_columns]
