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
        'ID',
        'Orden de Mantenimiento',
        'Fecha',
        'Mes',
        'Sede',
        'Ubicación',
        'Descripción del aviso',
        'Nombre',
        'Solicitado por',
        'Técnicos',
        'Evidencia de plagas']
        + columnas_cantidad_de_plagas +
        ['Fecha de entrega',
        'Hora de entrega',
        'Duración',
        'Descripción del trabajo realizado',
        'Recomendaciones'])
    
    # Orden predefinido de columnas principales
    all_columns = ([
        'ID',
        'Orden de Mantenimiento',
        'Fecha',
        'Mes',
        'Sede',
        'Ubicación',
        'Descripción del aviso',
        'Nombre',
        'Solicitado por',
        'Técnicos',
        'Evidencia de plagas']
        + columnas_cantidad_de_plagas +
        ['Fecha de entrega',
        'Hora de entrega',
        'Duración',
        'Descripción del trabajo realizado',
        'Recomendaciones'])
    
    return df[main_columns], df[all_columns]
