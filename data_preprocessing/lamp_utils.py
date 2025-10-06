import pandas as pd
import config as cfg


def agregar_columna_lampara(df: pd.DataFrame) -> pd.DataFrame:
    """
    Combina las columnas de lámpara manejando valores NaN correctamente.
    """
    # Fill NaN with empty strings before concatenation
    rionegro = df['Lámpara Rionegro'].fillna('').astype(str)
    medellin = df['Lámparas Medellín'].fillna('').astype(str)
    
    # Concatenate with space separator
    df.loc[:, 'Lámpara'] = (rionegro + ' ' + medellin).str.strip()
    
    # Drop original columns
    df.drop(columns=['Lámpara Rionegro', 'Lámparas Medellín'], inplace=True)
    
    return df



def ordenar_columnas_lamparas(df: pd.DataFrame, orden: list = None) -> pd.DataFrame:
    """
    Ordena las columnas del DataFrame según el orden especificado.

    Args:
        df (pd.DataFrame): El DataFrame original.
        orden (list, optional): Lista con el orden deseado de las columnas. 
                               Si es None, usa el orden predefinido.

    Returns:
        pd.DataFrame: El DataFrame con las columnas ordenadas.
    """
    columnas_estado_de_lamparas = [col for col in df.columns if col.startswith('Estado de la lámpara/')]
    columnas_cantidad_de_animales = [col for col in df.columns if col.startswith('Cantidad de ')]   

    # Orden predefinido de columnas principales
    main_columns = ([
        'ID',
        'Fecha',
        'Mes',
        'Sede',
        'Técnicos',
        'Lámpara',
        'Estado de la lámpara',
        'Estado del tubo',
        'Especies encontradas']
        +columnas_cantidad_de_animales+
        ['Observaciones'])

    # Orden predefinido de columnas principales
    all_columns = ([
        'ID',
        'Fecha',
        'Fecha pandas',
        'Mes',
        'Sede',
        'Técnicos',
        'Lámpara',
        'Estado de la lámpara']
        + columnas_estado_de_lamparas +
        ['Estado del tubo',
        'Especies encontradas']
        + columnas_cantidad_de_animales +
        ['Observaciones'])
    
    return df[main_columns], df[all_columns]
