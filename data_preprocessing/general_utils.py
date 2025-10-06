import pandas as pd
import config as cfg
import pandas as pd
from config import meses_esp



def agregar_ceros_a_columnas(df: pd.DataFrame, regex: str) -> pd.DataFrame:
    """
    Agregar ceros a las columnas que coincidan con el patrón regex especificado.

    Args:
        df (pd.DataFrame): El DataFrame original.
        regex (str): Patrón regex para filtrar columnas.

    Returns:
        pd.DataFrame: El DataFrame con las columnas actualizadas.
    """
    target_cols = df.filter(regex=regex).columns
    if len(target_cols) > 0:
        df.loc[:, target_cols] = df[target_cols].fillna(0).astype(int)
    return df


def crear_columna_combinada(df: pd.DataFrame, 
                          column_pattern: str,
                          new_column_name: str,
                          name_separator: str = '/',
                          join_separator: str = ', ',
                          empty_value: str = '') -> pd.DataFrame:
    """
    Crear una columna que combine información de múltiples columnas binarias o de cantidad.
    
    Args:
        df: DataFrame original
        column_pattern: Regex pattern para filtrar columnas (ej: r'^Técnicos/')
        new_column_name: Nombre de la nueva columna a crear
        name_separator: Separador para extraer nombres (ej: '/', 'hallazgos de ')
        join_separator: Separador para unir nombres (ej: ', ')
        empty_value: Valor cuando no hay coincidencias
        
    Returns:
        DataFrame con la nueva columna agregada
    """
    # Filtrar columnas que coinciden con el patrón
    filtered_cols = df.filter(regex=column_pattern).columns
    
    if len(filtered_cols) == 0:
        df.loc[:, new_column_name] = empty_value
        return df
    
    # Extraer nombres después del separador
    if name_separator == '/':
        names = filtered_cols.str.split('/', n=1).str[1]
    else:
        names = filtered_cols.str.split(name_separator, n=1).str[1]
    
    # Crear máscara usando gt(0) - funciona para binarias Y cantidades
    mask = df[filtered_cols].gt(0).to_numpy()
    
    # Crear la columna combinada
    df.loc[:, new_column_name] = pd.Series(
        (join_separator.join(names[row_mask]) if row_mask.any() else empty_value 
         for row_mask in mask),
        index=df.index
    )
    
    return df


def otros_a_dummy(df: pd.DataFrame, 
                  source_column: str,
                  prefix: str,
                  separator: str = '/',
                  drop_source: bool = True,
                  drop_columns: list = None) -> pd.DataFrame:
    """
    Convierte los valores de una columna en columnas binarias (dummy) con un prefijo específico.
    Utiliza pd.get_dummies() para mayor eficiencia.
    
    Args:
        df: DataFrame original
        source_column: Nombre de la columna fuente que contiene los valores únicos
        prefix: Prefijo para las nuevas columnas dummy (ej: 'Plaguicidas', 'Especies')
        separator: Separador entre prefijo y valor (por defecto '/')
        drop_source: Si True, elimina la columna fuente original
        drop_columns: Lista opcional de columnas específicas a eliminar
        
    Returns:  
        DataFrame con las nuevas columnas dummy agregadas
    """
    if source_column not in df.columns:
        return df
    
    # Usar get_dummies para crear columnas binarias de forma eficiente
    dummy_df = pd.get_dummies(df[source_column], 
                             prefix=prefix,
                             prefix_sep=separator,
                             dummy_na=False)  # No crear columna para NaN
    
    # Convertir a enteros (1/0) en lugar de booleanos (True/False)
    dummy_df = dummy_df.astype(int)
    
    # Agregar las columnas dummy al DataFrame original
    df = pd.concat([df, dummy_df], axis=1)
    
    # Eliminar columnas específicas si se proporcionan
    if drop_columns:
        df.drop(columns=drop_columns, inplace=True, errors='ignore')
    
    # Eliminar la columna fuente si se solicita
    if drop_source:
        df.drop(columns=[source_column], inplace=True, errors='ignore')
    
    return df



def agregar_cantidades_otras(df: pd.DataFrame,
                           source_column: str,
                           quantity_column: str,
                           prefix: str,
                           separator: str = ' ',
                           drop_source: bool = True,
                           drop_quantity: bool = True) -> pd.DataFrame:
    """
    Crear columnas de cantidad para cada valor único en una columna categórica.
    Versión genérica que puede trabajar con cualquier columna.
    
    Args:
        df: DataFrame original
        source_column: Columna que contiene los valores únicos a convertir
        quantity_column: Columna que contiene las cantidades correspondientes
        prefix: Prefijo para las nuevas columnas (ej: 'Cantidad de hallazgos de')
        separator: Separador entre prefijo y valor (por defecto ' ')
        drop_source: Si True, elimina la columna fuente original
        drop_quantity: Si True, elimina la columna de cantidades original
        
    Returns:
        DataFrame con las nuevas columnas de cantidad agregadas
    """
    if source_column not in df.columns or quantity_column not in df.columns:
        return df
    
    # Crear columnas binarias usando get_dummies
    dummies = pd.get_dummies(df[source_column], 
                            prefix=prefix,
                            prefix_sep=separator)
    
    # Obtener valores de cantidad con manejo robusto de datos no numéricos
    quantity_values = pd.to_numeric(df[quantity_column], errors='coerce').fillna(0).astype(int)
    
    # Multiplicación vectorizada: cada columna dummy * cantidad
    for col in dummies.columns:
        df.loc[:, col] = dummies[col] * quantity_values
    
    # Eliminar columnas originales si se solicita
    if drop_source:
        df.drop(columns=[source_column], inplace=True, errors='ignore')
    if drop_quantity:
        df.drop(columns=[quantity_column], inplace=True, errors='ignore')
    
    return df
